import logging
from typing import List
import whisper
from .config import WHISPER_MODEL_NAME

logger = logging.getLogger(__name__)

# Global model variable for singleton-like behavior
_whisper_model = None

def _get_whisper_model():
    """
    Internal function to load the Whisper model only once.
    """
    global _whisper_model
    if _whisper_model is None:
        logger.info(f"Loading Whisper model '{WHISPER_MODEL_NAME}'...")
        _whisper_model = whisper.load_model(WHISPER_MODEL_NAME)
        logger.info("Whisper model loaded successfully.")
    return _whisper_model

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes a single audio file and returns the transcript text.
    """
    logger.info(f"Starting transcription for {audio_path}")
    model = _get_whisper_model()
    try:
        result = model.transcribe(audio_path, task="transcribe")
        logger.info(f"Transcription completed for {audio_path}")
        return result["text"]
    except Exception as e:
        logger.error(f"Error transcribing {audio_path}: {e}")
        raise e

def transcribe_multiple(audio_files: List[str]) -> List[str]:
    """
    Transcribes multiple audio files.
    """
    transcripts = []
    for file_path in audio_files:
        try:
            transcript = transcribe_audio(file_path)
            transcripts.append(transcript)
        except Exception as e:
            logger.error(f"Skipping {file_path} due to error: {e}")
            transcripts.append("")
    return transcripts
