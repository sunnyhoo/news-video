#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频合成模块
============
使用 ffmpeg 将视频帧和音频合成为最终视频。
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path

from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS, OUTPUT_DIR, TEMP_DIR
from news.analyzer import build_voiceover_text
from video.frames import (
    create_title_frame,
    create_transition_frame,
    create_news_frame,
    create_summary_frame,
    create_ending_frame,
)

logger = logging.getLogger(__name__)


def generate_video(news_items, tts_engine):
    """生成完整视频"""
    logger.info("开始生成视频...")

    # 1. 生成语音
    logger.info("生成语音...")
    voiceover_text = build_voiceover_text(news_items)
    audio_path = tts_engine.generate(voiceover_text, TEMP_DIR / "voiceover_full.wav")

    # 获取音频时长
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio_path)],
        capture_output=True, text=True,
    )
    total_duration = float(probe.stdout.strip())
    logger.info(f"语音总时长: {total_duration:.1f}秒 ({total_duration/60:.1f}分钟)")

    # 2. 生成视频帧
    logger.info("生成视频帧...")
    frames = []

    # 标题帧
    title_img = create_title_frame()
    title_path = TEMP_DIR / "frame_title.png"
    title_img.save(str(title_path))
    frames.append(("title", title_path, 8))  # 8秒

    # 转场帧 + 新闻帧
    news_duration_per = (total_duration - 8 - 10) / len(news_items)  # 减去标题和结尾
    for i, item in enumerate(news_items):
        # 转场帧
        trans_img = create_transition_frame(i + 1, len(news_items), item["category"], item["title"])
        trans_path = TEMP_DIR / f"frame_trans_{item['id']}.png"
        trans_img.save(str(trans_path))
        frames.append(("transition", trans_path, 3))  # 3秒转场

        # 新闻帧
        news_img = create_news_frame(item, i + 1, len(news_items))
        news_path = TEMP_DIR / f"frame_news_{item['id']}.png"
        news_img.save(str(news_path))
        frames.append(("news", news_path, news_duration_per))

    # 总结帧
    summary_img = create_summary_frame()
    summary_path = TEMP_DIR / "frame_summary.png"
    summary_img.save(str(summary_path))
    frames.append(("summary", summary_path, 8))

    # 结尾帧
    ending_img = create_ending_frame()
    ending_path = TEMP_DIR / "frame_ending.png"
    ending_img.save(str(ending_path))
    frames.append(("ending", ending_path, 5))

    # 3. 使用ffmpeg合成视频（比moviepy更高效）
    logger.info("合成视频...")

    # 创建concat文件
    concat_path = TEMP_DIR / "concat.txt"
    with open(concat_path, "w") as f:
        for name, path, duration in frames:
            f.write(f"file '{path}'\n")
            f.write(f"duration {duration}\n")
        # 最后一个文件需要重复（ffmpeg concat要求）
        f.write(f"file '{frames[-1][1]}'\n")

    # 计算视频总时长
    video_duration = sum(d for _, _, d in frames)

    # 先生成无声视频
    silent_video = TEMP_DIR / "silent_video.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_path),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},fps={FPS}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-preset", "medium", "-crf", "23",
            str(silent_video),
        ],
        check=True, capture_output=True,
    )

    # 合并音频和视频
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"全球军事政治热点_{timestamp}.mp4"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(silent_video),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_path),
        ],
        check=True, capture_output=True,
    )

    logger.info(f"视频生成完成: {output_path}")
    logger.info(f"   时长: {video_duration:.1f}秒 ({video_duration/60:.1f}分钟)")
    return output_path
