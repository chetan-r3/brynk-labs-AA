import { useState } from "react";
import UploadForm from "./components/UploadForm";
import TranscriptView from "./components/TranscriptView";
import IssuesView from "./components/IssuesView";
import ToneView from "./components/ToneView";
import StatsCards from "./components/StatsCards";
import type { AnalysisResponse, ProcessingState } from "./types";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [state, setState] = useState<ProcessingState>("idle");
  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [uploadedFileName, setUploadedFileName] = useState<string>("");

  const handleUpload = async (file: File) => {
    setState("uploading");
    setError("");
    setData(null);
    setUploadedFileName(file.name);

    try {
      const formData = new FormData();
      formData.append("file", file);

      setState("processing");

      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result: AnalysisResponse = await response.json();
      setData(result);
      setState("success");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to process audio";
      setError(errorMessage);
      setState("error");
      console.error("Error processing audio:", err);
    }
  };

  const handleReset = () => {
    setState("idle");
    setData(null);
    setError("");
    setUploadedFileName("");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 max-w-7xl">
        {/* Header */}
        <header className="mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-xl sm:text-2xl font-semibold text-gray-900 mb-1">
                Audio Call Analyzer
              </h1>
              <p className="text-xs text-gray-500">
                Upload an audio file to analyze customer service calls
              </p>
            </div>
            {state === "success" && (
              <button
                onClick={handleReset}
                className="px-3 py-1.5 text-xs font-medium text-white bg-gray-900 rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Analyze Another
              </button>
            )}
          </div>
        </header>

        {/* Upload Form */}
        {state === "idle" || state === "error" ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <UploadForm onUpload={handleUpload} isProcessing={false} />
            {error && (
              <div className="mt-4 p-3 bg-red-50 border-l-4 border-red-500 rounded-r-lg">
                <div className="flex items-start gap-2">
                  <svg className="w-4 h-4 text-red-500 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-red-800">Error</p>
                    <p className="text-xs text-red-600 mt-0.5">{error}</p>
                    <button
                      onClick={handleReset}
                      className="mt-2 text-xs text-red-700 hover:text-red-900 font-medium underline"
                    >
                      Try again
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : null}

        {/* Loading State */}
        {state === "uploading" || state === "processing" ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <div className="inline-block relative">
              <div className="animate-spin rounded-full h-10 w-10 border-2 border-gray-200 border-t-gray-900 mb-3"></div>
            </div>
            <p className="text-xs font-medium text-gray-800 mb-1">
              {state === "uploading" ? "Uploading file..." : "Processing audio..."}
            </p>
            <p className="text-xs text-gray-500">
              This may take a minute. Please wait.
            </p>
          </div>
        ) : null}

        {/* Dashboard Results */}
        {state === "success" && data && (
          <div className="space-y-5">
            {/* File Info Header */}
            {data.metadata && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                    </svg>
                    <div>
                      <p className="text-xs font-semibold text-gray-900">{data.metadata.filename || uploadedFileName}</p>
                      <p className="text-xs text-gray-500">Processed {new Date(data.metadata.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    Request ID: <span className="font-mono">{data.metadata.request_id.slice(0, 8)}...</span>
                  </div>
                </div>
              </div>
            )}

            {/* Stats Cards */}
            {data.metadata && (
              <StatsCards metadata={data.metadata} />
            )}

            {/* Tone & Issues Side by Side */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <ToneView tone={data.tone} />
              <IssuesView issues={data.issues} />
            </div>

            {/* Transcript Section */}
            <TranscriptView transcript={data.transcript} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
