from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from dataclasses import dataclass

from music_creation_engine.integrations.base import IntegrationResult


@dataclass
class MetingIntegration:
    enabled: bool = True
    command: str = "npx"

    def _guess_package_root(self) -> Path | None:
        cmd_path = self.command
        if os.path.exists(cmd_path):
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

    def _search_via_mcp(self, keyword: str, platform: str) -> dict[str, object] | None:
        proc = subprocess.Popen(
            self._build_server_command(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            self._write_mcp_message(
                proc,
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "clientInfo": {"name": "music-creation-engine", "version": "0.4.0"},
                    },
                },
            )
            self._read_mcp_message(proc)
            self._write_mcp_message(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
            self._write_mcp_message(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
            tools_message = self._read_mcp_message(proc) or {}
            tools = tools_message.get("result", {}).get("tools", [])
            tool_name = None
            for tool in tools:
                name = tool.get("name", "")
                if "search" in name.lower():
                    tool_name = name
                    break
            if not tool_name:
                return None
            self._write_mcp_message(
                proc,
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": {"platform": platform, "keyword": keyword}},
                },
            )
            result_message = self._read_mcp_message(proc) or {}
            content = result_message.get("result", {}).get("content", [])
            for item in content:
                if item.get("type") == "text":
                    text = item.get("text", "")
                    try:
                        parsed = json.loads(text)
                        return self._normalize_meting_payload(parsed, platform) or parsed
                    except json.JSONDecodeError:
                        return {"raw": text}
            return result_message.get("result")
        finally:
            proc.kill()

    def _search_via_http_fallback(self, keyword: str) -> dict[str, object] | None:
        query = urlencode({"term": keyword, "entity": "song", "limit": 5})
        with urlopen(f"https://itunes.apple.com/search?{query}", timeout=10) as response:
            payload = json.loads(response.read().decode())
        songs = []
        for item in payload.get("results", []):
            songs.append(
                {
                    "title": item.get("trackName"),
                    "artist": item.get("artistName"),
                    "album": item.get("collectionName"),
                    "preview_url": item.get("previewUrl"),
                    "provider": "itunes",
                }
            )
        if songs:
            return {"provider": "itunes", "songs": songs}
        return None

    def _normalize_meting_payload(self, payload: object, platform: str) -> dict[str, object] | None:
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                return {"provider": platform, "raw": payload, "songs": []}
        if not isinstance(payload, dict):
            return None
        result = payload.get("result", payload)
        songs_raw = result.get("songs", []) if isinstance(result, dict) else []
        songs = []
        for item in songs_raw:
            if not isinstance(item, dict):
                continue
            artists = item.get("ar", [])
            artist_names = ", ".join(a.get("name") for a in artists if isinstance(a, dict) and a.get("name"))
            album = item.get("al", {}).get("name") if isinstance(item.get("al"), dict) else None
            songs.append(
                {
                    "title": item.get("name"),
                    "artist": artist_names,
                    "album": album,
                    "preview_url": None,
                    "provider": platform,
                    "song_id": item.get("id"),
                }
            )
        return {"provider": platform, "songs": songs, "raw": payload}

    def _search_via_node_module(self, keyword: str, platform: str) -> dict[str, object] | None:
        package_root = self._guess_package_root()
        if package_root is None:
            return None
        meting_module = (package_root / "src" / "meting" / "meting.js").as_posix()
        script = (
            f"import Meting from '{meting_module}';"
            f"const client = new Meting({json.dumps(platform)});"
            f"const result = await client.search({json.dumps(keyword)}, {{ limit: 5 }});"
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
            return None
        return self._normalize_meting_payload(result.stdout.strip(), platform)

    def search(self, keyword: str, platform: str = "netease") -> IntegrationResult:
        if self.enabled:
            try:
                payload = self._search_via_node_module(keyword, platform)
                if payload:
                    return IntegrationResult(payload=payload, source="meting")
            except Exception:
                pass
            try:
                result = subprocess.run(
                    [self.command, "@eldment/meting-agent", "search", "--platform", platform, "--keyword", keyword],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        payload = self._normalize_meting_payload(result.stdout, platform) or json.loads(result.stdout)
                        return IntegrationResult(payload=payload, source="meting")
                    except json.JSONDecodeError:
                        pass
            except (FileNotFoundError, subprocess.SubprocessError):
                pass
            try:
                payload = self._search_via_mcp(keyword, platform)
                if payload:
                    return IntegrationResult(payload=payload, source="meting")
            except (FileNotFoundError, subprocess.SubprocessError):
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
                "note": "Meting integration wiring is available; runtime command execution is optional.",
            },
            source="meting",
        )
