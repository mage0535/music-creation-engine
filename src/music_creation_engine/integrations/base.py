from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class IntegrationResult:
    payload: dict[str, Any]
    source: str
