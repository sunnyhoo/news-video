#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频模块
========
导出视频帧生成和视频合成函数。
"""

from video.frames import (
    get_font,
    draw_text_centered,
    draw_text_left,
    create_title_frame,
    create_transition_frame,
    create_news_frame,
    create_summary_frame,
    create_ending_frame,
)
from video.composer import generate_video

__all__ = [
    "get_font",
    "draw_text_centered",
    "draw_text_left",
    "create_title_frame",
    "create_transition_frame",
    "create_news_frame",
    "create_summary_frame",
    "create_ending_frame",
    "generate_video",
]
