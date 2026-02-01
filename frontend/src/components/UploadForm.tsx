import { useRef, useState } from "react";

interface UploadFormProps {
    onUpload: (file: File) => void;
    isProcessing: boolean;
}

export default function UploadForm({ onUpload, isProcessing }: UploadFormProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [error, setError] = useState<string>("");
    const [isDragging, setIsDragging] = useState(false);

    const allowedTypes = [".mp3", ".wav", ".m4a"];

    const handleFileSelect = (file: File) => {
        const fileExt = "." + file.name.split(".").pop()?.toLowerCase();
        if (!allowedTypes.includes(fileExt)) {
            setError(`Invalid file type. Allowed: ${allowedTypes.join(", ")}`);
            setSelectedFile(null);
            return;
        }

        if (file.size > 25 * 1024 * 1024) {
            setError("File size exceeds 25 MB limit");
            setSelectedFile(null);
            return;
        }

        setError("");
        setSelectedFile(file);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            handleFileSelect(file);
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file) {
            handleFileSelect(file);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (selectedFile && !isProcessing) {
            onUpload(selectedFile);
        }
    };

    const handleReset = () => {
        setSelectedFile(null);
        setError("");
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    return (
        <form onSubmit={handleSubmit} className="w-full">
            <div className="mb-6">
                <label
                    htmlFor="audio-file"
                    className="block text-sm font-medium text-gray-700 mb-3"
                >
                    Upload Audio File
                </label>

                {/* Drag and Drop Area */}
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${isDragging
                        ? "border-gray-400 bg-gray-50"
                        : "border-gray-300 bg-gray-50/50 hover:border-gray-400"
                        } ${isProcessing ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                    onClick={() => !isProcessing && fileInputRef.current?.click()}
                >
                    <input
                        ref={fileInputRef}
                        id="audio-file"
                        type="file"
                        accept=".mp3,.wav,.m4a"
                        onChange={handleInputChange}
                        disabled={isProcessing}
                        className="hidden"
                    />

                    <div className="flex flex-col items-center gap-3">
                        <div className="p-3 bg-gray-100 rounded-lg">
                            <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-gray-700 mb-1">
                                {selectedFile ? selectedFile.name : "Click to upload or drag and drop"}
                            </p>
                            <p className="text-xs text-gray-500">
                                {selectedFile
                                    ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB`
                                    : "MP3, WAV, or M4A (Max 25 MB)"
                                }
                            </p>
                        </div>
                    </div>
                </div>

                {selectedFile && (
                    <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                            </svg>
                            <div>
                                <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                                <p className="text-xs text-gray-600">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                            </div>
                        </div>
                        <button
                            type="button"
                            onClick={(e) => {
                                e.stopPropagation();
                                handleReset();
                            }}
                            disabled={isProcessing}
                            className="p-1.5 text-gray-400 hover:text-red-600 transition-colors disabled:opacity-50"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                )}

                {error && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                        <svg className="w-4 h-4 text-red-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        <p className="text-xs text-red-700">{error}</p>
                    </div>
                )}
            </div>

            <button
                type="submit"
                disabled={!selectedFile || isProcessing}
                className="w-full px-4 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
                {isProcessing ? (
                    <>
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                        <span>Processing...</span>
                    </>
                ) : (
                    <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        <span>Process Call</span>
                    </>
                )}
            </button>
        </form>
    );
}
