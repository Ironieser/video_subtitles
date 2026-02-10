# -*- coding: utf-8 -*-
"""
Video subtitles: Whisper transcription → ASS styling → FFmpeg burn-in.
"""

from .ass_style import generate_ass_header, format_time_ass, create_ass_file
from .transcribe import transcribe_video
from .burn import burn_subtitles
from .metadata_subs import metadata_to_segments, load_metadata

__all__ = [
    "generate_ass_header",
    "format_time_ass",
    "create_ass_file",
    "transcribe_video",
    "burn_subtitles",
    "metadata_to_segments",
    "load_metadata",
]
