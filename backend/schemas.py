from pydantic import BaseModel
from typing import Optional, List


class TranscriptSegment(BaseModel):
    """Schema for a single transcript segment with timestamps and speaker"""
    speaker: str  # "Agent" or "Customer"
    text: str
    start: float
    end: float


class AudioAnalysisRequest(BaseModel):
    """Request schema for audio analysis"""
    request_id: str
    filename: str
    timestamp: str
    file_size: int
    file_size_mb: float


class SpeakerStatistics(BaseModel):
    """Statistics about speaker distribution"""
    agent: dict
    customer: dict
    total_segments: int
    total_duration: float


class Issue(BaseModel):
    """Schema for a single extracted issue"""
    title: str
    details: str
    evidence: List[str]


class Tone(BaseModel):
    """Schema for tone classification"""
    label: str  # "Calm", "Frustrated", "Angry", "Anxious"
    confidence: float  # 0.0 to 1.0
    evidence: List[str]


class AudioAnalysisResponse(BaseModel):
    """Response schema for audio analysis"""
    status: str
    request_id: str
    timestamp: str
    processing_time_seconds: float
    filename: str
    file_size_mb: float
    transcript_segments: Optional[List[TranscriptSegment]] = None
    full_transcript: Optional[str] = None
    customer_only_transcript: Optional[str] = None
    issues: Optional[List[Issue]] = None
    tone: Optional[Tone] = None
    segment_count: Optional[int] = None
    speaker_statistics: Optional[SpeakerStatistics] = None
    note: Optional[str] = None
