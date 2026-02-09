#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI: Whisper transcribe → ASS file → optional FFmpeg burn-in.
Run from this directory: python run.py <video> [--no-burn] or -o <output>
"""

import argparse
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    _root = Path(__file__).resolve().parent
    _src = _root / "src"
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from video_subtitles import transcribe_video, create_ass_file, burn_subtitles


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Video subtitles: Whisper → ASS → optional burn-in"
    )
    parser.add_argument("video", type=Path, help="Input video path")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output video path (default: <stem>_subbed.<suffix>)",
    )
    parser.add_argument(
        "--ass", type=Path, default=None,
        help="Output .ass path (default: same dir, same name as video)",
    )
    parser.add_argument(
        "--no-burn", action="store_true",
        help="Only transcribe and write .ass, do not burn",
    )
    parser.add_argument(
        "--model", type=str, default="base",
        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
        help="Whisper model (default: base)",
    )
    parser.add_argument(
        "--language", type=str, default=None,
        help="Language code (e.g. zh, en); auto-detect if omitted",
    )
    parser.add_argument(
        "--device", type=str, default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Device for inference",
    )
    args = parser.parse_args()

    video_path = args.video
    if not video_path.exists():
        print(f"Error: video not found: {video_path}", file=sys.stderr)
        return 1

    base = video_path.parent / video_path.stem
    ass_path = args.ass if args.ass is not None else base.with_suffix(".ass")

    print("Transcribing (Whisper)...")
    try:
        segments, info = transcribe_video(
            video_path,
            model_size=args.model,
            device=args.device,
            language=args.language,
        )
    except Exception as e:
        print(f"Transcription failed: {e}", file=sys.stderr)
        return 1

    if not segments:
        print("No speech detected. Check audio and language.")
        return 0

    print(f"Got {len(segments)} segments, language: {getattr(info, 'language', 'N/A')}")

    print(f"Writing ASS: {ass_path}")
    create_ass_file(segments, ass_path)
    print("ASS written.")

    if args.no_burn:
        print("Skipping burn (--no-burn).")
        return 0

    out_path = args.output or video_path.parent / f"{video_path.stem}_subbed{video_path.suffix}"
    print(f"Burning to: {out_path}")
    try:
        burn_subtitles(video_path, ass_path, out_path)
        print("Done.")
    except FileNotFoundError as e:
        print(f"FFmpeg or file not found: {e}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
