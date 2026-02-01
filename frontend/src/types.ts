// TypeScript types matching the backend API response

export interface TranscriptSegment {
  speaker: "Agent" | "Customer";
  text: string;
  start: number;
  end: number;
}

export interface Issue {
  title: string;
  details: string;
  evidence: string[];
}

export interface Tone {
  label: "Calm" | "Frustrated" | "Angry" | "Anxious";
  confidence: number;
  evidence: string[];
}

export interface SpeakerStatistics {
  agent: {
    segments: number;
    duration_seconds: number;
    word_count: number;
  };
  customer: {
    segments: number;
    duration_seconds: number;
    word_count: number;
  };
  total_segments: number;
  total_duration: number;
}

export interface Metadata {
  filename: string;
  file_size_mb: number;
  processing_time_seconds: number;
  request_id: string;
  timestamp: string;
  segment_count: number;
  speaker_statistics: SpeakerStatistics;
}

export interface AnalysisResponse {
  transcript: TranscriptSegment[];
  issues: Issue[];
  tone: Tone;
  metadata?: Metadata;
}

export type ProcessingState = "idle" | "uploading" | "processing" | "success" | "error";
