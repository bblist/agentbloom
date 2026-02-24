"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const COOKIE_CONSENT_KEY = "agentbloom_cookie_consent";

export function CookieConsent() {
    const [show, setShow] = useState(false);

    useEffect(() => {
        const consent = localStorage.getItem(COOKIE_CONSENT_KEY);
        if (!consent) {
            // Small delay so it doesn't flash on page load
            const timer = setTimeout(() => setShow(true), 1000);
            return () => clearTimeout(timer);
        }
    }, []);

    const accept = () => {
        localStorage.setItem(COOKIE_CONSENT_KEY, "accepted");
        setShow(false);
    };

    const decline = () => {
        localStorage.setItem(COOKIE_CONSENT_KEY, "declined");
        setShow(false);
    };

    if (!show) return null;

    return (
        <div className="fixed bottom-0 left-0 right-0 z-50 p-4 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 shadow-lg">
            <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center gap-4">
                <p className="text-sm text-gray-600 dark:text-gray-400 flex-1">
                    We use cookies for authentication and to improve your experience.
                    See our{" "}
                    <Link href="/privacy" className="text-blue-600 hover:underline">
                        Privacy Policy
                    </Link>{" "}
                    for details.
                </p>
                <div className="flex gap-3 shrink-0">
                    <button
                        onClick={decline}
                        className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                        Decline
                    </button>
                    <button
                        onClick={accept}
                        className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Accept
                    </button>
                </div>
            </div>
        </div>
    );
}
