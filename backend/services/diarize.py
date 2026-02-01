"""
Speaker Diarization Service

⚠️ LIMITATIONS:
This is a heuristic-based speaker labeling system, NOT true speaker diarization.
It uses simple rules to assign speaker labels and may not be accurate for:
- Calls with more than 2 speakers
- Calls where speakers don't alternate regularly
- Calls with overlapping speech
- Calls where the first speaker is not the agent

For production use, consider implementing proper speaker diarization using:
- pyannote.audio
- Resemblyzer
- Or commercial APIs (AssemblyAI, Deepgram, etc.)

Current heuristic rules:
1. First speaker is assumed to be "Agent"
2. Speakers alternate based on silence gaps
3. Longer segments (>5 seconds) are more likely to be "Customer"
4. Short responses (<2 seconds) are more likely to be "Agent"
"""

from typing import List, Dict
from pathlib import Path


def label_speakers(segments: List[Dict[str, float]], 
                   silence_threshold: float = 1.5,
                   long_segment_threshold: float = 5.0,
                   short_segment_threshold: float = 2.0) -> List[Dict[str, any]]:
    """
    Label speakers in transcript segments using heuristic rules.
    
    ⚠️ WARNING: This is a simple heuristic approach, not true speaker diarization.
    Accuracy may vary significantly depending on call characteristics.
    
    Args:
        segments: List of transcript segments with "text", "start", "end" keys
        silence_threshold: Seconds of silence to consider as speaker change (default: 1.5s)
        long_segment_threshold: Segments longer than this are likely Customer (default: 5.0s)
        short_segment_threshold: Segments shorter than this are likely Agent (default: 2.0s)
    
    Returns:
        List of segments with added "speaker" field ("Agent" or "Customer")
        
    Example:
        Input:
        [
            {"text": "Hello, how can I help you?", "start": 0.0, "end": 2.1},
            {"text": "I haven't received my refund", "start": 2.2, "end": 6.8}
        ]
        
        Output:
        [
            {"speaker": "Agent", "text": "Hello, how can I help you?", "start": 0.0, "end": 2.1},
            {"speaker": "Customer", "text": "I haven't received my refund", "start": 2.2, "end": 6.8}
        ]
    """
    if not segments:
        return []
    
    labeled_segments = []
    current_speaker = "Agent"  # First speaker is assumed to be Agent
    
    for i, segment in enumerate(segments):
        segment_duration = segment["end"] - segment["start"]
        text = segment.get("text", "").strip()
        
        # Skip empty segments
        if not text:
            continue
        
        # Calculate gap from previous segment
        gap = 0.0
        if i > 0:
            prev_end = segments[i - 1]["end"]
            gap = segment["start"] - prev_end
        
        # Heuristic 1: Long silence gap suggests speaker change
        if gap > silence_threshold and i > 0:
            current_speaker = "Customer" if current_speaker == "Agent" else "Agent"
        
        # Heuristic 2: Long segments are more likely Customer (complaints, explanations)
        elif segment_duration > long_segment_threshold:
            current_speaker = "Customer"
        
        # Heuristic 3: Very short segments are more likely Agent (quick responses)
        elif segment_duration < short_segment_threshold and i > 0:
            # Only switch if it's a very short response after a longer segment
            if i > 0 and (segments[i - 1]["end"] - segments[i - 1]["start"]) > long_segment_threshold:
                current_speaker = "Agent"
        
        # Heuristic 4: Alternate speakers for medium-length segments
        elif i > 0 and gap < silence_threshold:
            # If previous segment was from one speaker, alternate
            if i > 1:
                prev_speaker = labeled_segments[-1].get("speaker", "Agent")
                current_speaker = "Customer" if prev_speaker == "Agent" else "Agent"
        
        # Create labeled segment
        labeled_segment = {
            "speaker": current_speaker,
            "text": text,
            "start": segment["start"],
            "end": segment["end"]
        }
        
        labeled_segments.append(labeled_segment)
    
    return labeled_segments


def get_speaker_statistics(labeled_segments: List[Dict[str, any]]) -> Dict[str, any]:
    """
    Get statistics about speaker distribution.
    
    Args:
        labeled_segments: List of segments with speaker labels
        
    Returns:
        Dictionary with speaker statistics
    """
    agent_segments = [s for s in labeled_segments if s.get("speaker") == "Agent"]
    customer_segments = [s for s in labeled_segments if s.get("speaker") == "Customer"]
    
    agent_duration = sum(s["end"] - s["start"] for s in agent_segments)
    customer_duration = sum(s["end"] - s["start"] for s in customer_segments)
    
    agent_word_count = sum(len(s["text"].split()) for s in agent_segments)
    customer_word_count = sum(len(s["text"].split()) for s in customer_segments)
    
    return {
        "agent": {
            "segments": len(agent_segments),
            "duration_seconds": round(agent_duration, 2),
            "word_count": agent_word_count
        },
        "customer": {
            "segments": len(customer_segments),
            "duration_seconds": round(customer_duration, 2),
            "word_count": customer_word_count
        },
        "total_segments": len(labeled_segments),
        "total_duration": round(agent_duration + customer_duration, 2)
    }


def format_transcript_by_speaker(labeled_segments: List[Dict[str, any]]) -> str:
    """
    Format transcript with speaker labels for readability.
    
    Args:
        labeled_segments: List of segments with speaker labels
        
    Returns:
        Formatted transcript string
    """
    lines = []
    for segment in labeled_segments:
        speaker = segment.get("speaker", "Unknown")
        text = segment.get("text", "")
        start = segment.get("start", 0.0)
        lines.append(f"[{start:.1f}s] {speaker}: {text}")
    
    return "\n".join(lines)


def get_customer_only_transcript(labeled_segments: List[Dict[str, any]]) -> str:
    """
    Extract and format customer-only transcript.
    
    This filters out all agent segments and returns only what the customer said.
    This is important for analysis as issues, complaints, and tone should come
    only from the customer, not the agent.
    
    Args:
        labeled_segments: List of segments with speaker labels
        
    Returns:
        Customer-only transcript as a single string with line breaks between segments
        
    Example:
        Input segments with both Agent and Customer
        Output:
        "I haven't received my refund...
        The app keeps crashing..."
    """
    # Filter to only customer segments
    customer_segments = [
        seg for seg in labeled_segments 
        if seg.get("speaker") == "Customer"
    ]
    
    # Extract text from customer segments
    customer_texts = [
        seg.get("text", "").strip() 
        for seg in customer_segments 
        if seg.get("text", "").strip()
    ]
    
    # Join with line breaks for readability
    customer_transcript = "\n".join(customer_texts)
    
    return customer_transcript


def get_customer_segments(labeled_segments: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """
    Get only customer segments (useful for analysis).
    
    Args:
        labeled_segments: List of segments with speaker labels
        
    Returns:
        List of segments where speaker is "Customer"
    """
    return [
        seg for seg in labeled_segments 
        if seg.get("speaker") == "Customer"
    ]

