import type { TranscriptSegment } from "../types";

interface TranscriptViewProps {
    transcript: TranscriptSegment[];
}

export default function TranscriptView({ transcript }: TranscriptViewProps) {
    if (transcript.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
                <svg className="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
                <p className="text-xs text-gray-500 font-medium">No transcript available</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-4">
                <div className="p-1.5 rounded bg-blue-50 border border-blue-200">
                    <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                    </svg>
                </div>
                <h2 className="text-base font-semibold text-gray-900">Transcript</h2>
                <span className="ml-auto px-2 py-0.5 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full">
                    {transcript.length} segments
                </span>
            </div>

            <div className="bg-gray-50 rounded-lg border border-gray-200 p-3 max-h-[500px] overflow-y-auto custom-scrollbar">
                <div className="space-y-2.5">
                    {transcript.map((segment, index) => {
                        const isAgent = segment.speaker === "Agent";
                        const duration = (segment.end - segment.start).toFixed(1);
                        const bgColor = isAgent ? "bg-blue-50" : "bg-orange-50";
                        const textColor = isAgent ? "text-blue-700" : "text-orange-700";
                        const badgeBg = isAgent ? "bg-blue-100" : "bg-orange-100";

                        return (
                            <div
                                key={index}
                                className={`${bgColor} rounded-lg border border-gray-200 p-3`}
                            >
                                <div className="flex items-start justify-between gap-3 mb-1.5">
                                    <div className="flex items-center gap-1.5">
                                        <span className={`px-1.5 py-0.5 rounded ${badgeBg} ${textColor} text-xs font-semibold`}>
                                            {segment.speaker}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-1 text-xs text-gray-500">
                                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        <span className="font-mono text-xs">
                                            {segment.start.toFixed(1)}s - {segment.end.toFixed(1)}s
                                        </span>
                                        <span className="text-gray-400">•</span>
                                        <span className="text-xs">{duration}s</span>
                                    </div>
                                </div>
                                <p className="text-xs text-gray-800 leading-relaxed">
                                    {segment.text}
                                </p>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
