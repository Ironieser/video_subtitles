# -*- coding: utf-8 -*-
"""
使用 faster-whisper 或 openai-whisper 对视频/音频进行语音识别，返回带时间戳的 segments。

- faster-whisper 需要 Python >= 3.9；若在 3.8 下安装失败，可改用 openai-whisper（较慢）。
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
    对视频或音频文件做语音识别，返回 (segments, info)。

    - video_path: 视频或音频文件路径
    - model_size: 如 "tiny", "base", "small", "medium", "large-v3"
    - device: "cuda", "cpu", "auto"
    - compute_type: "float32", "int8" 等（仅 faster-whisper）
    - language: 例如 "zh", "en"，None 表示自动检测
    - word_timestamps: 是否返回词级时间戳（仅 faster-whisper 支持）

    Returns:
        segments: 每项有 .start, .end, .text（以及可选的 .words）
        info: 识别结果中的 info 对象（如 language）
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")

    # 优先使用 faster-whisper（需 Python >= 3.9）
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
    """回退：使用 openai-whisper（支持 Python 3.8，速度较慢）。"""
    try:
        import whisper
    except ImportError:
        raise ImportError(
            "未找到 faster-whisper（需 Python>=3.9）或 openai-whisper。\n"
            "  - 推荐：使用 Python 3.9+ 后执行 pip install faster-whisper\n"
            "  - 或当前环境执行：pip install openai-whisper"
        ) from None

    model = whisper.load_model(model_size, device=device if device != "auto" else None)
    result = model.transcribe(str(path), language=language or None)
    segments = [
        SimpleNamespace(start=s["start"], end=s["end"], text=s.get("text", ""))
        for s in result.get("segments", [])
    ]
    info = SimpleNamespace(language=result.get("language"))
    return segments, info
