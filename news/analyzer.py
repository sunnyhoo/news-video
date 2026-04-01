#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻分析/播报文本生成模块
==========================
将新闻数据转换为适合语音播报的文本。
"""


def build_voiceover_text(news_items):
    """构建语音播报文本（精简版，适合口语化播报）"""
    parts = []

    # 开场
    parts.append("观众朋友们大家好，欢迎收看本期全球军事政治热点速递。")
    parts.append("过去12小时，国际局势风云突变，多条重磅消息同时发酵。")
    parts.append("下面我们逐一解读。")

    for item in news_items:
        parts.append(f"首先来看{item['category']}方面的最新动态。")
        parts.append(item["title"] + "。")
        # 精简内容播报
        content = item["content"]
        if len(content) > 150:
            content = content[:150] + "。"
        parts.append(content)
        # 精简分析
        analysis = item["analysis"]
        if len(analysis) > 150:
            analysis = analysis[:150] + "。"
        parts.append(analysis)

    # 结尾
    parts.append("以上就是本期全部内容。纵观全局，世界正面临多重危机叠加的复杂局面。")
    parts.append("保持战略定力，坚定维护核心利益，是我们应对一切挑战的根本。")
    parts.append("感谢收看，我们下期再见。")

    return "".join(parts)
