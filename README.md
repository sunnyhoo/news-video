# 全球军事政治新闻视频生成器

## 项目简介

本项目是一个自动化军事政治新闻视频生成工具，能够从预设或在线新闻源获取最新国际军事政治新闻，通过多引擎 TTS（文本转语音）生成中文语音播报，结合军情巴朗风格的视频模板，自动合成完整的新闻视频。

## 功能特性

- **多 TTS 引擎支持**：Edge TTS（免费高质量）、Qwen TTS（阿里通义千问，支持声音复刻）、Google TTS、espeak-ng（离线备选）
- **14种中文音色**：Edge TTS 提供云扬、晓晓、云希等14种音色，Qwen TTS 提供 Cherry、Serena 等4种音色
- **军情巴朗风格视频模板**：深色背景、红色金色装饰、大字标题、转场效果
- **完整的视频帧系统**：标题帧、转场帧、新闻详情帧（左右分栏）、总结帧、结尾帧
- **在线新闻抓取框架**：预留 AP News、路透社、中国国防部等新闻源接口
- **定时调度运行**：支持按小时间隔自动执行，支持 SIGINT/SIGTERM 优雅停止
- **跨平台支持**：自动适配 Linux / macOS / Windows 字体路径，支持环境变量覆盖

## 目录结构

```
military-news-video/
├── README.md                    # 项目说明文档
├── requirements.txt             # Python 依赖
├── config.py                    # 全局配置（路径、颜色、字体、音色等）
├── main.py                      # 主入口（命令行参数解析 + 流水线调度）
├── tts/
│   ├── __init__.py              # 导出 TTSEngine
│   └── engine.py                # TTSEngine 类（4个TTS引擎实现）
├── news/
│   ├── __init__.py              # 导出函数
│   ├── data.py                  # get_news_data() 预设数据
│   ├── fetcher.py               # 新闻抓取模块（框架代码，待实现）
│   └── analyzer.py              # 新闻分析 / 播报文本生成
├── video/
│   ├── __init__.py              # 导出函数
│   ├── frames.py                # 视频帧生成（标题帧、新闻帧、转场帧等）
│   ├── composer.py              # 视频合成（ffmpeg 调用）
│   └── assets/                  # 背景图片目录
│       └── .gitkeep
├── scheduler/
│   ├── __init__.py              # 导出 NewsScheduler
│   └── auto_run.py              # 定时调度器
├── output/                      # 输出目录（视频、脚本）
│   └── .gitkeep
└── tests/
    └── .gitkeep
```

## 快速开始

### 1. 安装依赖

```bash
cd military-news-video
pip install -r requirements.txt
```

系统依赖：
- **ffmpeg**：视频合成和音频转换（必须）
- **espeak-ng**：离线 TTS 备选引擎（可选）

```bash
# Ubuntu/Debian
sudo apt install ffmpeg espeak-ng

# macOS
brew install ffmpeg espeak-ng

# Windows
# 下载 ffmpeg 并添加到 PATH
```

### 2. 运行

```bash
# 单次生成（使用预设新闻数据 + Edge TTS 默认音色）
python main.py

# 指定 TTS 引擎和音色
python main.py --tts edge --voice "云扬(男-新闻播报)"
python main.py --tts edge --voice zh-CN-YunyangNeural

# 使用 Qwen TTS（需要 DASHSCOPE_API_KEY 环境变量）
export DASHSCOPE_API_KEY="your_api_key"
python main.py --tts qwen --voice Cherry

# 调整语速
python main.py --speed 1.2

# 列出所有可用音色
python main.py --list-voices

# 启用在线新闻抓取（需先实现 fetcher 模块）
python main.py --fetch --hours 24
```

## TTS 引擎配置说明

### Edge TTS（推荐）

免费、高质量中文语音，需要网络连接。

```bash
python main.py --tts edge --voice "云扬(男-新闻播报)"
```

可用音色：
| 名称 | ID |
|------|-----|
| 云扬(男-新闻播报) | zh-CN-YunyangNeural |
| 晓晓(女-通用) | zh-CN-XiaoxiaoNeural |
| 云希(男-温暖) | zh-CN-YunxiNeural |
| 晓伊(女-温柔) | zh-CN-XiaoyiNeural |
| 云健(男-专业) | zh-CN-YunjianNeural |
| 晓梦(女-知性) | zh-CN-XiaomengNeural |
| 云夏(男-少年) | zh-CN-YunxiaNeural |
| 晓辰(男-少年) | zh-CN-XiaochenNeural |
| 晓涵(女-少女) | zh-CN-XiaohanNeural |
| 晓秋(女-成熟) | zh-CN-XiaoqiuNeural |
| 晓瑞(男-新闻) | zh-CN-XiaoruiNeural |
| 晓双(女-活泼) | zh-CN-XiaoshuangNeural |
| 云野(男-自然) | zh-CN-YunyeNeural |
| 云泽(男-沉稳) | zh-CN-YunzeNeural |

### Qwen TTS

阿里通义千问语音合成，支持声音复刻，需要 API Key。

```bash
export DASHSCOPE_API_KEY="sk-xxx"
python main.py --tts qwen --voice Cherry
```

### Google TTS

免费，需要网络连接，音质一般。

```bash
python main.py --tts gtts
```

### espeak-ng

完全离线，音质较差，适合无网络环境。

```bash
python main.py --tts espeak
```

## 定时运行

使用 `--interval` 参数启用定时调度模式：

```bash
# 每12小时自动生成一次
python main.py --interval 12

# 每6小时
python main.py --interval 6 --tts edge --voice "云扬(男-新闻播报)"

# 后台运行
nohup python main.py --interval 12 > scheduler.log 2>&1 &
```

调度器支持 SIGINT (Ctrl+C) 和 SIGTERM 信号优雅停止。

也可以在代码中使用：

```python
from scheduler.auto_run import NewsScheduler

scheduler = NewsScheduler(interval_hours=12)
scheduler.run_loop()
```

## 自定义开发指南

### 修改视频模板

视频帧生成逻辑位于 `video/frames.py`，包含以下函数：

- `create_title_frame()` - 标题帧
- `create_transition_frame(index, total, category, title)` - 转场帧
- `create_news_frame(item, index, total)` - 新闻详情帧
- `create_summary_frame()` - 总结帧
- `create_ending_frame()` - 结尾帧

颜色方案在 `config.py` 的 `C` 字典中定义。背景图片放在 `video/assets/` 目录下，文件名对应：
- `title_bg.png` - 标题帧背景
- `transition.png` - 转场帧背景
- `news_bg.png` - 新闻帧背景
- `summary_bg.png` - 总结帧背景
- `ending_bg.png` - 结尾帧背景

### 添加新闻源

在 `news/fetcher.py` 中实现新的抓取方法：

```python
class NewsFetcher:
    def fetch_xinhua(self) -> List[dict]:
        """抓取新华社新闻"""
        # TODO: 实现抓取逻辑
        # 返回标准化的新闻数据列表，格式参考 news/data.py
        return []
```

然后在 `fetch_all()` 中调用。

### 修改预设新闻数据

编辑 `news/data.py` 中的 `get_news_data()` 函数，每条新闻数据格式：

```python
{
    "id": 1,
    "category": "分类名称",
    "title": "新闻标题",
    "time": "时间范围",
    "location": "地点",
    "severity": "极高/高/中高/中/低",
    "tag": "标签（突发/深度/前线等）",
    "content": "新闻内容",
    "analysis": "深度分析",
    "impact": ["影响1", "影响2", ...],
    "sources": ["来源1", "来源2", ...],
}
```

### 修改播报脚本

播报文本生成逻辑位于 `news/analyzer.py` 的 `build_voiceover_text()` 函数。

### 自定义字体

通过环境变量覆盖默认字体：

```bash
export MNV_FONT_REGULAR="/path/to/your/font-regular.ttf"
export MNV_FONT_BOLD="/path/to/your/font-bold.ttf"
export MNV_FONT_BLACK="/path/to/your/font-black.ttf"
python main.py
```

## 注意事项

1. **ffmpeg 是必需依赖**：视频合成完全依赖 ffmpeg，请确保已安装并在 PATH 中。
2. **Edge TTS 需要网络**：首次使用会下载语音模型，后续会有缓存。
3. **Qwen TTS 需要 API Key**：设置 `DASHSCOPE_API_KEY` 环境变量。
4. **字体兼容性**：项目自动适配 Linux/macOS/Windows 字体路径。如果使用其他系统或自定义字体，请通过环境变量指定。
5. **新闻抓取模块待实现**：`news/fetcher.py` 目前是框架代码，实际抓取逻辑需要根据目标网站实现。
6. **临时文件**：视频生成过程中的临时文件存放在项目根目录下的 `.temp/` 文件夹中，可安全删除。
7. **视频分辨率**：默认 1920x1080 (Full HD)，可在 `config.py` 中修改 `VIDEO_WIDTH` 和 `VIDEO_HEIGHT`。
