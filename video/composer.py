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
import random

from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS, OUTPUT_DIR, TEMP_DIR, ASSETS_DIR
from news.analyzer import build_voiceover_text
from video.frames import (
    create_title_frame,
    create_transition_frame,
    create_news_frame,
    create_summary_frame,
    create_ending_frame,
)

logger = logging.getLogger(__name__)

# 新闻类别对应的视频素材映射
CATEGORY_VIDEO_MAP = {
    "国际新闻": ["international.mp4"],
    "国防新闻": ["military.mp4"],
    "政治新闻": ["politics.mp4"],
    "经济新闻": ["economy.mp4"],
    "科技新闻": ["technology.mp4"],
    "默认": ["default.mp4"]
}


def get_video_background(category):
    """根据新闻类别获取视频背景"""
    video_dir = ASSETS_DIR / "videos"
    if not video_dir.exists():
        video_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取该类别的视频列表
    videos = CATEGORY_VIDEO_MAP.get(category, CATEGORY_VIDEO_MAP["默认"])
    
    # 随机选择一个视频
    selected_video = random.choice(videos)
    video_path = video_dir / selected_video
    
    # 如果视频不存在，返回None
    if not video_path.exists():
        logger.warning(f"视频素材不存在: {video_path}")
        return None
    
    return video_path


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
        trans_path = TEMP_DIR / f"frame_trans_{i}.png"
        trans_img.save(str(trans_path))
        frames.append(("transition", trans_path, 3))  # 3秒转场

        # 新闻帧 - 尝试使用视频背景
        category = item.get("category", "默认")
        video_background = get_video_background(category)
        
        if video_background:
            # 使用视频背景
            news_video_path = TEMP_DIR / f"news_video_{i}.mp4"
            # 截取视频片段
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(video_background),
                    "-t", str(news_duration_per),
                    "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},fps={FPS}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-preset", "medium", "-crf", "23",
                    str(news_video_path),
                ],
                check=True, capture_output=True,
            )
            frames.append(("news_video", news_video_path, news_duration_per))
        else:
            # 使用静态图片帧
            news_img = create_news_frame(item, i + 1, len(news_items))
            news_path = TEMP_DIR / f"frame_news_{i}.png"
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
            if name.endswith("_video"):
                # 视频文件直接使用
                f.write(f"file '{path}'\n")
            else:
                # 图片文件需要指定持续时间
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
            "-vf", f"fps={FPS}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-preset", "medium", "-crf", "23",
            str(silent_video),
        ],
        check=True, capture_output=True,
    )

    # 处理背景音乐
    background_music_path = ASSETS_DIR / "background_music.mp3"
    if background_music_path.exists():
        # 生成背景音乐（调整音量和时长）
        bg_music = TEMP_DIR / "background_music.mp3"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(background_music_path),
                "-af", f"volume=0.15,apad=pad_dur={video_duration}",
                "-t", str(video_duration),
                str(bg_music),
            ],
            check=True, capture_output=True,
        )

        # 混合语音和背景音乐
        mixed_audio = TEMP_DIR / "mixed_audio.wav"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(audio_path),
                "-i", str(bg_music),
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=shortest",
                str(mixed_audio),
            ],
            check=True, capture_output=True,
        )
        final_audio = mixed_audio
    else:
        final_audio = audio_path

    # 合并音频和视频
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"全球军事政治热点_{timestamp}.mp4"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(silent_video),
            "-i", str(final_audio),
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
