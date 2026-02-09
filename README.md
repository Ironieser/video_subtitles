# video_subtitles

Whisper speech recognition → ASS subtitles → optional FFmpeg burn-in. Works with Chinese/English on Mac, Windows, Linux.

## Requirements

- **Python** ≥ 3.9 (3.8: use `openai-whisper`, slower)
- **Package**: `pip install faster-whisper` (or `openai-whisper`)
- **FFmpeg** with libass (for burn-in)
- **Fonts**: Mac uses PingFang SC; Windows/Linux use SimHei. Install CJK fonts if you see boxes.

## Quick start

From this directory:

```bash
# ASS only (no burn)
python run.py demo.mp4 --no-burn

# ASS + burn to new file (default: demo_subbed.mp4)
python run.py demo.mp4 -o with_subs.mp4
```

## CLI

```bash
python run.py <video> [options]
```

| Option | Meaning | Default |
|--------|---------|---------|
| `-o`, `--output` | Output video path | `<stem>_subbed.<suffix>` |
| `--ass` | Output .ass path | Same dir, same name as video |
| `--no-burn` | Only create .ass | — |
| `--model` | Whisper model | `base` (tiny/small/medium/large-v3) |
| `--language` | e.g. `zh`, `en` | Auto |
| `--device` | `auto` / `cuda` / `cpu` | `auto` |

## Layout

- **`run.py`** — Single entry point (CLI).
- **`src/video_subtitles/`** — Package: `transcribe.py`, `ass_style.py`, `burn.py`.

## Use as library

Add the repo **parent** to `sys.path`, or run from parent:

```python
from pathlib import Path
from video_subtitles import transcribe_video, create_ass_file, burn_subtitles

video = Path("demo.mp4")
ass_path = video.with_suffix(".ass")
out_path = video.parent / f"{video.stem}_subbed{video.suffix}"

segments, info = transcribe_video(video, model_size="base")
create_ass_file(segments, ass_path)
burn_subtitles(video, ass_path, out_path)
```

Custom ASS style: use `generate_ass_header()` and `create_ass_file(..., header=header)` from `video_subtitles.ass_style`.

## Demo

`demo.mp4` is included as a sample video for testing.

## Troubleshooting

- **faster-whisper install fails (e.g. Python 3.8)** → Use `pip install openai-whisper`; script falls back automatically.
- **Subtitle boxes** → Install a CJK font (e.g. Linux: `fonts-noto-cjk`).
- **FFmpeg font warning (PingFangUI.ttc)** → Libass falls back; subtitles still work. Or set default font to `Heiti SC` in `ass_style.py`.
