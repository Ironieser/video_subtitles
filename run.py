#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字幕生成一站式脚本：Whisper 识别 → 生成 .ass →（可选）FFmpeg 烧录

在本目录运行:
    python run.py 你的视频.mp4 --no-burn
    python run.py 你的视频.mp4 -o 带字幕.mp4

依赖: pip install faster-whisper，FFmpeg（烧录时）
"""

import argparse
import subprocess
import sys
from pathlib import Path

# 本目录直接运行 (python run.py) 时，把父目录加入 path 以便导入 video_subtitles
if __name__ == "__main__":
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

from video_subtitles.ass_style import generate_ass_header, create_ass_file
from video_subtitles.transcribe import transcribe_video
from video_subtitles.burn import burn_subtitles


def main() -> int:
    parser = argparse.ArgumentParser(
        description="视频字幕生成：Whisper 识别 → ASS 样式化 → 可选 FFmpeg 烧录"
    )
    parser.add_argument(
        "video",
        type=Path,
        help="输入视频路径（如 s2v-14B_832*480_4_..._081358.mp4）",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="烧录后的输出视频路径；不指定则用 原文件名_subbed.mp4",
    )
    parser.add_argument(
        "--ass",
        type=Path,
        default=None,
        help="输出的 .ass 文件路径；不指定则与视频同目录、同名 .ass",
    )
    parser.add_argument(
        "--no-burn",
        action="store_true",
        help="只做识别并生成 .ass，不调用 FFmpeg 烧录",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
        help="Whisper 模型大小 (默认 base)",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="语言代码，如 zh / en；不指定则自动检测",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="推理设备",
    )
    args = parser.parse_args()

    video_path = args.video
    if not video_path.exists():
        print(f"错误：视频文件不存在 {video_path}", file=sys.stderr)
        return 1

    base = video_path.parent / video_path.stem
    ass_path = args.ass if args.ass is not None else base.with_suffix(".ass")

    # 1. Whisper 识别
    print("正在识别语音 (Whisper)...")
    try:
        segments, info = transcribe_video(
            video_path,
            model_size=args.model,
            device=args.device,
            language=args.language,
        )
    except Exception as e:
        print(f"识别失败: {e}", file=sys.stderr)
        return 1

    if not segments:
        print("未识别到任何语音，请检查视频是否含音轨及语言设置。")
        return 0

    print(f"识别到 {len(segments)} 条片段，语言: {getattr(info, 'language', 'N/A')}")

    # 2. 生成 .ass
    print(f"正在生成 ASS 字幕: {ass_path}")
    create_ass_file(segments, ass_path)
    print("ASS 已写入。")

    if args.no_burn:
        print("已跳过烧录 (--no-burn)。")
        return 0

    # 3. FFmpeg 烧录
    out_path = args.output
    if out_path is None:
        out_path = video_path.parent / f"{video_path.stem}_subbed{video_path.suffix}"
    print(f"正在烧录字幕到: {out_path}")
    try:
        burn_subtitles(video_path, ass_path, out_path)
        print("烧录完成。")
    except FileNotFoundError as e:
        print(f"未找到 FFmpeg 或文件: {e}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 执行失败: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

