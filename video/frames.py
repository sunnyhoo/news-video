#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频帧生成模块 - 军情巴朗风格
==============================
包含所有视频帧的生成函数：
- 标题帧、转场帧、新闻帧
- 总结帧、结尾帧
"""

import logging
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, ASSETS_DIR,
    FONT_REGULAR, FONT_BOLD, FONT_BLACK,
    C,
)

logger = logging.getLogger(__name__)


def get_font(size, bold=False):
    """获取字体"""
    path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def draw_text_centered(draw, text, font, y, max_width, fill):
    """居中绘制文字（自动换行）"""
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        current = ""
        for ch in paragraph:
            test = current + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width:
                if current:
                    lines.append(current)
                current = ch
            else:
                current = test
        if current:
            lines.append(current)

    total_height = len(lines) * (font.size + 8)
    start_y = y - total_height // 2

    for line in lines:
        if not line:
            start_y += font.size + 8
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (VIDEO_WIDTH - tw) // 2
        draw.text((x, start_y), line, font=font, fill=fill)
        start_y += font.size + 8


def draw_text_left(draw, text, font, x, y, max_width, fill, line_spacing=10):
    """左对齐绘制文字（自动换行）"""
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        current = ""
        for ch in paragraph:
            test = current + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width:
                if current:
                    lines.append(current)
                current = ch
            else:
                current = test
        if current:
            lines.append(current)

    for line in lines:
        if not line:
            y += font.size + line_spacing
            continue
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_spacing
    return y


def create_title_frame():
    """标题帧 - 军情巴朗风格"""
    bg_path = ASSETS_DIR / "title_bg.png"
    if bg_path.exists():
        img = Image.open(str(bg_path)).convert("RGB")
    else:
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), C["bg"])
    draw = ImageDraw.Draw(img)

    # 顶部红色装饰条
    draw.rectangle([(0, 0), (VIDEO_WIDTH, 6)], fill=C["red"])

    # 左右红色竖条
    draw.rectangle([(50, 150), (58, 500)], fill=C["red"])
    draw.rectangle([(VIDEO_WIDTH - 58, 150), (VIDEO_WIDTH - 50, 500)], fill=C["red"])

    # 主标题
    font_title = get_font(68, bold=True)
    draw_text_centered(draw, "全球军事政治热点速递", font_title, 320, VIDEO_WIDTH - 300, C["white"])

    # 副标题
    font_sub = get_font(32)
    draw_text_centered(draw, "国际局势深度解读", font_sub, 430, VIDEO_WIDTH - 300, C["gold"])

    # 日期和标签
    font_info = get_font(24)
    now_str = datetime.now().strftime("%Y年%m月%d日")
    draw.text((80, VIDEO_HEIGHT - 120), now_str, font=font_info, fill=C["gray"])
    draw.text((VIDEO_WIDTH - 350, VIDEO_HEIGHT - 120), "时事评论 | 深度分析", font=font_info, fill=C["gray"])

    # 底部红色条
    draw.rectangle([(0, VIDEO_HEIGHT - 6), (VIDEO_WIDTH, VIDEO_HEIGHT)], fill=C["red"])

    return img


def create_transition_frame(index, total, category, title):
    """转场帧 - 新闻切换过渡"""
    bg_path = ASSETS_DIR / "transition.png"
    if bg_path.exists():
        img = Image.open(str(bg_path)).convert("RGB")
    else:
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), C["bg_dark"])
    draw = ImageDraw.Draw(img)

    # 中央圆形编号
    cx, cy = VIDEO_WIDTH // 2, VIDEO_HEIGHT // 2 - 60
    r = 80
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=C["red"], width=4)
    font_num = get_font(64, bold=True)
    num_text = f"{index:02d}"
    bbox = draw.textbbox((0, 0), num_text, font=font_num)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy - 32), num_text, font=font_num, fill=C["white"])

    # 分类标签
    font_cat = get_font(28, bold=True)
    cat_text = f"【{category}】"
    bbox = draw.textbbox((0, 0), cat_text, font=font_cat)
    tw = bbox[2] - bbox[0]
    draw.text(((VIDEO_WIDTH - tw) // 2, cy + 100), cat_text, font=font_cat, fill=C["gold"])

    # 标题
    font_title = get_font(40, bold=True)
    draw_text_centered(draw, title, font_title, cy + 180, VIDEO_WIDTH - 300, C["white"])

    return img


def create_news_frame(item, index, total):
    """新闻详情帧 - 军情巴朗风格"""
    bg_path = ASSETS_DIR / "news_bg.png"
    if bg_path.exists():
        img = Image.open(str(bg_path)).convert("RGB")
        draw = ImageDraw.Draw(img)
    else:
        # 创建渐变背景
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), C["bg"])
        draw = ImageDraw.Draw(img)
        # 添加深色渐变效果
        for i in range(VIDEO_HEIGHT):
            alpha = int(255 * (1 - i / VIDEO_HEIGHT * 0.3))
            draw.rectangle([(0, i), (VIDEO_WIDTH, i + 1)], fill=(0, 0, 0))
        draw = ImageDraw.Draw(img)

    # 顶部红色条
    draw.rectangle([(0, 0), (VIDEO_WIDTH, 5)], fill=C["red"])

    # 左侧红色装饰线
    draw.rectangle([(40, 30), (46, VIDEO_HEIGHT - 30)], fill=C["red"])

    # 顶部信息栏
    font_cat = get_font(22, bold=True)
    font_sev = get_font(20)
    font_tag = get_font(20, bold=True)

    # 分类 + 标签
    cat_text = item["category"]
    tag_text = item.get("tag", "")
    draw.text((70, 20), cat_text, font=font_cat, fill=C["gold"])

    # 标签（如"突发"、"深度"）
    if tag_text:
        tag_color = C["red"] if tag_text in ("突发", "警示") else C["accent_blue"]
        tag_bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
        tag_w = tag_bbox[2] - tag_bbox[0] + 20
        draw.rounded_rectangle(
            [(70 + len(cat_text) * 24 + 20, 18), (70 + len(cat_text) * 24 + 20 + tag_w, 48)],
            radius=4, fill=tag_color,
        )
        draw.text((70 + len(cat_text) * 24 + 30, 20), tag_text, font=font_tag, fill=C["white"])

    # 编号
    counter = f"{index}/{total}"
    draw.text((VIDEO_WIDTH - 100, 22), counter, font=font_sev, fill=C["gray"])

    # 严重程度
    sev = item["severity"]
    sev_color = C["red"] if sev in ("极高", "高") else C["gold"]
    draw.text((VIDEO_WIDTH - 250, 22), f"● {sev}", font=font_sev, fill=sev_color)

    # 标题（大字醒目）
    y = 65
    font_title = get_font(44, bold=True)
    y = draw_text_left(draw, item["title"], font_title, 70, y, VIDEO_WIDTH - 160, C["white"], 12)

    # 元信息
    y += 10
    font_meta = get_font(20)
    meta = f"时间: {item['time']}    地点: {item['location']}"
    draw.text((70, y), meta, font=font_meta, fill=C["gray"])
    y += 35

    # 分割线
    draw.line([(70, y), (VIDEO_WIDTH - 70, y)], fill=C["card_border"], width=1)
    y += 15

    # 左右分栏内容
    col_width = (VIDEO_WIDTH - 200) // 2
    left_x = 70
    right_x = VIDEO_WIDTH // 2 + 30

    # 左栏：事件概况
    font_section = get_font(26, bold=True)
    font_body = get_font(22)
    draw.text((left_x, y), "▎事件概况", font=font_section, fill=C["accent_blue"])
    # 添加蓝色背景框
    draw.rounded_rectangle([(left_x + 5, y + 30), (left_x + col_width + 15, VIDEO_HEIGHT - 180)], radius=5, fill=(0, 30, 60, 100))
    y_left = y + 38
    y_left = draw_text_left(draw, item["content"], font_body, left_x + 10, y_left, col_width - 20, C["light_gray"], 8)

    # 右栏：深度分析
    draw.text((right_x, y), "▎深度分析", font=font_section, fill=C["gold"])
    # 添加金色背景框
    draw.rounded_rectangle([(right_x + 5, y + 30), (right_x + col_width + 15, VIDEO_HEIGHT - 180)], radius=5, fill=(60, 40, 0, 100))
    y_right = y + 38
    y_right = draw_text_left(draw, item["analysis"], font_body, right_x + 10, y_right, col_width - 20, C["light_gray"], 8)

    # 底部影响栏
    bottom_y = VIDEO_HEIGHT - 160
    draw.line([(70, bottom_y), (VIDEO_WIDTH - 70, bottom_y)], fill=C["card_border"], width=1)
    bottom_y += 10

    draw.text((70, bottom_y), "▎关键影响", font=font_section, fill=C["red"])
    bottom_y += 35

    font_imp = get_font(20)
    impacts = item["impact"]
    mid = (len(impacts) + 1) // 2
    for i, imp in enumerate(impacts):
        col = 0 if i < mid else 1
        row = i if i < mid else i - mid
        x_pos = 90 + col * (VIDEO_WIDTH // 2)
        y_pos = bottom_y + row * 26
        if y_pos < VIDEO_HEIGHT - 30:
            # 添加红色圆点
            draw.ellipse([(x_pos - 10, y_pos + 8), (x_pos - 2, y_pos + 16)], fill=C["red"])
            draw.text((x_pos, y_pos), imp, font=font_imp, fill=C["gold"])

    # 底部来源信息
    font_source = get_font(16)
    sources_text = "来源: " + ", ".join(item.get("sources", []))
    draw.text((70, VIDEO_HEIGHT - 60), sources_text, font=font_source, fill=C["gray"])

    return img


def create_summary_frame():
    """总结帧"""
    bg_path = ASSETS_DIR / "summary_bg.png"
    if bg_path.exists():
        img = Image.open(str(bg_path)).convert("RGB")
    else:
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), C["bg"])
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (VIDEO_WIDTH, 5)], fill=C["gold"])
    draw.rectangle([(0, VIDEO_HEIGHT - 5), (VIDEO_WIDTH, VIDEO_HEIGHT)], fill=C["gold"])

    font_title = get_font(44, bold=True)
    font_body = get_font(26)

    draw.text((80, 60), "▎本期总结", font=font_title, fill=C["gold"])

    summary_lines = [
        "1. 美以伊战争国际化加剧 —— 胡塞武装参战，霍尔木兹海峡封锁",
        "2. 俄乌消耗战持续升级 —— 俄军发动最大规模进攻",
        "3. 中美贸易博弈反复摇摆 —— 双方互征关税超30%",
        "4. 南海台海暗流涌动 —— 日本自卫队首登菲律宾",
        "",
        "核心判断：旧秩序崩塌与新秩序建立的过渡期阵痛",
        "多极化趋势不可逆转，保持战略定力是应对之道",
    ]

    y = 140
    for line in summary_lines:
        if not line:
            y += 20
            continue
        color = C["white"] if not line.startswith("核心") else C["gold"]
        draw.text((100, y), line, font=font_body, fill=color)
        y += 45

    return img


def create_ending_frame():
    """结尾帧"""
    bg_path = ASSETS_DIR / "ending_bg.png"
    if bg_path.exists():
        img = Image.open(str(bg_path)).convert("RGB")
    else:
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), C["bg_dark"])
    draw = ImageDraw.Draw(img)

    font_big = get_font(56, bold=True)
    font_sub = get_font(30)
    font_small = get_font(22)

    # 感谢语
    text = "感谢收看"
    bbox = draw.textbbox((0, 0), text, font=font_big)
    tw = bbox[2] - bbox[0]
    draw.text(((VIDEO_WIDTH - tw) // 2, 380), text, font=font_big, fill=C["white"])

    sub = "全球军事政治热点速递"
    bbox = draw.textbbox((0, 0), sub, font=font_sub)
    tw = bbox[2] - bbox[0]
    draw.text(((VIDEO_WIDTH - tw) // 2, 460), sub, font=font_sub, fill=C["gold"])

    follow = "关注我们 · 获取最新国际时政军事深度分析"
    bbox = draw.textbbox((0, 0), follow, font=font_small)
    tw = bbox[2] - bbox[0]
    draw.text(((VIDEO_WIDTH - tw) // 2, 540), follow, font=font_small, fill=C["gray"])

    # 数据来源
    disclaimer = "数据来源：美联社 · 中国国防部 · 乌克兰国防部 · ISW · 联合国"
    bbox = draw.textbbox((0, 0), disclaimer, font=font_small)
    tw = bbox[2] - bbox[0]
    draw.text(((VIDEO_WIDTH - tw) // 2, VIDEO_HEIGHT - 150), disclaimer, font=font_small, fill=C["gray"])

    now_str = datetime.now().strftime("%Y-%m-%d")
    bbox = draw.textbbox((0, 0), now_str, font=font_small)
    tw = bbox[2] - bbox[0]
    draw.text(((VIDEO_WIDTH - tw) // 2, VIDEO_HEIGHT - 110), now_str, font=font_small, fill=C["gray"])

    draw.rectangle([(0, VIDEO_HEIGHT - 5), (VIDEO_WIDTH, VIDEO_HEIGHT)], fill=C["red"])

    return img
