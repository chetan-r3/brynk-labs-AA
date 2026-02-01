import time
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from services.audio import save_audio_temp, delete_temp_file, get_request_metadata
from services.transcribe import transcribe_audio, get_full_transcript
from services.diarize import label_speakers, get_speaker_statistics, get_customer_only_transcript
from services.analysis import extract_issues, classify_tone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Audio Call Analyzer API",
    description="API for analyzing audio call recordings",
    version="1.0.0"
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {"message": "Audio Call Analyzer API"}

@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze uploaded audio file.
    
    Complete pipeline:
    1. Upload & validate
    2. Normalize audio (convert to WAV)
    3. Transcribe using Whisper
    4. Speaker labeling (heuristic-based)
    5. Extract customer-only transcript
    6. Extract issues (LLM)
    7. Classify tone (LLM)
    8. Return complete analysis
    """
    request_id = None
    file_path = None
    start_time = time.time()
    
    try:
        logger.info(f"Starting analysis for file: {file.filename}")
        
        # Step 1: Save audio file to temp storage (normalize)
        logger.info("Step 1: Validating and normalizing audio...")
        request_id, file_path = await save_audio_temp(file)
        logger.info(f"Audio saved: {file_path}, Request ID: {request_id}")
        
        # Get request metadata
        metadata = get_request_metadata(request_id, file_path)
        
        # Step 2: Transcribe audio using Whisper
        logger.info("Step 2: Transcribing audio...")
        transcript_segments = transcribe_audio(file_path)
        logger.info(f"Transcription complete: {len(transcript_segments)} segments")
        
        # Step 3: Label speakers (heuristic-based)
        logger.info("Step 3: Labeling speakers...")
        labeled_segments = label_speakers(transcript_segments)
        
        # Get speaker statistics
        speaker_stats = get_speaker_statistics(labeled_segments)
        logger.info(f"Speaker labeling complete: {speaker_stats['agent']['segments']} agent, {speaker_stats['customer']['segments']} customer segments")
        
        # Get full transcript
        full_transcript = get_full_transcript(transcript_segments)
        
        # Step 4: Extract customer-only transcript
        logger.info("Step 4: Extracting customer-only transcript...")
        customer_only_transcript = get_customer_only_transcript(labeled_segments)
        
        # Step 5: Extract issues using LLM
        issues = []
        if customer_only_transcript:
            try:
                logger.info("Step 5: Extracting issues using LLM...")
                issues = extract_issues(customer_only_transcript)
                logger.info(f"Issues extracted: {len(issues)} issues found")
            except Exception as e:
                logger.warning(f"Issue extraction failed: {str(e)}")
                issues = []
        else:
            logger.info("No customer transcript available, skipping issue extraction")
        
        # Step 6: Classify tone using LLM
        tone = {
            "label": "Calm",
            "confidence": 0.5,
            "evidence": []
        }
        if customer_only_transcript:
            try:
                logger.info("Step 6: Classifying tone using LLM...")
                tone = classify_tone(customer_only_transcript)
                logger.info(f"Tone classified: {tone['label']} (confidence: {tone['confidence']})")
            except Exception as e:
                logger.warning(f"Tone classification failed: {str(e)}")
        else:
            logger.info("No customer transcript available, skipping tone classification")
        
        # Calculate processing time
        processing_time = round(time.time() - start_time, 2)
        logger.info(f"Analysis complete in {processing_time}s for request {request_id}")
        
        # Step 7: Assemble final response (with metadata for dashboard)
        return JSONResponse(
            status_code=200,
            content={
                "transcript": labeled_segments,
                "issues": issues,
                "tone": tone,
                "metadata": {
                    "filename": file.filename,
                    "file_size_mb": metadata["file_size_mb"],
                    "processing_time_seconds": processing_time,
                    "request_id": request_id,
                    "timestamp": metadata["timestamp"],
                    "segment_count": len(transcript_segments),
                    "speaker_statistics": speaker_stats
                }
            }
        )
    
    except HTTPException:
        raise
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
    
    finally:
        # Clean up temporary file after processing
        if file_path:
            logger.info(f"Cleaning up temporary file: {file_path}")
            delete_temp_file(file_path)
