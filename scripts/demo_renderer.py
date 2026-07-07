#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from music_creation_engine.models import RenderRequest
from music_creation_engine.services.render_service import RenderService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render demo audio from a MIDI file.")
    parser.add_argument("--midi", required=True)
    parser.add_argument("--soundfont")
    parser.add_argument("--output", required=True)
    parser.add_argument("--format", default="mp3")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    request = RenderRequest(
        midi_path=args.midi,
        output_base=args.output,
        format=args.format,
        soundfont_path=args.soundfont,
    )
    result = RenderService().render(request)
    payload = json.dumps(result, ensure_ascii=False)
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
