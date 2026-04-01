#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局配置模块
============
从 news_video_v2.py 提取的所有全局配置项。
路径均基于 PROJECT_ROOT，支持跨平台部署。
"""

import platform
from pathlib import Path

# ============================================================
# 项目根目录
# ============================================================
PROJECT_ROOT = Path(__file__).parent

# ============================================================
# 目录配置（基于项目根目录的相对路径）
# ============================================================
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMP_DIR = PROJECT_ROOT / ".temp"
ASSETS_DIR = PROJECT_ROOT / "video" / "assets"

# 确保目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 视频参数
# ============================================================
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 24

# ============================================================
# 颜色方案 - 军事新闻风格
# ============================================================
C = {
    "bg": (13, 17, 23),
    "bg_dark": (8, 10, 15),
    "red": (198, 40, 40),
    "red_dark": (139, 0, 0),
    "gold": (212, 160, 23),
    "white": (230, 230, 230),
    "gray": (139, 148, 158),
    "light_gray": (200, 205, 210),
    "card_bg": (22, 27, 34),
    "card_border": (48, 54, 61),
    "accent_blue": (56, 132, 244),
    "overlay": (0, 0, 0, 160),
}

# ============================================================
# 字体配置（支持跨平台）
# ============================================================
_SYSTEM = platform.system()

if _SYSTEM == "Linux":
    FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    FONT_BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
elif _SYSTEM == "Darwin":  # macOS
    FONT_REGULAR = "/System/Library/Fonts/PingFang.ttc"
    FONT_BOLD = "/System/Library/Fonts/PingFang.ttc"
    FONT_BLACK = "/System/Library/Fonts/PingFang.ttc"
elif _SYSTEM == "Windows":
    FONT_REGULAR = "C:/Windows/Fonts/msyh.ttc"
    FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
    FONT_BLACK = "C:/Windows/Fonts/msyhbd.ttc"
else:
    FONT_REGULAR = ""
    FONT_BOLD = ""
    FONT_BLACK = ""

# 允许通过环境变量覆盖字体路径
import os
FONT_REGULAR = os.environ.get("MNV_FONT_REGULAR", FONT_REGULAR)
FONT_BOLD = os.environ.get("MNV_FONT_BOLD", FONT_BOLD)
FONT_BLACK = os.environ.get("MNV_FONT_BLACK", FONT_BLACK)

# ============================================================
# Edge TTS 中文音色列表
# ============================================================
EDGE_VOICES = {
    "云扬(男-新闻播报)": "zh-CN-YunyangNeural",
    "晓晓(女-通用)": "zh-CN-XiaoxiaoNeural",
    "云希(男-温暖)": "zh-CN-YunxiNeural",
    "晓伊(女-温柔)": "zh-CN-XiaoyiNeural",
    "云健(男-专业)": "zh-CN-YunjianNeural",
    "晓梦(女-知性)": "zh-CN-XiaomengNeural",
    "云夏(男-少年)": "zh-CN-YunxiaNeural",
    "晓辰(男-少年)": "zh-CN-XiaochenNeural",
    "晓涵(女-少女)": "zh-CN-XiaohanNeural",
    "晓秋(女-成熟)": "zh-CN-XiaoqiuNeural",
    "晓瑞(男-新闻)": "zh-CN-XiaoruiNeural",
    "晓双(女-活泼)": "zh-CN-XiaoshuangNeural",
    "云野(男-自然)": "zh-CN-YunyeNeural",
    "云泽(男-沉稳)": "zh-CN-YunzeNeural",
}

# ============================================================
# Qwen TTS 音色列表
# ============================================================
QWEN_VOICES = {
    "Cherry(女-温柔)": "Cherry",
    "Serena(女-知性)": "Serena",
    "Ethan(男-沉稳)": "Ethan",
    "Chelsie(女-活泼)": "Chelsie",
}
