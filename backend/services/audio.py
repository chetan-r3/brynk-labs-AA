import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
import ffmpeg

# Configuration
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a"}
TEMP_DIR = Path(__file__).parent.parent / "temp"

# Ensure temp directory exists
TEMP_DIR.mkdir(exist_ok=True)


def validate_audio_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded audio file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
    
    return True, None


async def save_audio_temp(file: UploadFile, request_id: Optional[str] = None) -> Tuple[str, Path]:
    """
    Save uploaded audio file to temporary storage.
    Converts to WAV format if needed.
    
    Args:
        file: Uploaded file object
        request_id: Optional request ID (generates UUID if not provided)
        
    Returns:
        Tuple of (request_id, file_path)
    """
    # Generate request ID if not provided
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    # Validate file
    is_valid, error_msg = validate_audio_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Read file content
    contents = await file.read()
    
    # Check file size
    file_size = len(contents)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed size ({MAX_FILE_SIZE / (1024 * 1024)} MB)"
        )
    
    # Get file extension
    file_ext = Path(file.filename).suffix.lower()
    
    # Save original file temporarily
    temp_input_path = TEMP_DIR / f"{request_id}_input{file_ext}"
    temp_output_path = TEMP_DIR / f"{request_id}.wav"
    
    try:
        # Write original file to temp
        with open(temp_input_path, "wb") as f:
            f.write(contents)
        
        # Convert to WAV if needed
        if file_ext != ".wav":
            try:
                # Convert to WAV using ffmpeg
                stream = ffmpeg.input(str(temp_input_path))
                stream = ffmpeg.output(stream, str(temp_output_path), acodec='pcm_s16le', ac=1, ar='16000')
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
                
                # Remove original file after conversion
                if temp_input_path.exists():
                    temp_input_path.unlink()
            except ffmpeg.Error as e:
                # Clean up on error
                if temp_input_path.exists():
                    temp_input_path.unlink()
                raise HTTPException(
                    status_code=500,
                    detail=f"Error converting audio file: {str(e)}"
                )
        else:
            # If already WAV, just rename
            temp_input_path.rename(temp_output_path)
        
        return request_id, temp_output_path
    
    except Exception as e:
        # Clean up on any error
        if temp_input_path.exists():
            temp_input_path.unlink()
        if temp_output_path.exists():
            temp_output_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error saving audio file: {str(e)}")


def delete_temp_file(file_path: Path) -> None:
    """
    Delete temporary audio file.
    
    Args:
        file_path: Path to the file to delete
    """
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        # Log error but don't raise (cleanup is best effort)
        print(f"Warning: Could not delete temp file {file_path}: {str(e)}")


def get_request_metadata(request_id: str, file_path: Path) -> dict:
    """
    Get metadata for a request.
    
    Args:
        request_id: Request ID
        file_path: Path to the saved file
        
    Returns:
        Dictionary with request metadata
    """
    file_size = file_path.stat().st_size if file_path.exists() else 0
    
    return {
        "request_id": request_id,
        "timestamp": datetime.now().isoformat(),
        "file_path": str(file_path),
        "file_size": file_size,
        "file_size_mb": round(file_size / (1024 * 1024), 2)
    }
