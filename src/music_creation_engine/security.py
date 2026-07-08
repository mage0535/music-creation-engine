from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock

from fastapi import Request

from music_creation_engine.models import ErrorCode, SecuritySettings


@dataclass
class RequestDecision:
    allowed: bool
    status_code: int = 200
    payload: dict[str, object] | None = None
    retry_after_seconds: int | None = None


class SlidingWindowRateLimiter:
    def __init__(self, limit_per_minute: int) -> None:
        self.limit_per_minute = limit_per_minute
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, subject: str) -> tuple[bool, int | None]:
        if self.limit_per_minute <= 0:
            return True, None
        now = time.monotonic()
        cutoff = now - 60
        with self._lock:
            events = self._events[subject]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= self.limit_per_minute:
                retry_after = max(1, int(60 - (now - events[0])))
                return False, retry_after
            events.append(now)
        return True, None


class RequestGate:
    def __init__(self, settings: SecuritySettings) -> None:
        self.settings = settings
        self.rate_limiter = SlidingWindowRateLimiter(settings.rate_limit_per_minute)

    def _extract_api_key(self, request: Request) -> str | None:
        header_value = request.headers.get(self.settings.auth_header_name)
        if header_value:
            return header_value.strip()
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            return auth_header.split(" ", 1)[1].strip()
        return None

    def _build_error(self, status_code: int, code: ErrorCode, message: str, detail: str = "") -> RequestDecision:
        return RequestDecision(
            allowed=False,
            status_code=status_code,
            payload={"error": {"code": code.value, "message": message, "detail": detail}},
        )

    def validate(self, request: Request) -> RequestDecision:
        path = request.url.path
        if not path.startswith("/v1/"):
            return RequestDecision(allowed=True)

        api_key = self._extract_api_key(request)
        configured_keys = set(self.settings.api_keys)
        if configured_keys:
            if not api_key:
                return self._build_error(
                    401,
                    ErrorCode.UNAUTHORIZED,
                    "Missing API key",
                    f"Provide {self.settings.auth_header_name} or Authorization: Bearer <key>.",
                )
            if api_key not in configured_keys:
                return self._build_error(401, ErrorCode.UNAUTHORIZED, "Invalid API key")
            subject = f"key:{api_key}"
        else:
            client_host = request.client.host if request.client else "anonymous"
            subject = f"ip:{client_host}"

        allowed, retry_after = self.rate_limiter.allow(subject)
        if not allowed:
            decision = self._build_error(
                429,
                ErrorCode.RATE_LIMITED,
                "Rate limit exceeded",
                f"Allowed {self.settings.rate_limit_per_minute} requests per minute.",
            )
            decision.retry_after_seconds = retry_after
            return decision

        return RequestDecision(allowed=True)
