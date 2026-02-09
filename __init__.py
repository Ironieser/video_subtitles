# -*- coding: utf-8 -*-
"""
字幕生成模块：Whisper 识别 → ASS 样式化 → FFmpeg 烧录

- transcribe: 使用 faster-whisper 生成带时间戳的文本
- ass_style: 生成 .ass 文件（字体、描边、对齐等）
- burn: 使用 FFmpeg 将 .ass 烧录进视频
"""

from .ass_style import generate_ass_header, format_time_ass, create_ass_file
from .transcribe import transcribe_video
from .burn import burn_subtitles

__all__ = [
    "generate_ass_header",
    "format_time_ass",
    "create_ass_file",
    "transcribe_video",
    "burn_subtitles",
]
