# 字幕生成 (video_subtitles)

使用 **Whisper** 识别语音、生成 **ASS** 字幕，并用 **FFmpeg** 烧录进视频。支持中英文，Mac / Windows / Linux。

## 环境要求

- **Python** ≥ 3.9（3.8 可用 openai-whisper 回退，较慢）
- **依赖**：`pip install faster-whisper`（或 `openai-whisper`）
- **FFmpeg**（烧录时需支持 libass）
- **字体**：Mac 默认 PingFang SC，Windows/Linux 默认 SimHei；无中文字体会出现方框

## 快速开始

在本目录下执行：

```bash
# 只生成 .ass，不烧录
python run.py demo.mp4 --no-burn

# 生成 .ass 并烧录（默认输出：demo_subbed.mp4）
python run.py demo.mp4 -o 带字幕.mp4
```

项目内提供 **demo.mp4** 作为示例视频，可直接用上述命令试跑。

## 命令行

```bash
python run.py <视频路径> [选项]
```

| 参数 | 说明 | 默认 |
|------|------|------|
| `-o`, `--output` | 烧录后的视频路径 | `原文件名_subbed.mp4` |
| `--ass` | 输出的 .ass 路径 | 与视频同目录、同名 .ass |
| `--no-burn` | 只生成 .ass，不烧录 | — |
| `--model` | Whisper 模型 | `base`（可选 tiny/small/medium/large-v3） |
| `--language` | 语言代码（zh、en 等） | 自动检测 |
| `--device` | 推理设备 | `auto`（cuda/cpu） |

## 目录结构

- **`run.py`** — 唯一入口（命令行）
- **`src/video_subtitles/`** — 代码包：`transcribe.py`、`ass_style.py`、`burn.py`

## 在代码中调用

需将本仓库的**父目录**加入 `sys.path`，或从父目录运行：

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

自定义 ASS 样式：使用 `video_subtitles.ass_style` 中的 `generate_ass_header()` 和 `create_ass_file(..., header=header)`。

## 常见问题

- **Python 3.8 安装 faster-whisper 报错** → 使用 Python 3.9+，或 `pip install openai-whisper`，脚本会自动回退。
- **字幕显示方框** → 安装中文字体（如 Linux：`fonts-noto-cjk`）。
- **烧录时提示 Error opening font (PingFangUI.ttc)** → libass 会回退，字幕正常；可改默认字体为 `Heiti SC`（在 `ass_style.py`）。
