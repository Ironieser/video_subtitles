#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI：用 TTS 的 narrator_metadata.json 直接生成字幕并烧录，无需 ASR。
用法：python run_from_metadata.py <视频> <metadata.json> [-o 输出] [--no-burn]
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    _root = Path(__file__).resolve().parent
    _src = _root / "src"
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from video_subtitles import create_ass_file, burn_subtitles
from video_subtitles.metadata_subs import metadata_to_segments


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="从 TTS narrator_metadata.json 生成字幕并烧录进视频（无需 ASR）"
    )
    parser.add_argument("video", type=Path, help="输入视频路径")
    parser.add_argument(
        "metadata",
        type=Path,
        help="narrator_metadata.json 路径（与 merged_narrator.wav 对应）",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="烧录后的视频路径（默认：<视频名>_subbed.<后缀>）",
    )
    parser.add_argument(
        "--ass", type=Path, default=None,
        help="输出的 .ass 路径（默认：与视频同目录同名）",
    )
    parser.add_argument(
        "--no-burn", action="store_true",
        help="只生成 .ass，不烧录",
    )
    args = parser.parse_args()

    video_path = args.video
    if not video_path.exists():
        print(f"错误：视频不存在 {video_path}", file=sys.stderr)
        return 1
    if not args.metadata.exists():
        print(f"错误：元数据不存在 {args.metadata}", file=sys.stderr)
        return 1

    base = video_path.parent / video_path.stem
    ass_path = args.ass if args.ass is not None else base.with_suffix(".ass")

    print("从 metadata 生成字幕时间轴...")
    segments = metadata_to_segments(args.metadata)
    if not segments:
        print("未得到任何字幕段，请检查 metadata 中是否有 text。")
        return 0

    print(f"共 {len(segments)} 条字幕")
    print(f"写入 ASS: {ass_path}")
    create_ass_file(segments, ass_path)
    print("ASS 已写入。")

    if args.no_burn:
        print("已跳过烧录 (--no-burn)。")
        return 0

    out_path = args.output or video_path.parent / f"{video_path.stem}_subbed{video_path.suffix}"
    print(f"烧录到: {out_path}")
    try:
        burn_subtitles(video_path, ass_path, out_path)
        print("完成。")
    except FileNotFoundError as e:
        print(f"FFmpeg 或文件未找到: {e}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 错误: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
