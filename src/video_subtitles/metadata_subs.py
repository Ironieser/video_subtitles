# -*- coding: utf-8 -*-
"""
从 TTS 的 narrator_metadata.json 生成字幕时间轴，无需 ASR。
元数据中每条有 duration_seconds、duration_with_interval_seconds、text，
按顺序累加得到每条 start/end，供 ASS 烧录使用。
"""

import json
from pathlib import Path
from types import SimpleNamespace
from typing import List, Union, Any


def load_metadata(metadata_path: Union[str, Path]) -> List[dict]:
    """加载 narrator_metadata.json，返回原始条目列表。"""
    path = Path(metadata_path)
    if not path.exists():
        raise FileNotFoundError(f"Metadata not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("narrator_metadata.json 应为 JSON 数组")
    return data


def metadata_to_segments(
    metadata_path: Union[str, Path],
) -> List[Any]:
    """
    根据 narrator_metadata.json 生成带时间轴的字幕段。
    每条段为 SimpleNamespace(start, end, text)，与 transcribe 返回格式兼容，
    可直接传给 create_ass_file。
    """
    items = load_metadata(metadata_path)
    segments = []
    t_start = 0.0
    for item in items:
        duration = float(item.get("duration_seconds", 0))
        duration_with_interval = float(item.get("duration_with_interval_seconds", duration))
        text = (item.get("text") or "").strip()
        if not text:
            t_start += duration_with_interval
            continue
        seg = SimpleNamespace(
            start=t_start,
            end=t_start + duration,
            text=text,
        )
        segments.append(seg)
        t_start += duration_with_interval
    return segments
