# -*- coding: utf-8 -*-
"""
Speech recognition via faster-whisper or openai-whisper; returns timestamped segments.
faster-whisper requires Python >= 3.9; use openai-whisper on 3.8 (slower).
"""

from pathlib import Path
from types import SimpleNamespace
from typing import List, Optional, Tuple, Any, Union


def transcribe_video(
    video_path: Union[str, Path],
    model_size: str = "base",
    device: str = "auto",
    compute_type: str = "float32",
    language: Optional[str] = None,
    word_timestamps: bool = False,
) -> Tuple[List[Any], Any]:
    """
    Transcribe video/audio; returns (segments, info).
    Segments have .start, .end, .text (and optionally .words); info has .language.
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        from faster_whisper import Whisper
    except ImportError:
        return _transcribe_with_openai_whisper(path, model_size, device, language)

    model = Whisper(model_size, device=device, compute_type=compute_type)
    segments_generator, info = model.transcribe(
        str(path),
        language=language,
        word_timestamps=word_timestamps,
    )
    segments = list(segments_generator)
    return segments, info


def _transcribe_with_openai_whisper(
    path: Path,
    model_size: str,
    device: str,
    language: Optional[str],
) -> Tuple[List[Any], Any]:
    """Fallback: openai-whisper (Python 3.8, slower)."""
    try:
        import whisper
    except ImportError:
        raise ImportError(
            "Install faster-whisper (Python>=3.9) or openai-whisper:\n"
            "  pip install faster-whisper   # or  pip install openai-whisper"
        ) from None

    model = whisper.load_model(model_size, device=device if device != "auto" else None)
    result = model.transcribe(str(path), language=language or None)
    segments = [
        SimpleNamespace(start=s["start"], end=s["end"], text=s.get("text", ""))
        for s in result.get("segments", [])
    ]
    info = SimpleNamespace(language=result.get("language"))
    return segments, info
