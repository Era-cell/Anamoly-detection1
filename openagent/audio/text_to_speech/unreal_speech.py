import asyncio
import os
import types
import httpx
import requests
import time

from openagent.logger import get_logger
from openagent.utils import Singleton
from openagent.audio.text_to_speech.base import TextToSpeech

logger = get_logger(__name__)
DEBUG = False

config = types.SimpleNamespace(**{
    'chunk_size': 1024,
    'url': 'https://lab.api.unrealspeech.com/stream',
    'headers': {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
    },
    'data': {
        'speed': -0.2,
    }
})


class UnrealSpeech(Singleton, TextToSpeech):
    def __init__(self):
        super().__init__()
        logger.info("Initializing [Unreal Speech] voices...")

    async def stream(self, text, websocket, tts_event: asyncio.Event, voice_id=5, *args, **kwargs) -> None:
        if DEBUG:
            return
        params = {
            "text": text,
            "speaker_index": voice_id,
            **config.data,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(config.url, params=params)
            if response.status_code != 200:
                logger.error(
                    f"Unreal Speech returns response {response.status_code}")
            async for chunk in response.aiter_bytes():
                await asyncio.sleep(0.1)
                if tts_event.is_set():
                    # stop streaming audio
                    break
                await websocket.send_bytes(chunk)
