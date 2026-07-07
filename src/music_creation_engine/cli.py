from __future__ import annotations

import argparse
import json
from pathlib import Path

from music_creation_engine.adapters.install import install_adapter_files
from music_creation_engine.capabilities import detect_capabilities
from music_creation_engine.config import load_settings
from music_creation_engine.models import ReferenceSearchRequest, RenderRequest, ScoreRequest, WorkflowRequest
from music_creation_engine.services.reference_service import ReferenceService
from music_creation_engine.services.render_service import RenderService
from music_creation_engine.services.score_service import ScoreService
from music_creation_engine.services.workflow_service import WorkflowService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="music-creation-engine")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("health")
    subparsers.add_parser("capabilities")
    score = subparsers.add_parser("score")
    score.add_argument("--lyrics", default="")
    score.add_argument("--output", required=True)
    score.add_argument("--key", default="C")
    score.add_argument("--bpm", type=int, default=120)
    score.add_argument("--time-signature", default="4/4")
    score.add_argument("--instruments", default="piano,vocals")
    score.add_argument("--style", default="pop")
    score.add_argument("--mode", default="all")
    render = subparsers.add_parser("render")
    render.add_argument("--midi", required=True)
    render.add_argument("--output", required=True)
    render.add_argument("--format", default="mp3")
    render.add_argument("--soundfont")
    workflow = subparsers.add_parser("workflow")
    workflow_subparsers = workflow.add_subparsers(dest="workflow_command")
    workflow_full = workflow_subparsers.add_parser("full")
    workflow_full.add_argument("--lyrics", default="")
    workflow_full.add_argument("--output", required=True)
    workflow_full.add_argument("--key", default="C")
    workflow_full.add_argument("--bpm", type=int, default=120)
    workflow_full.add_argument("--instruments", default="piano,vocals")
    workflow_full.add_argument("--style", default="pop")
    references = subparsers.add_parser("references")
    references_subparsers = references.add_subparsers(dest="references_command")
    references_search = references_subparsers.add_parser("search")
    references_search.add_argument("--keyword", required=True)
    references_search.add_argument("--platform", default="netease")
    adapters = subparsers.add_parser("adapters")
    adapters_subparsers = adapters.add_subparsers(dest="adapters_command")
    adapters_subparsers.add_parser("install")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "health":
        print(json.dumps({"status": "ok"}))
        return 0

    if args.command == "capabilities":
        settings = load_settings()
        print(json.dumps(detect_capabilities(settings).to_dict()))
        return 0

    if args.command == "references" and args.references_command == "search":
        service = ReferenceService()
        result = service.search(
            ReferenceSearchRequest(keyword=args.keyword, platform=args.platform)
        )
        print(json.dumps(result))
        return 0

    if args.command == "score":
        service = ScoreService()
        result = service.generate(
            ScoreRequest(
                lyrics=args.lyrics,
                output_base=args.output,
                key=args.key,
                bpm=args.bpm,
                time_signature=args.time_signature,
                instruments=args.instruments,
                style=args.style,
                mode=args.mode,
            )
        )
        print(json.dumps(result))
        return 0

    if args.command == "render":
        service = RenderService()
        result = service.render(
            RenderRequest(
                midi_path=args.midi,
                output_base=args.output,
                format=args.format,
                soundfont_path=args.soundfont,
            )
        )
        print(json.dumps(result))
        return 0

    if args.command == "workflow" and args.workflow_command == "full":
        workflow_service = WorkflowService(
            score_service=ScoreService(),
            render_service=RenderService(),
        )
        result = workflow_service.run_full(
            WorkflowRequest(
                lyrics=args.lyrics,
                output_base=args.output,
                key=args.key,
                bpm=args.bpm,
                instruments=args.instruments,
                style=args.style,
            )
        )
        print(json.dumps(result))
        return 0

    if args.command == "adapters" and args.adapters_command == "install":
        installed = install_adapter_files(Path.cwd())
        print(json.dumps(installed))
        return 0

    parser.print_help()
    return 1


def run() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    run()
