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

from music_creation_engine.models import ScoreRequest
from music_creation_engine.services.score_service import ScoreService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate sheet music artifacts from lyrics.")
    parser.add_argument("--lyrics", default="", help="Lyrics text")
    parser.add_argument("--lyrics-file", help="Optional lyrics file path")
    parser.add_argument("--key", default="C")
    parser.add_argument("--bpm", type=int, default=120)
    parser.add_argument("--time-signature", default="4/4")
    parser.add_argument("--instruments", default="piano,vocals")
    parser.add_argument("--style", default="pop")
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", default="all")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_lyrics(args: argparse.Namespace) -> str:
    if args.lyrics_file:
        with open(args.lyrics_file, "r", encoding="utf-8") as handle:
            return handle.read()
    return args.lyrics


def main() -> int:
    args = parse_args()
    request = ScoreRequest(
        lyrics=load_lyrics(args),
        output_base=args.output,
        key=args.key,
        bpm=args.bpm,
        time_signature=args.time_signature,
        instruments=args.instruments,
        style=args.style,
        mode=args.mode,
    )
    result = ScoreService().generate(request)
    payload = json.dumps(result, ensure_ascii=False)
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
