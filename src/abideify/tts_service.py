# src/abideify/tts_service.py

import os
import logging
import subprocess
import requests
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class BaseTTSService:
    """Base abstract TTS service."""
    def synthesize_text(self, text: str, voice: str, debug_mode: bool = False) -> Optional[str]:
        raise NotImplementedError


class UnrealSpeechTTSService(BaseTTSService):
    """
    Integrates with UnrealSpeech at https://api.v7.unrealspeech.com/stream
    """
    def __init__(self, api_key: str, tts_audio_dir: str):
        self.api_key = api_key
        self.tts_audio_dir = tts_audio_dir

    def synthesize_text(self, text: str, voice: str, debug_mode: bool = False) -> Optional[str]:
        if not self.api_key:
            logger.error("UnrealSpeech API key is not set. Please provide it.")
            return None

        # We'll create a temporary wave file that we eventually return
        temp_wav_file = 'temp_response.wav'
        temp_mp3_file = 'temp_response.mp3'
        url = 'https://api.v7.unrealspeech.com/stream'
        headers = {'Authorization': f'Bearer {self.api_key}'}
        data = {
            'Text': text,
            'VoiceId': voice,
            'Bitrate': '192k',
            'Speed': '0',
            'Pitch': '1',
            # For streaming endpoint, 'Codec' can be 'libmp3lame' if you want MP3
            'Codec': 'libmp3lame'
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                with open(temp_mp3_file, 'wb') as f:
                    f.write(response.content)

                # Convert MP3 -> WAV so pydub can easily handle it
                command = ['ffmpeg', '-y', '-i', temp_mp3_file, temp_wav_file]
                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # Optionally remove the MP3
                if os.path.exists(temp_mp3_file):
                    os.remove(temp_mp3_file)

                if debug_mode:
                    # Move/copy this WAV file to a debug directory with timestamp
                    os.makedirs(self.tts_audio_dir, exist_ok=True)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    debug_wav_file = os.path.join(self.tts_audio_dir, f"response_{timestamp}.wav")
                    os.rename(temp_wav_file, debug_wav_file)
                    logger.info(f"Saved TTS audio to {debug_wav_file}")
                    return debug_wav_file

                return temp_wav_file

            else:
                logger.error(f"UnrealSpeech request failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"UnrealSpeechTTSService error: {e}")
            return None

