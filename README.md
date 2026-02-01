# Audio Call Analyzer

Audio call analysis application with FastAPI backend and React frontend.

## Project Structure

```
audio-call-analyzer/
├─ backend/
│  ├─ main.py
│  ├─ services/
│  │  ├─ audio.py          # Audio validation & temp storage
│  │  ├─ transcribe.py     # Whisper transcription service
│  │  ├─ diarize.py        # Speaker labeling (heuristic-based)
│  │  ├─ analysis.py       # LLM-based issues extraction & tone classification
│  ├─ schemas.py           # Pydantic models
│  ├─ requirements.txt
│  ├─ temp/                # Temporary audio files
│  └─ samples/             # Sample audio files for testing
├─ frontend/
│  ├─ src/
│  │  ├─ components/       # React components
│  │  │  ├─ UploadForm.tsx
│  │  │  ├─ TranscriptView.tsx
│  │  │  ├─ IssuesView.tsx
│  │  │  └─ ToneView.tsx
│  │  ├─ types.ts          # TypeScript types
│  │  ├─ App.tsx           # Main app component
│  │  └─ main.tsx
│  ├─ index.html
│  ├─ vite.config.ts
│  └─ package.json
└─ README.md
```

## Backend Setup

### Prerequisites

- Python 3.8+
- FFmpeg (required for audio conversion)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg` or `sudo yum install ffmpeg`
  - Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note**: On first run, Whisper will download the model (~150MB for base model). If you encounter SSL certificate errors:

1. **macOS**: Run `/Applications/Python\ 3.x/Install\ Certificates.command`
2. **Upgrade certifi**: `pip install --upgrade certifi`
3. **Development workaround** (not for production):
   ```bash
   export PYTHONHTTPSVERIFY=0
   ```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

### Run the Server

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at: http://127.0.0.1:8000

### Test the API

Visit: http://127.0.0.1:8000/docs (Swagger UI)

## Frontend Setup

### Prerequisites

- Node.js 18+ and npm

### Install Dependencies

```bash
cd frontend
npm install
```

### Run the Development Server

```bash
npm run dev
```

The frontend will be available at: http://localhost:5173

### Build for Production

```bash
npm run build
```

## Running the Full Application

1. **Start the backend** (in one terminal):
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open your browser**: http://localhost:5173

## API Response Format

The `/analyze` endpoint returns:

```json
{
  "transcript": [
    {
      "speaker": "Agent",
      "text": "Hello, how can I help you?",
      "start": 0.0,
      "end": 2.1
    },
    {
      "speaker": "Customer",
      "text": "I haven't received my refund",
      "start": 2.2,
      "end": 6.8
    }
  ],
  "issues": [
    {
      "title": "Refund delay",
      "details": "Refund not received in 10 days",
      "evidence": ["I still haven't got my refund"]
    }
  ],
  "tone": {
    "label": "Frustrated",
    "confidence": 0.76,
    "evidence": ["Repeated complaints", "Urgent wording"]
  }
}
```

## Features

### Backend Features

- **Audio Validation**: Max 25 MB, supports `.mp3`, `.wav`, `.m4a`
- **Audio Normalization**: Automatic conversion to WAV (16kHz, mono, PCM)
- **Speech Transcription**: OpenAI Whisper AI for accurate transcription
- **Speaker Labeling**: Heuristic-based speaker diarization (Agent vs Customer)
- **Issues Extraction**: LLM-powered extraction of customer issues with evidence
- **Tone Classification**: LLM-based classification of customer tone (Calm, Frustrated, Angry, Anxious)
- **CORS Enabled**: Backend allows all origins for frontend integration
- **Auto Cleanup**: Temporary files are automatically deleted after processing

### Frontend Features

- **Modern UI**: Clean, responsive design with Tailwind CSS
- **File Upload**: Drag-and-drop or click to upload audio files
- **Real-time Processing**: Loading states and progress indicators
- **Results Display**: Three clearly separated sections:
  - **Transcript**: Speaker-labeled, timestamped conversation
  - **Issues**: Structured list of customer issues with evidence
  - **Tone**: Visual tone classification with confidence score
- **Error Handling**: User-friendly error messages
- **TypeScript**: Fully typed for better developer experience

### API Endpoints

- **POST `/analyze`**: Upload and analyze audio file
  - Accepts: `.mp3`, `.wav`, `.m4a` files (max 25 MB)
  - Returns: Complete analysis with transcript, issues, and tone
  - Processing time: Typically 30-60 seconds depending on audio length

### Testing

**Using the Frontend:**
1. Start both backend and frontend (see "Running the Full Application" above)
2. Open http://localhost:5173
3. Upload an audio file and click "Process Call"

**Using the API directly:**
1. Test using the Swagger UI at http://127.0.0.1:8000/docs
2. Or use curl:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@backend/samples/1.mp3"
```

**Using the test script:**
```bash
cd backend
python3 test_transcribe.py samples/1.mp3
```

## Notes

- **Speaker Labeling**: The current implementation uses heuristic-based speaker labeling. For production use, consider integrating a proper speaker diarization service (e.g., pyannote.audio) for better accuracy.
- **CORS**: The backend is configured to allow all origins (`*`). For production, restrict this to specific domains.
- **OpenAI API**: Requires a valid OpenAI API key for issues extraction and tone classification. The key should be set in `backend/.env`.

