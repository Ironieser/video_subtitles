# -*- coding: utf-8 -*-
"""
ASS (Advanced Substation Alpha) styles and file generation.
"""

import sys
from pathlib import Path
from typing import List, Union, Any


DEFAULT_PLAY_RES_X = 1920
DEFAULT_PLAY_RES_Y = 1080
DEFAULT_FONT = "PingFang SC" if sys.platform == "darwin" else "SimHei"


def generate_ass_header(
    play_res_x: int = DEFAULT_PLAY_RES_X,
    play_res_y: int = DEFAULT_PLAY_RES_Y,
    font_name: str = None,
    font_size: int = 80,
    primary_colour: str = "&H00FFFFFF",
    secondary_colour: str = "&H000000FF",
    outline_colour: str = "&H00000000",
    back_colour: str = "&H00000000",
    bold: int = 0,
    italic: int = 0,
    border_style: int = 1,
    outline: float = 2.5,
    shadow: float = 1.0,
    alignment: int = 2,
    margin_l: int = 10,
    margin_r: int = 10,
    margin_v: int = 40,
    encoding: int = 1,
) -> str:
    """Build [Script Info] and [V4+ Styles] header. Colours AABBGGRR; alignment 2=bottom-center."""
    if font_name is None:
        font_name = DEFAULT_FONT
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_colour},{secondary_colour},{outline_colour},{back_colour},{bold},{italic},{border_style},{outline},{shadow},{alignment},{margin_l},{margin_r},{margin_v},{encoding}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def format_time_ass(seconds: float) -> str:
    """Seconds → H:MM:SS.cs (centiseconds)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds * 100) % 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def _escape_ass_text(text: str) -> str:
    if not text:
        return ""
    return text.replace("\\", "\\\\").replace("{", "{{").replace("}", "}}").replace("\n", "\\N")


def create_ass_file(
    segments: List[Any],
    filename: Union[str, Path],
    header: str = None,
    *,
    text_attr: str = "text",
    start_attr: str = "start",
    end_attr: str = "end",
) -> Path:
    """Write segments to .ass file. Each segment has .start, .end, .text (or dict keys)."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    if header is None:
        header = generate_ass_header()

    with open(path, "w", encoding="utf-8") as f:
        f.write(header)
        for seg in segments:
            if hasattr(seg, start_attr):
                start = getattr(seg, start_attr)
                end = getattr(seg, end_attr)
                text = getattr(seg, text_attr, None) or getattr(seg, "text", "")
            else:
                start = seg.get(start_attr)
                end = seg.get(end_attr)
                text = seg.get(text_attr, seg.get("text", ""))
            start_s = format_time_ass(float(start))
            end_s = format_time_ass(float(end))
            line = _escape_ass_text(str(text).strip())
            f.write(f"Dialogue: 0,{start_s},{end_s},Default,,0,0,0,,{line}\n")

    return path
