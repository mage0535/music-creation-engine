from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from music_creation_engine.adapters.install import install_adapter_files
from music_creation_engine.capabilities import detect_capabilities
from music_creation_engine.config import load_settings
from music_creation_engine.models import (
    ErrorCode,
    EngineError,
    MidiDiffRequest,
    MidiInspectRequest,
    MidiQueryRequest,
    PlayabilityRequest,
    ReferenceSearchRequest,
    RenderRequest,
    ScoreRequest,
    WorkflowRequest,
)
from music_creation_engine.services.midi_service import MidiService
from music_creation_engine.services.playability_service import PlayabilityService
from music_creation_engine.services.reference_service import ReferenceService
from music_creation_engine.services.render_service import RenderService
from music_creation_engine.services.score_service import ScoreService
from music_creation_engine.services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)


def _print_json(data: object) -> None:
    json.dump(data, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


def _print_error_json(code: str, message: str) -> None:
    _print_json({"error": {"code": code, "message": message}})


def cmd_health() -> int:
    _print_json({"status": "ok"})
    return 0


def cmd_capabilities() -> int:
    settings = load_settings()
    _print_json(detect_capabilities(settings).to_dict())
    return 0


def cmd_score(args: argparse.Namespace) -> int:
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
            chord_progression=[item for item in args.chord_progression.split(",") if item] if args.chord_progression else [],
            sections=json.loads(args.sections) if args.sections else [],
            melody=json.loads(args.melody) if args.melody else {},
            instrument_roles=json.loads(args.instrument_roles) if args.instrument_roles else {},
        )
    )
    _print_json(result)
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    service = RenderService()
    result = service.render(
        RenderRequest(
            midi_path=args.midi,
            output_base=args.output,
            format=args.format,
            soundfont_path=args.soundfont,
        )
    )
    _print_json(result)
    return 0


def cmd_workflow_full(args: argparse.Namespace) -> int:
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
            chord_progression=[item for item in args.chord_progression.split(",") if item] if args.chord_progression else [],
            sections=json.loads(args.sections) if args.sections else [],
            melody=json.loads(args.melody) if args.melody else {},
            instrument_roles=json.loads(args.instrument_roles) if args.instrument_roles else {},
        )
    )
    _print_json(result)
    return 0


def cmd_references_search(args: argparse.Namespace) -> int:
    service = ReferenceService()
    result = service.search(
        ReferenceSearchRequest(keyword=args.keyword, platform=args.platform)
    )
    _print_json(result)
    return 0


def cmd_adapters_install() -> int:
    installed = install_adapter_files(Path.cwd())
    _print_json(installed)
    return 0


def cmd_midi_diff(args: argparse.Namespace) -> int:
    service = MidiService()
    result = service.diff(
        MidiDiffRequest(
            left_notes=[int(item) for item in args.left_notes.split(",") if item],
            right_notes=[int(item) for item in args.right_notes.split(",") if item],
        )
    )
    _print_json(result)
    return 0


def cmd_midi_inspect(args: argparse.Namespace) -> int:
    service = MidiService()
    result = service.inspect(MidiInspectRequest(notes=[int(item) for item in args.notes.split(",") if item]))
    _print_json(result)
    return 0


def cmd_midi_query(args: argparse.Namespace) -> int:
    service = MidiService()
    result = service.query(
        MidiQueryRequest(
            notes=[int(item) for item in args.notes.split(",") if item],
            min_pitch=args.min_pitch,
            max_pitch=args.max_pitch,
        )
    )
    _print_json(result)
    return 0


def cmd_playability(args: argparse.Namespace) -> int:
    service = PlayabilityService()
    result = service.evaluate(
        PlayabilityRequest(
            instrument=args.instrument,
            notes=[int(item) for item in args.notes.split(",") if item],
        )
    )
    _print_json(result)
    return 0


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
    score.add_argument("--chord-progression", default="")
    score.add_argument("--sections", default="")
    score.add_argument("--melody", default="")
    score.add_argument("--instrument-roles", default="")
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
    workflow_full.add_argument("--chord-progression", default="")
    workflow_full.add_argument("--sections", default="")
    workflow_full.add_argument("--melody", default="")
    workflow_full.add_argument("--instrument-roles", default="")
    references = subparsers.add_parser("references")
    references_subparsers = references.add_subparsers(dest="references_command")
    references_search = references_subparsers.add_parser("search")
    references_search.add_argument("--keyword", required=True)
    references_search.add_argument("--platform", default="netease")
    adapters = subparsers.add_parser("adapters")
    adapters_subparsers = adapters.add_subparsers(dest="adapters_command")
    adapters_subparsers.add_parser("install")
    midi = subparsers.add_parser("midi")
    midi_subparsers = midi.add_subparsers(dest="midi_command")
    midi_diff = midi_subparsers.add_parser("diff")
    midi_diff.add_argument("--left-notes", required=True)
    midi_diff.add_argument("--right-notes", required=True)
    midi_inspect = midi_subparsers.add_parser("inspect")
    midi_inspect.add_argument("--notes", required=True)
    midi_query = midi_subparsers.add_parser("query")
    midi_query.add_argument("--notes", required=True)
    midi_query.add_argument("--min-pitch", type=int)
    midi_query.add_argument("--max-pitch", type=int)
    playability = subparsers.add_parser("playability")
    playability.add_argument("--instrument", required=True)
    playability.add_argument("--notes", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    try:
        if args.command == "health":
            return cmd_health()

        if args.command == "capabilities":
            return cmd_capabilities()

        if args.command == "score":
            return cmd_score(args)

        if args.command == "render":
            return cmd_render(args)

        if args.command == "workflow" and args.workflow_command == "full":
            return cmd_workflow_full(args)

        if args.command == "references" and args.references_command == "search":
            return cmd_references_search(args)

        if args.command == "adapters" and args.adapters_command == "install":
            return cmd_adapters_install()

        if args.command == "midi" and args.midi_command == "diff":
            return cmd_midi_diff(args)

        if args.command == "midi" and args.midi_command == "inspect":
            return cmd_midi_inspect(args)

        if args.command == "midi" and args.midi_command == "query":
            return cmd_midi_query(args)

        if args.command == "playability":
            return cmd_playability(args)

        parser.print_help()
        return 1

    except EngineError as exc:
        logger.error("cli: %s %s", exc.code.value, exc.message)
        _print_error_json(exc.code.value, exc.message)
        return 1
    except Exception:
        logger.exception("cli: unexpected error")
        _print_error_json(ErrorCode.RUNTIME_FAILURE.value, "Unexpected internal error")
        return 1


def run() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    run()
