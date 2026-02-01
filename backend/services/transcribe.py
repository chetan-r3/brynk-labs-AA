import ssl
import certifi
import os
from pathlib import Path
from typing import List, Dict

# Fix SSL certificate issues before importing whisper
# This handles self-signed certificates and corporate proxies
def _fix_ssl():
    """Fix SSL certificate verification issues by patching urllib."""
    import urllib.request
    import urllib.error
    
    # Create SSL context - try certifi first, fallback to unverified
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        # Fallback: disable SSL verification (development only)
        # WARNING: Not secure for production!
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    
    # Monkey patch urlopen to use our SSL context
    original_urlopen = urllib.request.urlopen
    
    def patched_urlopen(*args, **kwargs):
        if 'context' not in kwargs:
            kwargs['context'] = ssl_context
        return original_urlopen(*args, **kwargs)
    
    urllib.request.urlopen = patched_urlopen

# Apply SSL fix before importing whisper
_fix_ssl()

import whisper

# Load Whisper model (base model - good balance of speed and accuracy)
# Model is loaded once and reused for all transcriptions
_model = None


def get_whisper_model(model_name: str = "base"):
    """
    Get or load Whisper model (singleton pattern).
    
    Args:
        model_name: Whisper model name (tiny, base, small, medium, large)
        
    Returns:
        Loaded Whisper model
        
    Raises:
        Exception: If model loading fails due to SSL or network issues
    """
    global _model
    if _model is None:
        try:
            # Load the model (SSL context is already set)
            _model = whisper.load_model(model_name)
        except ssl.SSLError as e:
            raise Exception(
                f"SSL certificate verification failed. Solutions:\n"
                f"1. Install/upgrade certifi: pip install --upgrade certifi\n"
                f"2. Set environment variable: export PYTHONHTTPSVERIFY=0 (dev only)\n"
                f"3. Install certificates: /Applications/Python\\ 3.x/Install\\ Certificates.command (macOS)\n"
                f"Original error: {str(e)}"
            )
        except Exception as e:
            error_msg = str(e)
            if "certificate" in error_msg.lower() or "ssl" in error_msg.lower():
                raise Exception(
                    f"SSL/Network error loading Whisper model. Try:\n"
                    f"1. pip install --upgrade certifi\n"
                    f"2. Set PYTHONHTTPSVERIFY=0 (development only)\n"
                    f"3. Check internet connection\n"
                    f"Original: {error_msg}"
                )
            raise Exception(f"Failed to load Whisper model '{model_name}': {error_msg}")
    return _model


def transcribe_audio(file_path: Path, model_name: str = "base") -> List[Dict[str, float]]:
    """
    Transcribe audio file using Whisper and return timestamped segments.
    
    Args:
        file_path: Path to the WAV audio file
        model_name: Whisper model to use (tiny, base, small, medium, large)
                   Default: "base" (good balance of speed and accuracy)
    
    Returns:
        List of dictionaries with "text", "start", and "end" keys
        Example:
        [
            {"text": "Hello, how can I help you?", "start": 0.0, "end": 2.1},
            {"text": "I haven't received my refund", "start": 2.2, "end": 6.8}
        ]
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    # Load Whisper model
    model = get_whisper_model(model_name)
    
    # Transcribe audio with word-level timestamps
    result = model.transcribe(
        str(file_path),
        word_timestamps=False,  # We want segment-level timestamps
        verbose=False
    )
    
    # Extract segments with timestamps
    segments = []
    for segment in result.get("segments", []):
        segments.append({
            "text": segment.get("text", "").strip(),
            "start": round(segment.get("start", 0.0), 2),
            "end": round(segment.get("end", 0.0), 2)
        })
    
    return segments


def get_full_transcript(segments: List[Dict[str, float]]) -> str:
    """
    Combine all segment texts into a single transcript.
    
    Args:
        segments: List of transcript segments
        
    Returns:
        Full transcript as a single string
    """
    return " ".join(segment["text"] for segment in segments)
