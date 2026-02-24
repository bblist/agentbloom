"use client";

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    return (
        <html lang="en">
            <body>
                <main className="min-h-screen flex items-center justify-center bg-gray-50">
                    <div className="text-center px-6">
                        <h1 className="text-6xl font-bold text-red-500">500</h1>
                        <h2 className="mt-4 text-2xl font-semibold text-gray-900">
                            Something went wrong
                        </h2>
                        <p className="mt-2 text-gray-500 max-w-md mx-auto">
                            An unexpected error occurred. Our team has been notified.
                        </p>
                        {error.digest && (
                            <p className="mt-1 text-xs text-gray-400">
                                Error ID: {error.digest}
                            </p>
                        )}
                        <button
                            onClick={reset}
                            className="mt-8 px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                        >
                            Try Again
                        </button>
                    </div>
                </main>
            </body>
        </html>
    );
}
