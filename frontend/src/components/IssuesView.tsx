import type { Issue } from "../types";

interface IssuesViewProps {
    issues: Issue[];
}

export default function IssuesView({ issues }: IssuesViewProps) {
    if (issues.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 flex items-center justify-center min-h-[300px]">
                <div className="text-center">
                    <svg className="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-xs text-gray-500 font-medium">No issues found</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-4">
                <div className="p-1.5 rounded bg-orange-50 border border-orange-200">
                    <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                </div>
                <h2 className="text-base font-semibold text-gray-900">Issues</h2>
                <span className="ml-auto px-2 py-0.5 bg-orange-100 text-orange-700 text-xs font-semibold rounded-full">
                    {issues.length}
                </span>
            </div>

            {/* Horizontal scrollable issues */}
            <div className="overflow-x-auto -mx-5 px-5">
                <div className="flex gap-4 min-w-max pb-2">
                    {issues.map((issue, index) => (
                        <div
                            key={index}
                            className="bg-gray-50 rounded-lg border border-gray-200 p-4 min-w-[280px] max-w-[320px] shrink-0"
                        >
                            <div className="flex items-start gap-2 mb-3">
                                <div className="shrink-0 w-6 h-6 rounded-full bg-orange-500 flex items-center justify-center text-white text-xs font-bold">
                                    {index + 1}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h3 className="text-sm font-semibold text-gray-900 mb-1.5 leading-tight">
                                        {issue.title}
                                    </h3>
                                    <p className="text-xs text-gray-600 leading-relaxed mb-3">
                                        {issue.details}
                                    </p>
                                </div>
                            </div>

                            {issue.evidence && issue.evidence.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-gray-200">
                                    <p className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">Evidence</p>
                                    {/* Evidence in flex-col (vertical) */}
                                    <div className="flex flex-col gap-2">
                                        {issue.evidence.map((quote, idx) => (
                                            <div key={idx} className="text-xs text-gray-600 bg-white rounded border border-gray-200 p-2.5">
                                                <span className="text-orange-500">"</span>
                                                <span className="italic">{quote}</span>
                                                <span className="text-orange-500">"</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
