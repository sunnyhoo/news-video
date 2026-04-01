#!/usr/bin/env python3
"""全球军事政治新闻视频生成器 - 主入口"""
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import OUTPUT_DIR, TEMP_DIR
from tts.engine import TTSEngine
from news.data import get_news_data
from news.analyzer import build_voiceover_text
from news.fetcher import NewsFetcher
from video.composer import generate_video

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run_pipeline(hours=12, tts_engine="edge", voice=None, speed=1.0, use_fetcher=False):
    """执行完整的视频生成流水线"""
    # 1. 获取新闻
    if use_fetcher:
        fetcher = NewsFetcher(hours=hours)
        news_items = fetcher.fetch_all()
        if not news_items:
            logger.warning("抓取未获得新闻，使用预设数据")
            news_items = get_news_data()
    else:
        news_items = get_news_data()

    logger.info(f"已加载 {len(news_items)} 条新闻")

    # 2. 初始化TTS
    tts = TTSEngine(engine=tts_engine, voice=voice, speed=speed)

    # 3. 生成脚本
    script_text = build_voiceover_text(news_items)
    script_path = OUTPUT_DIR / f"视频脚本_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    script_path.write_text(script_text, encoding="utf-8")
    logger.info(f"脚本已保存: {script_path}")

    # 4. 生成视频
    video_path = generate_video(news_items, tts)

    return {"video": video_path, "script": script_path, "news_count": len(news_items)}

def main():
    parser = argparse.ArgumentParser(description="全球军事政治新闻视频生成器")
    parser.add_argument("--hours", type=float, default=12, help="新闻时间范围（小时）")
    parser.add_argument("--tts", type=str, default="edge", choices=["edge","qwen","gtts","espeak"])
    parser.add_argument("--voice", type=str, default=None, help="TTS音色")
    parser.add_argument("--speed", type=float, default=1.0, help="语速倍率")
    parser.add_argument("--fetch", action="store_true", help="启用在线新闻抓取")
    parser.add_argument("--interval", type=float, default=None, help="定时运行间隔（小时）")
    parser.add_argument("--list-voices", action="store_true", help="列出可用音色")

    args = parser.parse_args()

    if args.list_voices:
        from config import EDGE_VOICES, QWEN_VOICES
        print("\n=== Edge TTS 中文音色 ===")
        for n, v in EDGE_VOICES.items(): print(f"  {n:30s} -> {v}")
        print("\n=== Qwen TTS 音色 ===")
        for n, v in QWEN_VOICES.items(): print(f"  {n:30s} -> {v}")
        return

    if args.interval:
        from scheduler.auto_run import NewsScheduler
        scheduler = NewsScheduler(interval_hours=args.interval)
        scheduler.run_loop()
    else:
        result = run_pipeline(
            hours=args.hours, tts_engine=args.tts,
            voice=args.voice, speed=args.speed, use_fetcher=args.fetch,
        )
        print(f"\n视频: {result['video']}")
        print(f"脚本: {result['script']}")

if __name__ == "__main__":
    main()
