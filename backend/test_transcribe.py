#!/usr/bin/env python3
"""
Test script for transcription service.
Tests Whisper transcription directly without going through the API.

Usage:
    python test_transcribe.py [audio_file_path]
    
Example:
    python test_transcribe.py samples/1.mp3
    python test_transcribe.py samples/2.mp3
"""

import sys
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from services.transcribe import transcribe_audio, get_full_transcript
from services.diarize import label_speakers, get_speaker_statistics, format_transcript_by_speaker, get_customer_only_transcript
from services.analysis import extract_issues, format_issues_for_display, classify_tone
import ffmpeg


def print_separator():
    """Print a visual separator."""
    print("=" * 80)


def print_segment(segment, index):
    """Print a single transcript segment."""
    start = segment["start"]
    end = segment["end"]
    text = segment["text"]
    duration = end - start
    
    print(f"\n[{index}] {start:.2f}s - {end:.2f}s ({duration:.2f}s)")
    print(f"    {text}")


def test_transcription(audio_path: Path, model_name: str = "base"):
    """
    Test transcription on an audio file.
    
    Args:
        audio_path: Path to audio file
        model_name: Whisper model to use
    """
    print_separator()
    print(f"Testing Transcription Service")
    print_separator()
    print(f"Audio file: {audio_path}")
    print(f"Model: {model_name}")
    print(f"File exists: {audio_path.exists()}")
    
    if not audio_path.exists():
        print(f"\n❌ Error: File not found: {audio_path}")
        return False
    
    # Check file size
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")
    print_separator()
    
    # For non-WAV files, we need to convert first
    should_cleanup = False
    wav_path = None
    
    if audio_path.suffix.lower() != ".wav":
        print(f"\n⚠️  File is {audio_path.suffix}, converting to WAV first...")
        try:
            # Create temp WAV file
            temp_dir = Path(__file__).parent / "temp"
            temp_dir.mkdir(exist_ok=True)
            wav_path = temp_dir / f"{uuid.uuid4()}.wav"
            
            # Convert using ffmpeg
            stream = ffmpeg.input(str(audio_path))
            stream = ffmpeg.output(stream, str(wav_path), acodec='pcm_s16le', ac=1, ar='16000')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"✅ Converted to: {wav_path}")
            audio_path = wav_path
            should_cleanup = True
        except Exception as e:
            print(f"❌ Conversion error: {str(e)}")
            print("   Make sure ffmpeg is installed and the file is a valid audio file.")
            return False
    
    print_separator()
    print("\n🔄 Starting transcription...")
    print("   (This may take a while on first run - model needs to download)")
    print()
    
    try:
        # Transcribe
        segments = transcribe_audio(audio_path, model_name)
        
        # Get full transcript
        full_transcript = get_full_transcript(segments)
        
        # Label speakers (heuristic-based)
        print("\n🔍 Labeling speakers (heuristic-based)...")
        labeled_segments = label_speakers(segments)
        speaker_stats = get_speaker_statistics(labeled_segments)
        
        # Print results
        print_separator()
        print("✅ TRANSCRIPTION SUCCESSFUL")
        print_separator()
        print(f"\n📊 Summary:")
        print(f"   Total segments: {len(segments)}")
        if segments:
            total_duration = segments[-1]["end"]
            print(f"   Total duration: {total_duration:.2f} seconds")
        
        print(f"\n👥 Speaker Statistics:")
        print(f"   Agent: {speaker_stats['agent']['segments']} segments, "
              f"{speaker_stats['agent']['duration_seconds']}s, "
              f"{speaker_stats['agent']['word_count']} words")
        print(f"   Customer: {speaker_stats['customer']['segments']} segments, "
              f"{speaker_stats['customer']['duration_seconds']}s, "
              f"{speaker_stats['customer']['word_count']} words")
        
        print_separator()
        print("\n📝 Transcript Segments (with Speaker Labels):")
        print_separator()
        
        for i, segment in enumerate(labeled_segments, 1):
            speaker = segment.get("speaker", "Unknown")
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            duration = end - start
            
            print(f"\n[{i}] {speaker} | {start:.2f}s - {end:.2f}s ({duration:.2f}s)")
            print(f"    {text}")
        
        print_separator()
        print("\n📄 Full Transcript (by Speaker):")
        print_separator()
        print(format_transcript_by_speaker(labeled_segments))
        print_separator()
        
        print("\n📄 Full Transcript (plain):")
        print_separator()
        print(full_transcript)
        print_separator()
        
        # Get customer-only transcript
        customer_only = get_customer_only_transcript(labeled_segments)
        
        print("\n👤 Customer-Only Transcript (for LLM analysis):")
        print_separator()
        if customer_only:
            print("Customer said:")
            print(customer_only)
        else:
            print("(No customer segments found)")
        print_separator()
        
        # Extract issues using LLM (if customer transcript exists)
        issues = []
        if customer_only:
            print("\n🤖 Extracting issues using LLM...")
            print("   (This requires OPENAI_API_KEY environment variable)")
            try:
                issues = extract_issues(customer_only)
                print(f"   ✅ Extracted {len(issues)} issue(s)")
            except ValueError as e:
                print(f"   ⚠️  {str(e)}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        if issues:
            print_separator()
            print("\n🔍 Extracted Issues:")
            print_separator()
            print(format_issues_for_display(issues))
            print_separator()
        
        # Classify tone using LLM
        tone = {
            "label": "Calm",
            "confidence": 0.5,
            "evidence": []
        }
        if customer_only:
            print("\n🎭 Classifying tone using LLM...")
            try:
                tone = classify_tone(customer_only)
                print(f"   ✅ Tone classified: {tone['label']} (confidence: {tone['confidence']})")
            except ValueError as e:
                print(f"   ⚠️  {str(e)}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        if tone and (tone.get("label") != "Calm" or tone.get("confidence", 0) > 0.5):
            print_separator()
            print("\n🎭 Tone Classification:")
            print_separator()
            print(f"Label: {tone.get('label', 'Unknown')}")
            print(f"Confidence: {tone.get('confidence', 0.0):.2f}")
            evidence = tone.get('evidence', [])
            if evidence:
                print("Evidence:")
                for item in evidence:
                    print(f"  - {item}")
            print_separator()
        
        # Print JSON output
        print("\n📋 JSON Output (Complete Analysis):")
        print_separator()
        output = {
            "segments": labeled_segments,
            "full_transcript": full_transcript,
            "customer_only_transcript": customer_only,
            "issues": issues,
            "tone": tone,
            "segment_count": len(segments),
            "speaker_statistics": speaker_stats,
            "note": "⚠️ Speaker labels are heuristic-based and may not be accurate"
        }
        print(json.dumps(output, indent=2))
        print_separator()
        
        # Cleanup
        if should_cleanup and wav_path and wav_path.exists():
            try:
                wav_path.unlink()
                print(f"\n🧹 Cleaned up temporary file: {wav_path}")
            except Exception as e:
                print(f"\n⚠️  Warning: Could not delete temp file: {e}")
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print_separator()
        print("❌ TRANSCRIPTION FAILED")
        print_separator()
        print(f"\nError: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Cleanup on error
        if should_cleanup and wav_path and wav_path.exists():
            try:
                wav_path.unlink()
            except Exception:
                pass  # Best effort cleanup
        
        return False


def main():
    """Main function."""
    # Default to first sample file if no argument provided
    if len(sys.argv) > 1:
        audio_path = Path(sys.argv[1])
    else:
        # Try to find a sample file
        samples_dir = Path(__file__).parent / "samples"
        sample_files = list(samples_dir.glob("*.mp3")) + list(samples_dir.glob("*.wav")) + list(samples_dir.glob("*.m4a"))
        
        if sample_files:
            audio_path = sample_files[0]
            print(f"ℹ️  No file specified, using: {audio_path}")
        else:
            print("❌ Error: No audio file specified and no sample files found.")
            print("\nUsage: python test_transcribe.py [audio_file_path]")
            print("Example: python test_transcribe.py samples/1.mp3")
            sys.exit(1)
    
    # Make path absolute if relative
    if not audio_path.is_absolute():
        audio_path = Path(__file__).parent / audio_path
    
    # Optional: specify model (default is "base")
    model_name = sys.argv[2] if len(sys.argv) > 2 else "base"
    
    # Run test
    success = test_transcription(audio_path, model_name)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

