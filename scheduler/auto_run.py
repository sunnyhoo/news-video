"""定时调度器"""
import time
import signal
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self, interval_hours: float = 12):
        self.interval_hours = interval_hours
        self.running = True
        signal.signal(signal.SIGINT, self._stop)
        signal.signal(signal.SIGTERM, self._stop)

    def _stop(self, signum, frame):
        logger.info("收到停止信号...")
        self.running = False

    def run_once(self):
        """执行一次完整的新闻视频生成"""
        from main import run_pipeline
        return run_pipeline()

    def run_loop(self):
        """循环运行"""
        logger.info(f"调度器启动，间隔: {self.interval_hours} 小时")
        while self.running:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"执行出错: {e}")
            if not self.running:
                break
            next_run = datetime.now() + timedelta(hours=self.interval_hours)
            logger.info(f"下次运行: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            # 分段等待，支持随时停止
            wait_secs = self.interval_hours * 3600
            elapsed = 0
            while elapsed < wait_secs and self.running:
                time.sleep(min(60, wait_secs - elapsed))
                elapsed += 60
        logger.info("调度器已停止")
