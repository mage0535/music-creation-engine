from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from music_creation_engine import __version__ as PACKAGE_VERSION
from music_creation_engine.integrations.base import IntegrationResult

logger = logging.getLogger(__name__)


@dataclass
class MetingIntegration:
    enabled: bool = True
    command: str = "npx"

    def _guess_package_root(self) -> Path | None:
        cmd_path = self.command
        command_base = os.path.basename(cmd_path).lower()
        if os.path.exists(cmd_path) and not any(token in command_base for token in ("npx", "npm")):
            resolved = Path(cmd_path).resolve()
            for parent in resolved.parents:
                if (parent / "package.json").exists():
                    return parent
        for base in (
            Path("/root/.hermes/node/lib/node_modules/@eldment/meting-agent"),
            Path("/usr/lib/node_modules/@eldment/meting-agent"),
        ):
            if base.exists():
                return base
        try:
            result = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=5, check=False)
            root = Path(result.stdout.strip()) / "@eldment" / "meting-agent"
            if root.exists():
                return root
        except Exception:
            pass
        return None

    def _guess_node_command(self) -> str:
        if os.path.exists(self.command):
            sibling = Path(self.command).resolve().parent / "node"
            if sibling.exists():
                return str(sibling)
        return "node"

    def _build_server_command(self) -> list[str]:
        base = os.path.basename(self.command)
        if "npx" in base:
            return [self.command, "-y", "@eldment/meting-agent"]
        return [self.command]

    def _build_cli_command(self, keyword: str, platform: str) -> list[str]:
        base = os.path.basename(self.command)
        if "npx" in base:
            return [self.command, "-y", "@eldment/meting-agent", "search", "--platform", platform, "--keyword", keyword]
        return [self.command, "@eldment/meting-agent", "search", "--platform", platform, "--keyword", keyword]

    def _write_mcp_message(self, proc: subprocess.Popen, message: dict[str, object]) -> None:
        body = json.dumps(message)
        payload = f"Content-Length: {len(body.encode())}\r\n\r\n{body}"
        assert proc.stdin is not None
        proc.stdin.write(payload)
        proc.stdin.flush()

    def _read_mcp_message(self, proc: subprocess.Popen, timeout: float = 5.0) -> dict[str, object] | None:
        assert proc.stdout is not None
        try:
            os.set_blocking(proc.stdout.fileno(), False)
        except Exception:
            pass
        header = ""
        deadline = time.monotonic() + timeout
        while "\r\n\r\n" not in header and time.monotonic() < deadline:
            char = proc.stdout.read(1)
            if not char:
                time.sleep(0.05)
                continue
            header += char
        if "\r\n\r\n" not in header:
            return None
        head, body_prefix = header.split("\r\n\r\n", 1)
        length = 0
        for line in head.split("\r\n"):
            if line.lower().startswith("content-length:"):
                length = int(line.split(":", 1)[1].strip())
                break
        if length <= 0:
            return None
        body = body_prefix
        while len(body.encode()) < length and time.monotonic() < deadline:
            char = proc.stdout.read(1)
            if not char:
                time.sleep(0.05)
                continue
            body += char
        if len(body.encode()) < length:
            return None
        try:
            return json.loads(body[:length])
        except json.JSONDecodeError:
            return None

    def _coerce_int(self, value: object) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _as_list(self, value: object) -> list[object]:
        if isinstance(value, list):
            return value
        if value is None:
            return []
        return [value]

    def _first_non_empty(self, *values: object) -> object | None:
        for value in values:
            if value is None:
                continue
            if isinstance(value, str) and not value.strip():
                continue
            if isinstance(value, (list, dict)) and not value:
                continue
            return value
        return None

    def _clean_text(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _extract_json_from_text(self, text: str) -> object | None:
        candidate = text.strip()
        if not candidate:
            return None
        if candidate.startswith("```"):
            lines = [line for line in candidate.splitlines() if not line.strip().startswith("```")]
            candidate = "\n".join(lines).strip()
        for start_char, end_char in (("{", "}"), ("[", "]")):
            start = candidate.find(start_char)
            end = candidate.rfind(end_char)
            if start != -1 and end != -1 and end >= start:
                fragment = candidate[start : end + 1]
                try:
                    return json.loads(fragment)
                except json.JSONDecodeError:
                    continue
        return None

    def _extract_song_candidates(self, payload: object) -> list[dict[str, object]]:
        if isinstance(payload, str):
            try:
                parsed = json.loads(payload)
            except json.JSONDecodeError:
                parsed = None
            if parsed is not None:
                return self._extract_song_candidates(parsed)
            parsed = self._extract_json_from_text(payload)
            if parsed is not None:
                return self._extract_song_candidates(parsed)
            return []
        if isinstance(payload, list):
            results: list[dict[str, object]] = []
            for item in payload:
                if isinstance(item, dict):
                    if any(key in item for key in ("name", "songname", "title", "trackName")):
                        results.append(item)
                    else:
                        results.extend(self._extract_song_candidates(item))
            return results
        if not isinstance(payload, dict):
            return []

        direct_lists = (
            payload.get("songs"),
            payload.get("list"),
            payload.get("data"),
            payload.get("result"),
        )
        for candidate in direct_lists:
            if isinstance(candidate, list):
                return [item for item in candidate if isinstance(item, dict)]

        nested_dicts = [
            payload,
            payload.get("result"),
            payload.get("data"),
            payload.get("body"),
            payload.get("payload"),
        ]
        for candidate in nested_dicts:
            if not isinstance(candidate, dict):
                continue
            for key in ("songs", "songList", "song_list", "list", "items"):
                value = candidate.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
            for key in ("data", "result"):
                value = candidate.get(key)
                if isinstance(value, dict):
                    nested = self._extract_song_candidates(value)
                    if nested:
                        return nested
        return []

    def _normalize_artist_names(self, item: dict[str, object]) -> str | None:
        artist_lists = [
            item.get("ar"),
            item.get("artists"),
            item.get("singer"),
            item.get("author_simple"),
        ]
        names: list[str] = []
        for artists in artist_lists:
            for artist in self._as_list(artists):
                if isinstance(artist, dict):
                    name = self._clean_text(
                        self._first_non_empty(
                            artist.get("name"),
                            artist.get("artistName"),
                            artist.get("title"),
                        )
                    )
                    if name:
                        names.append(name)
                else:
                    name = self._clean_text(artist)
                    if name:
                        names.append(name)
        if names:
            return ", ".join(dict.fromkeys(names))
        return self._clean_text(
            self._first_non_empty(
                item.get("artist"),
                item.get("artistName"),
                item.get("singername"),
                item.get("author_name"),
            )
        )

    def _normalize_song_item(self, item: dict[str, object], platform: str) -> dict[str, object] | None:
        title = self._clean_text(
            self._first_non_empty(
                item.get("name"),
                item.get("songname"),
                item.get("title"),
                item.get("trackName"),
            )
        )
        artist = self._normalize_artist_names(item)
        album_source = self._first_non_empty(item.get("al"), item.get("album"), item.get("albuminfo"))
        album = None
        album_id = None
        artwork_url = None
        if isinstance(album_source, dict):
            album = self._clean_text(
                self._first_non_empty(
                    album_source.get("name"),
                    album_source.get("title"),
                    album_source.get("albumName"),
                )
            )
            album_id = self._coerce_int(self._first_non_empty(album_source.get("id"), album_source.get("albumid")))
            artwork_url = self._clean_text(
                self._first_non_empty(
                    album_source.get("picUrl"),
                    album_source.get("cover"),
                    album_source.get("pic"),
                )
            )
        else:
            album = self._clean_text(
                self._first_non_empty(
                    album_source,
                    item.get("albumname"),
                    item.get("collectionName"),
                )
            )
            album_id = self._coerce_int(item.get("album_id"))

        artwork_url = self._clean_text(
            self._first_non_empty(
                artwork_url,
                item.get("pic"),
                item.get("picUrl"),
                item.get("artworkUrl100"),
                item.get("albumPic"),
            )
        )
        duration_ms = self._coerce_int(
            self._first_non_empty(
                item.get("dt"),
                item.get("duration"),
                item.get("interval"),
                item.get("songTimeMinutes"),
                item.get("trackTimeMillis"),
            )
        )
        if duration_ms is not None and 0 < duration_ms < 1000:
            duration_ms *= 1000

        song_id = self._clean_text(
            self._first_non_empty(
                item.get("id"),
                item.get("songid"),
                item.get("songmid"),
                item.get("mid"),
                item.get("rid"),
                item.get("hash"),
                item.get("trackId"),
            )
        )
        artist_id = self._clean_text(self._first_non_empty(item.get("artistId"), item.get("artistid")))
        preview_url = self._clean_text(
            self._first_non_empty(
                item.get("url"),
                item.get("previewUrl"),
                item.get("playUrl"),
                item.get("listen_url"),
            )
        )

        if not title and not song_id:
            return None

        return {
            "title": title,
            "artist": artist,
            "album": album,
            "preview_url": preview_url,
            "artwork_url": artwork_url,
            "provider": platform,
            "song_id": song_id,
            "album_id": album_id,
            "artist_id": artist_id,
            "duration_ms": duration_ms,
        }

    def _dedupe_songs(self, songs: list[dict[str, object]]) -> list[dict[str, object]]:
        deduped: list[dict[str, object]] = []
        seen: set[tuple[str | None, str | None, str | None]] = set()
        for song in songs:
            key = (
                self._clean_text(song.get("song_id")),
                self._clean_text(song.get("title")),
                self._clean_text(song.get("artist")),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(song)
        return deduped

    def _normalize_meting_payload(self, payload: object, platform: str) -> dict[str, object] | None:
        candidates = self._extract_song_candidates(payload)
        songs = [
            normalized
            for item in candidates
            if isinstance(item, dict)
            for normalized in [self._normalize_song_item(item, platform)]
            if normalized is not None
        ]
        if not songs:
            if isinstance(payload, str):
                return {"provider": platform, "songs": [], "raw": payload}
            if isinstance(payload, dict):
                return {"provider": platform, "songs": [], "raw": payload}
            return None
        deduped = self._dedupe_songs(songs)
        return {
            "provider": platform,
            "platform": platform,
            "song_count": len(deduped),
            "songs": deduped,
            "raw": payload,
        }

    def _normalize_http_fallback_payload(self, keyword: str, payload: dict[str, object]) -> dict[str, object] | None:
        songs: list[dict[str, object]] = []
        for item in payload.get("results", []):
            if not isinstance(item, dict):
                continue
            songs.append(
                {
                    "title": self._clean_text(item.get("trackName")),
                    "artist": self._clean_text(item.get("artistName")),
                    "album": self._clean_text(item.get("collectionName")),
                    "preview_url": self._clean_text(item.get("previewUrl")),
                    "artwork_url": self._clean_text(item.get("artworkUrl100")),
                    "provider": "itunes",
                    "song_id": self._clean_text(self._first_non_empty(item.get("trackId"), item.get("collectionId"))),
                    "album_id": self._coerce_int(item.get("collectionId")),
                    "artist_id": self._clean_text(item.get("artistId")),
                    "duration_ms": self._coerce_int(item.get("trackTimeMillis")),
                }
            )
        songs = self._dedupe_songs(songs)
        if songs:
            return {
                "provider": "itunes",
                "platform": "itunes",
                "query": keyword,
                "song_count": len(songs),
                "songs": songs,
                "raw": payload,
            }
        return None

    def _search_via_http_fallback(self, keyword: str) -> dict[str, object] | None:
        query = urlencode({"term": keyword, "entity": "song", "limit": 5})
        with urlopen(f"https://itunes.apple.com/search?{query}", timeout=10) as response:
            payload = json.loads(response.read().decode())
        return self._normalize_http_fallback_payload(keyword, payload)

    def _mcp_call_tool(
        self,
        proc: subprocess.Popen,
        request_id: int,
        tool_name: str,
        arguments: dict[str, object],
        timeout: float,
    ) -> dict[str, object] | None:
        self._write_mcp_message(
            proc,
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            },
        )
        return self._read_mcp_message(proc, timeout) or {}

    def _extract_tool_text_payload(self, result_message: dict[str, object]) -> object | None:
        result = result_message.get("result", {})
        if not isinstance(result, dict):
            return None
        content = result.get("content", [])
        if isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "text" and isinstance(item.get("text"), str):
                    parsed = self._extract_json_from_text(item["text"])
                    return parsed if parsed is not None else item["text"]
                if item.get("type") == "json":
                    return item.get("json")
        structured = result.get("structuredContent")
        if structured is not None:
            return structured
        return result

    def _enrich_with_mcp_tools(
        self,
        proc: subprocess.Popen,
        tools: dict[str, str],
        normalized: dict[str, object],
        deadline: float,
    ) -> dict[str, object]:
        if not normalized.get("songs"):
            return normalized

        url_tool = tools.get("url")
        pic_tool = tools.get("pic")
        if not url_tool and not pic_tool:
            return normalized

        enriched: list[dict[str, object]] = []
        request_id = 100
        for song in normalized.get("songs", []):
            if not isinstance(song, dict):
                continue
            current = dict(song)
            song_id = current.get("song_id")
            if not song_id:
                enriched.append(current)
                continue
            remaining = max(0.1, deadline - time.monotonic())
            if url_tool and not current.get("preview_url") and remaining > 0:
                for args in (
                    {"platform": normalized.get("platform"), "id": song_id},
                    {"platform": normalized.get("platform"), "song_id": song_id},
                ):
                    message = self._mcp_call_tool(proc, request_id, url_tool, args, min(2.0, remaining))
                    request_id += 1
                    payload = self._extract_tool_text_payload(message or {})
                    if isinstance(payload, dict):
                        current["preview_url"] = self._clean_text(
                            self._first_non_empty(
                                payload.get("url"),
                                payload.get("data"),
                                payload.get("playUrl"),
                            )
                        )
                    elif isinstance(payload, str):
                        current["preview_url"] = self._clean_text(payload)
                    if current.get("preview_url"):
                        break
            remaining = max(0.1, deadline - time.monotonic())
            if pic_tool and not current.get("artwork_url") and remaining > 0:
                for args in (
                    {"platform": normalized.get("platform"), "id": song_id},
                    {"platform": normalized.get("platform"), "song_id": song_id},
                ):
                    message = self._mcp_call_tool(proc, request_id, pic_tool, args, min(2.0, remaining))
                    request_id += 1
                    payload = self._extract_tool_text_payload(message or {})
                    if isinstance(payload, dict):
                        current["artwork_url"] = self._clean_text(
                            self._first_non_empty(
                                payload.get("url"),
                                payload.get("pic"),
                                payload.get("data"),
                            )
                        )
                    elif isinstance(payload, str):
                        current["artwork_url"] = self._clean_text(payload)
                    if current.get("artwork_url"):
                        break
            enriched.append(current)

        normalized["songs"] = enriched
        normalized["song_count"] = len(enriched)
        return normalized

    def _search_via_mcp(self, keyword: str, platform: str) -> dict[str, object] | None:
        missing_proc_timeout = 15
        proc = subprocess.Popen(
            self._build_server_command(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            deadline = time.monotonic() + missing_proc_timeout

            def remaining() -> float:
                return max(0.1, deadline - time.monotonic())

            self._write_mcp_message(
                proc,
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "clientInfo": {"name": "music-creation-engine", "version": PACKAGE_VERSION},
                    },
                },
            )
            init_response = self._read_mcp_message(proc, min(5.0, remaining()))
            if init_response is None:
                return None
            self._write_mcp_message(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
            self._write_mcp_message(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
            tools_message = self._read_mcp_message(proc, min(5.0, remaining())) or {}
            tools_raw = tools_message.get("result", {}).get("tools", [])
            tools: dict[str, str] = {}
            search_tool = None
            for tool in tools_raw:
                if not isinstance(tool, dict):
                    continue
                name = str(tool.get("name", ""))
                lowered = name.lower()
                tools[lowered] = name
                if search_tool is None and "search" in lowered:
                    search_tool = name
            if not search_tool:
                return None

            attempt_arguments = [
                {"platform": platform, "query": keyword, "limit": 5},
                {"platform": platform, "keyword": keyword, "limit": 5},
                {"platform": platform, "keywords": keyword, "limit": 5},
            ]
            for index, arguments in enumerate(attempt_arguments, start=3):
                result_message = self._mcp_call_tool(proc, index, search_tool, arguments, min(5.0, remaining())) or {}
                payload = self._extract_tool_text_payload(result_message)
                normalized = self._normalize_meting_payload(payload, platform) if payload is not None else None
                if normalized and normalized.get("songs"):
                    return self._enrich_with_mcp_tools(proc, tools, normalized, deadline)
            return None
        except (BrokenPipeError, OSError) as exc:
            logger.warning("MCP search failed (pipe): %s", exc)
            return None
        except TimeoutError:
            logger.warning("MCP search timed out after %ds", missing_proc_timeout)
            return None
        finally:
            try:
                import signal

                pgid = os.getpgid(proc.pid)
                os.killpg(pgid, signal.SIGTERM)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    def _search_via_node_module(self, keyword: str, platform: str) -> dict[str, object] | None:
        package_root = self._guess_package_root()
        if package_root is None:
            return None
        meting_module = (package_root / "src" / "meting" / "meting.js").as_posix()
        search_calls = [
            f"client.search({{ query: {json.dumps(keyword)}, limit: 5 }})",
            f"client.search({{ keyword: {json.dumps(keyword)}, limit: 5 }})",
            f"client.search({json.dumps(keyword)}, {{ limit: 5 }})",
        ]
        for call in search_calls:
            script = (
                f"import Meting from '{meting_module}';"
                f"const client = new Meting({json.dumps(platform)});"
                f"const result = await {call};"
                "console.log(JSON.stringify(result));"
            )
            result = subprocess.run(
                [self._guess_node_command(), "--input-type=module", "-e", script],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            if result.returncode != 0 or not result.stdout.strip():
                continue
            normalized = self._normalize_meting_payload(result.stdout.strip(), platform)
            if normalized and normalized.get("songs"):
                return normalized
        return None

    def search(self, keyword: str, platform: str = "netease") -> IntegrationResult:
        if self.enabled:
            try:
                payload = self._search_via_node_module(keyword, platform)
                if payload and payload.get("songs"):
                    payload["query"] = keyword
                    return IntegrationResult(payload=payload, source="meting")
            except Exception:
                pass
            try:
                result = subprocess.run(
                    self._build_cli_command(keyword, platform),
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    payload = self._normalize_meting_payload(result.stdout, platform)
                    if payload and payload.get("songs"):
                        payload["query"] = keyword
                        return IntegrationResult(payload=payload, source="meting")
            except (FileNotFoundError, subprocess.SubprocessError, BrokenPipeError, OSError):
                pass
            try:
                payload = self._search_via_mcp(keyword, platform)
                if payload and payload.get("songs"):
                    payload["query"] = keyword
                    return IntegrationResult(payload=payload, source="meting")
            except (FileNotFoundError, subprocess.SubprocessError, BrokenPipeError, OSError):
                pass
            try:
                payload = self._search_via_http_fallback(keyword)
                if payload:
                    return IntegrationResult(payload=payload, source="reference-fallback")
            except Exception:
                pass
        return IntegrationResult(
            payload={
                "keyword": keyword,
                "platform": platform,
                "enabled": self.enabled,
                "songs": [],
                "song_count": 0,
                "note": "Meting integration wiring is available; runtime command execution is optional.",
            },
            source="meting",
        )
