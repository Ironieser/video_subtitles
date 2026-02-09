# 字幕生成 (video_subtitles)

用 **Whisper** 识别语音、生成 **ASS** 样式字幕，并用 **FFmpeg** 烧录进视频（hardsub）。支持中英文、Mac / Windows / Linux。

---

## 功能

- **语音识别**：faster-whisper 或 openai-whisper，带时间戳
- **ASS 字幕**：可配置字体、字号、颜色、描边、阴影、对齐（类似「字幕界的 CSS」）
- **烧录**：FFmpeg libass 硬字幕，画质可控

---

## 环境要求

| 项目 | 说明 |
|------|------|
| **Python** | ≥ 3.9（推荐 3.10+）。3.8 可用 openai-whisper 回退，较慢 |
| **依赖包** | `faster-whisper` 或 `openai-whisper` |
| **FFmpeg** | 烧录字幕时需要，且需支持 libass |
| **字体** | Mac 默认用 PingFang SC，Windows/Linux 默认 SimHei；无中文字体会出现方框 |

### 安装依赖

```bash
# 推荐：Python 3.9+ 下安装 faster-whisper
pip install faster-whisper

# 若为 Python 3.8 或 faster-whisper 安装失败，可改用 openai-whisper（较慢）
pip install openai-whisper
```

FFmpeg（Mac）：

```bash
brew install ffmpeg
```

---

## 快速开始

在**本目录**（`video_subtitles/`）下执行：

```bash
# 只生成 .ass，不烧录
python run.py 你的视频.mp4 --no-burn

# 生成 .ass 并烧录成新视频（默认输出：原文件名_subbed.mp4）
python run.py 你的视频.mp4 -o 带字幕.mp4
```

---

## 命令行用法

```bash
python run.py <视频路径> [选项]
```

### 参数

| 参数 | 说明 | 默认 |
|------|------|------|
| `-o`, `--output` | 烧录后的视频路径 | `原文件名_subbed.mp4` |
| `--ass` | 输出的 .ass 路径 | 与视频同目录、同名 .ass |
| `--no-burn` | 只识别并生成 .ass，不烧录 | - |
| `--model` | Whisper 模型 | `base`（可选 tiny/small/medium/large-v3） |
| `--language` | 语言代码（如 zh、en） | 自动检测 |
| `--device` | 推理设备 | `auto`（可选 cuda/cpu） |

### 示例

```bash
# 只出字幕
python run.py clip.mp4 --no-burn

# 指定输出与字幕路径
python run.py clip.mp4 -o clip_subbed.mp4 --ass clip.ass

# 用更大模型、指定中文
python run.py movie.mkv --model small --language zh -o out.mp4
```

---

## 在代码中调用

在其它项目中调用时，需把本目录的**父目录**加入 `sys.path`，或从父目录执行：

```python
from pathlib import Path
from video_subtitles import transcribe_video, create_ass_file, burn_subtitles

video_path = Path("你的视频.mp4")
ass_path = video_path.with_suffix(".ass")
out_path = video_path.parent / f"{video_path.stem}_subbed{video_path.suffix}"

# 1. 识别
segments, info = transcribe_video(video_path, model_size="base")

# 2. 生成 ASS
create_ass_file(segments, ass_path)

# 3. 烧录
burn_subtitles(video_path, ass_path, out_path)
```

自定义样式（字体、字号、颜色等）：

```python
from video_subtitles.ass_style import generate_ass_header, create_ass_file

header = generate_ass_header(
    font_name="PingFang SC",
    font_size=96,
    primary_colour="&H00FFFFFF",
    outline=3,
)
create_ass_file(segments, "out.ass", header=header)
```

---

## 目录与文件

| 文件 | 说明 |
|------|------|
| `run.py` | CLI 入口：识别 → ASS → 可选烧录 |
| `transcribe.py` | Whisper 调用（faster-whisper 优先，openai-whisper 回退） |
| `ass_style.py` | ASS 头部样式、时间格式、`create_ass_file` |
| `burn.py` | FFmpeg 烧录 ASS 到视频 |

---

## 样式说明

默认 ASS 样式（在 `ass_style.generate_ass_header()` 中）：

- **字体**：Mac 为 PingFang SC，其它为 SimHei
- **字号**：80（PlayRes 1920×1080）
- **颜色**：白字、黑描边、阴影
- **对齐**：底中（Alignment=2），下边距 40

可调参数：`font_name`、`font_size`、`primary_colour`、`outline_colour`、`outline`、`shadow`、`alignment`、`margin_v` 等，见 `ass_style.py`。

---

## 常见问题

- **Python 3.8 安装 faster-whisper 报错**（如 `puccinialin` / tokenizers）：请用 Python 3.9+，或改用 `pip install openai-whisper`，脚本会自动回退。
- **字幕显示方框**：系统缺少对应中文字体；Mac 已用 PingFang SC，Linux 可装 `fonts-noto-cjk`。
- **烧录时提示 Error opening font (PingFangUI.ttc)**：libass 会回退到 PingFang.ttc，字幕仍正常；若想消除提示可把默认字体改为 `Heiti SC`（在 `ass_style.py` 的 `DEFAULT_FONT`）。

---

## 进阶

- **双语字幕**：在写入文本时用 `\N` 换行，或定义多个 Style 分别用于上/下行。
- **卡拉 OK 逐字高亮**：使用 Whisper 的 `word_timestamps=True` 得到词级时间，再生成带 `{\k}` 标签的 ASS。

---

## 仓库与提交

本目录可单独作为 Git 仓库。创建好远程仓库后，在**本目录**执行：

```bash
git init
git add .
git commit -m "Initial commit: Whisper + ASS + FFmpeg 字幕生成"
git branch -M main
git remote add origin <你的仓库 URL>
git push -u origin main
```
