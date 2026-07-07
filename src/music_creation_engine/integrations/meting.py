from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass

from music_creation_engine.integrations.base import IntegrationResult


@dataclass
class MetingIntegration:
    enabled: bool = True
    command: str = "npx"

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
                        return json.loads(text)
                    except json.JSONDecodeError:
                        return {"raw": text}
            return result_message.get("result")
        finally:
            proc.kill()

    def search(self, keyword: str, platform: str = "netease") -> IntegrationResult:
        if self.enabled:
            try:
                result = subprocess.run(
                    [self.command, "@eldment/meting-agent", "search", "--platform", platform, "--keyword", keyword],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        payload = json.loads(result.stdout)
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
        return IntegrationResult(
            payload={
                "keyword": keyword,
                "platform": platform,
                "enabled": self.enabled,
                "note": "Meting integration wiring is available; runtime command execution is optional.",
            },
            source="meting",
        )
