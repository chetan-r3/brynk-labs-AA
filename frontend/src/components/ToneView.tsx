import type { Tone } from "../types";

interface ToneViewProps {
    tone: Tone;
}

const toneConfig: Record<Tone["label"], {
    bg: string;
    text: string;
    border: string;
    progress: string;
}> = {
    Calm: {
        bg: "bg-green-50",
        text: "text-green-700",
        border: "border-green-200",
        progress: "bg-green-500",
    },
    Frustrated: {
        bg: "bg-yellow-50",
        text: "text-yellow-700",
        border: "border-yellow-200",
        progress: "bg-yellow-500",
    },
    Angry: {
        bg: "bg-red-50",
        text: "text-red-700",
        border: "border-red-200",
        progress: "bg-red-500",
    },
    Anxious: {
        bg: "bg-purple-50",
        text: "text-purple-700",
        border: "border-purple-200",
        progress: "bg-purple-500",
    },
};

export default function ToneView({ tone }: ToneViewProps) {
    const confidencePercent = Math.round(tone.confidence * 100);
    const config = toneConfig[tone.label] || toneConfig.Calm;

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-4">
                <div className={`p-1.5 rounded ${config.bg} border ${config.border}`}>
                    <svg className={`w-4 h-4 ${config.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                    </svg>
                </div>
                <h2 className="text-base font-semibold text-gray-900">Tone Analysis</h2>
            </div>

            <div className="space-y-4">
                {/* Tone Label & Confidence */}
                <div className="space-y-2.5">
                    <div className="flex items-center justify-between">
                        <span className={`px-2.5 py-1 rounded border ${config.border} font-semibold ${config.text} text-xs`}>
                            {tone.label}
                        </span>
                        <span className="text-lg font-semibold text-gray-900">
                            {confidencePercent}%
                        </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>Confidence</span>
                            <span className="font-medium">{confidencePercent}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                            <div
                                className={`h-full ${config.progress} rounded-full transition-all duration-500`}
                                style={{ width: `${confidencePercent}%` }}
                            />
                        </div>
                    </div>
                </div>

                {/* Reasoning */}
                {tone.evidence && tone.evidence.length > 0 && (
                    <div className="pt-3 border-t border-gray-200">
                        <p className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">Reasoning</p>
                        <div className="flex flex-col gap-1.5">
                            {tone.evidence.map((item, idx) => (
                                <div key={idx} className="flex items-start gap-1.5 text-xs text-gray-600">
                                    <span className={`mt-0.5 w-1 h-1 rounded-full ${config.progress} shrink-0`}></span>
                                    <span className="leading-relaxed">{item}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
