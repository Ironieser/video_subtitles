# -*- coding: utf-8 -*-
"""
Burn .ass subtitles into video with FFmpeg (libass).
"""

import subprocess
from pathlib import Path
from typing import Union, List


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
    """Burn ASS into video via libass. Audio is stream-copied when copy_audio=True."""
    video_path = Path(video_path)
    ass_path = Path(ass_path)
    output_path = Path(output_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    if not ass_path.exists():
        raise FileNotFoundError(f"Subtitle file not found: {ass_path}")

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
