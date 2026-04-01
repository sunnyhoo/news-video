#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻数据模块
============
预设新闻数据集，用于视频生成。
"""

from news.data import get_news_data
from news.analyzer import build_voiceover_text

__all__ = ["get_news_data", "build_voiceover_text"]
