import type { Metadata } from "../types";

interface StatsCardsProps {
    metadata: Metadata;
}

export default function StatsCards({ metadata }: StatsCardsProps) {
    const stats = [
        {
            label: "File Size",
            value: `${metadata.file_size_mb.toFixed(2)} MB`,
            icon: (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
            ),
        },
        {
            label: "Processing Time",
            value: `${metadata.processing_time_seconds}s`,
            icon: (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            ),
        },
        {
            label: "Total Segments",
            value: metadata.segment_count.toString(),
            icon: (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
            ),
        },
        {
            label: "Agent Segments",
            value: metadata.speaker_statistics.agent.segments.toString(),
            icon: (
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clipRule="evenodd" />
                </svg>
            ),
        },
        {
            label: "Customer Segments",
            value: metadata.speaker_statistics.customer.segments.toString(),
            icon: (
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
            ),
        },
        {
            label: "Total Duration",
            value: `${Math.round(metadata.speaker_statistics.total_duration)}s`,
            icon: (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            ),
        },
    ];

    return (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {stats.map((stat, index) => (
                <div
                    key={index}
                    className="bg-white rounded-lg border border-gray-200 p-3 shadow-sm"
                >
                    <div className="flex items-center gap-2 mb-1.5">
                        <div className="text-gray-500">{stat.icon}</div>
                        <p className="text-xs text-gray-500 font-medium">{stat.label}</p>
                    </div>
                    <p className="text-base font-semibold text-gray-900">{stat.value}</p>
                </div>
            ))}
        </div>
    );
}

