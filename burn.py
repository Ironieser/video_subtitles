# -*- coding: utf-8 -*-
"""
使用 FFmpeg 将 .ass 字幕烧录进视频（hardsub）。
"""

import subprocess
from pathlib import Path
from typing import Union, List, Optional


def burn_subtitles(
    video_path: Union[str, Path],
    ass_path: Union[str, Path],
    output_path: Union[str, Path],
    *,
    video_codec: str = "libx264",
    preset: str = "fast",
    crf: int = 23,
    copy_audio: bool = True,
    ffmpeg_bin: str = "ffmpeg",
) -> Path:
    """
    使用 libass 滤镜将 ASS 字幕烧录到视频中。

    - video_path: 输入视频
    - ass_path: .ass 字幕文件（路径中若有逗号、反斜杠需注意 FFmpeg 转义）
    - output_path: 输出视频路径
    - video_codec / preset / crf: 视频编码参数
    - copy_audio: True 时音频流直接复制，不重新编码
    """
    video_path = Path(video_path)
    ass_path = Path(ass_path)
    output_path = Path(output_path)

    if not video_path.exists():
        raise FileNotFoundError(f"视频不存在: {video_path}")
    if not ass_path.exists():
        raise FileNotFoundError(f"字幕文件不存在: {ass_path}")

    # ass 路径传给滤镜时使用绝对路径并转义（Windows 下 \ 和 , 需转义）
    ass_abs = str(ass_path.resolve()).replace("\\", "\\\\").replace(",", "\\,")
    vf = f"ass='{ass_abs}'"

    cmd: List[str] = [
        ffmpeg_bin, "-y",
        "-i", str(video_path),
        "-vf", vf,
        "-c:v", video_codec,
        "-preset", preset,
        "-crf", str(crf),
    ]
    if copy_audio:
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    cmd.append(str(output_path))

    subprocess.run(cmd, check=True)
    return output_path
