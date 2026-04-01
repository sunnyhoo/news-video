#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS 引擎模块
============
多引擎TTS管理器，支持 Edge TTS / Qwen TTS / gTTS / espeak。
从 news_video_v2.py 提取，移除了未使用的 import。
"""

import asyncio
import logging
import os
import subprocess
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSEngine:
    """多引擎TTS管理器"""

    def __init__(self, engine="edge", voice=None, speed=1.0):
        self.engine = engine
        self.voice = voice
        self.speed = speed

    def generate(self, text: str, output_path: Path) -> Path:
        """生成语音文件，返回音频文件路径"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.engine == "edge":
            return self._edge_tts(text, output_path)
        elif self.engine == "qwen":
            return self._qwen_tts(text, output_path)
        elif self.engine == "gtts":
            return self._gtts(text, output_path)
        elif self.engine == "espeak":
            return self._espeak(text, output_path)
        else:
            raise ValueError(f"不支持的TTS引擎: {self.engine}")

    def _edge_tts(self, text: str, output_path: Path) -> Path:
        """Edge TTS - 免费高质量中文语音"""
        if not self.voice:
            self.voice = "zh-CN-YunyangNeural"  # 默认新闻播报男声

        # 计算语速参数
        rate = "+0%"
        if self.speed > 1.0:
            rate = f"+{int((self.speed - 1) * 100)}%"
        elif self.speed < 1.0:
            rate = f"{int((self.speed - 1) * 100)}%"

        mp3_path = output_path.with_suffix(".mp3")

        async def _gen():
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice, rate=rate)
            await communicate.save(str(mp3_path))

        try:
            asyncio.run(_gen())
            logger.info(f"Edge TTS 生成成功: {mp3_path.name} (音色: {self.voice})")
            return mp3_path
        except Exception as e:
            logger.warning(f"Edge TTS 失败: {e}, 回退到 espeak")
            return self._espeak(text, output_path)

    def _qwen_tts(self, text: str, output_path: Path) -> Path:
        """Qwen TTS - 阿里通义千问语音合成（支持声音复刻）"""
        api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        if not api_key:
            logger.warning("未设置 DASHSCOPE_API_KEY, 回退到 Edge TTS")
            return self._edge_tts(text, output_path)

        if not self.voice:
            self.voice = "Cherry"

        try:
            import dashscope
            from dashscope.audio.qwen_tts_realtime import (
                AudioFormat,
                QwenTtsRealtime,
                QwenTtsRealtimeCallback,
            )

            dashscope.api_key = api_key
            pcm_path = output_path.with_suffix(".pcm")
            mp3_path = output_path.with_suffix(".mp3")

            import threading

            class Callback(QwenTtsRealtimeCallback):
                def __init__(self):
                    self.complete = threading.Event()
                    self.file = open(str(pcm_path), "wb")

                def on_event(self, response):
                    import base64
                    if response.get("type") == "response.audio.delta":
                        self.file.write(base64.b64decode(response["delta"]))
                    if response.get("type") == "session.finished":
                        self.complete.set()

                def on_close(self, code, msg):
                    self.file.close()

            cb = Callback()
            tts = QwenTtsRealtime(
                model="qwen3-tts-flash-realtime",
                callback=cb,
                url="wss://dashscope.aliyuncs.com/api-ws/v1/realtime",
            )
            tts.connect()
            tts.update_session(
                voice=self.voice,
                response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
                mode="server_commit",
            )
            # 分段发送文本
            for chunk in self._split_text(text, 50):
                tts.append_text(chunk)
                time.sleep(0.05)
            tts.finish()
            cb.complete.wait(timeout=60)

            # PCM转MP3
            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
                    "-i", str(pcm_path), "-ar", "44100", "-b:a", "192k", str(mp3_path),
                ],
                check=True, capture_output=True,
            )
            logger.info(f"Qwen TTS 生成成功: {mp3_path.name} (音色: {self.voice})")
            return mp3_path
        except Exception as e:
            logger.warning(f"Qwen TTS 失败: {e}, 回退到 Edge TTS")
            return self._edge_tts(text, output_path)

    def _gtts(self, text: str, output_path: Path) -> Path:
        """Google TTS"""
        mp3_path = output_path.with_suffix(".mp3")
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang="zh-cn", slow=False)
            tts.save(str(mp3_path))
            logger.info(f"gTTS 生成成功: {mp3_path.name}")
            return mp3_path
        except Exception as e:
            logger.warning(f"gTTS 失败: {e}, 回退到 espeak")
            return self._espeak(text, output_path)

    def _espeak(self, text: str, output_path: Path) -> Path:
        """espeak-ng 本地TTS（离线备选）"""
        wav_path = output_path.with_suffix(".wav")
        mp3_path = output_path.with_suffix(".mp3")
        speed_val = int(160 * self.speed)
        subprocess.run(
            ["espeak-ng", "-v", "cmn", "-s", str(speed_val), "-p", "45", "-a", "100",
             "-w", str(wav_path), text],
            check=True, capture_output=True,
        )
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(wav_path), "-ar", "44100", "-b:a", "128k", str(mp3_path)],
            check=True, capture_output=True,
        )
        logger.info(f"espeak TTS 生成成功: {mp3_path.name}")
        return mp3_path

    @staticmethod
    def _split_text(text, max_len):
        """将文本分割为适合TTS的短段"""
        chunks = []
        while text:
            if len(text) <= max_len:
                chunks.append(text)
                break
            # 在标点处分割
            idx = max_len
            for sep in ["。", "！", "？", "；", "，", " "]:
                pos = text.rfind(sep, 0, max_len)
                if pos > 0:
                    idx = pos + 1
                    break
            chunks.append(text[:idx])
            text = text[idx:]
        return chunks
