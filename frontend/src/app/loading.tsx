export default function Loading() {
    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-950">
            <div className="text-center">
                <div className="inline-flex items-center gap-2">
                    <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.3s]" />
                    <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.15s]" />
                    <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce" />
                </div>
                <p className="mt-4 text-sm text-gray-500">Loading...</p>
            </div>
        </div>
    );
}
