import Link from "next/link";

export default function NotFound() {
    return (
        <main className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
            <div className="text-center px-6">
                <h1 className="text-8xl font-bold text-blue-600 dark:text-blue-400">404</h1>
                <h2 className="mt-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">
                    Page Not Found
                </h2>
                <p className="mt-2 text-gray-500 max-w-md mx-auto">
                    The page you&apos;re looking for doesn&apos;t exist or has been moved.
                </p>
                <div className="mt-8 flex gap-4 justify-center">
                    <Link
                        href="/"
                        className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                    >
                        Go Home
                    </Link>
                    <Link
                        href="/dashboard"
                        className="px-6 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                        Dashboard
                    </Link>
                </div>
            </div>
        </main>
    );
}
