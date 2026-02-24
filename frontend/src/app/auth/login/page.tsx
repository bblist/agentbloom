"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import Script from "next/script";
import { useRouter } from "next/navigation";
import { authAPI } from "@/lib/api";
import { dicebear } from "@/lib/dicebear";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [gsiReady, setGsiReady] = useState(false);

    const handleGoogleResponse = useCallback(
        async (response: { credential: string }) => {
            setLoading(true);
            setError("");
            try {
                const { data } = await authAPI.googleLogin({
                    credential: response.credential,
                });
                document.cookie = `auth_token=${data.token}; path=/; max-age=2592000`;
                router.push("/dashboard");
            } catch (err: unknown) {
                const message =
                    (err as { response?: { data?: { detail?: string } } })
                        .response?.data?.detail || "Google sign-in failed";
                setError(message);
            } finally {
                setLoading(false);
            }
        },
        [router]
    );

    useEffect(() => {
        if (!gsiReady || !GOOGLE_CLIENT_ID) return;
        const g = (window as unknown as Record<string, unknown>).google as {
            accounts: {
                id: {
                    initialize: (opts: Record<string, unknown>) => void;
                    renderButton: (
                        el: HTMLElement,
                        opts: Record<string, unknown>
                    ) => void;
                };
            };
        };
        if (!g?.accounts?.id) return;

        g.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleResponse,
        });

        const btnEl = document.getElementById("google-signin-btn");
        if (btnEl) {
            g.accounts.id.renderButton(btnEl, {
                theme: "outline",
                size: "large",
                width: "400",
                text: "signin_with",
                shape: "rectangular",
                logo_alignment: "left",
            });
        }
    }, [gsiReady, handleGoogleResponse]);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const { data } = await authAPI.login({ email, password });
            document.cookie = `auth_token=${data.token}; path=/; max-age=2592000`;
            router.push("/dashboard");
        } catch (err: unknown) {
            const message =
                (err as { response?: { data?: { non_field_errors?: string[]; detail?: string } } })
                    .response?.data?.non_field_errors?.[0] ||
                (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
                "Login failed";
            setError(message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <>
            <Script
                src="https://accounts.google.com/gsi/client"
                strategy="afterInteractive"
                onLoad={() => setGsiReady(true)}
            />
            <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-950 dark:to-gray-900">
                <div className="w-full max-w-md p-8 bg-white dark:bg-gray-900 rounded-2xl shadow-xl">
                    {/* Logo */}
                    <div className="text-center mb-8">
                        <Link href="/">
                            <div className="flex items-center justify-center gap-2 mb-2">
                                {/* eslint-disable-next-line @next/next/no-img-element */}
                                <img
                                    src={dicebear("bottts", "agentbloom-logo", { backgroundColor: ["b6e3f4"], radius: 50 })}
                                    alt=""
                                    className="w-10 h-10 rounded-xl"
                                />
                            </div>
                            <h1 className="text-3xl font-bold">
                                <span className="text-blue-600">Agent</span>
                                <span className="text-emerald-500">Bloom</span>
                            </h1>
                        </Link>
                        <p className="mt-2 text-gray-500">Sign in to your account</p>
                    </div>

                    {error && (
                        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
                            {error}
                        </div>
                    )}

                    {/* Google Sign-In Button */}
                    {GOOGLE_CLIENT_ID && (
                        <>
                            <div className="flex justify-center mb-4">
                                <div id="google-signin-btn" />
                            </div>

                            <div className="relative mb-4">
                                <div className="absolute inset-0 flex items-center">
                                    <div className="w-full border-t border-gray-200 dark:border-gray-700" />
                                </div>
                                <div className="relative flex justify-center text-sm">
                                    <span className="px-3 bg-white dark:bg-gray-900 text-gray-400">
                                        or sign in with email
                                    </span>
                                </div>
                            </div>
                        </>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium mb-1">
                                Email
                            </label>
                            <input
                                id="email"
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-700"
                                placeholder="you@example.com"
                            />
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium mb-1">
                                Password
                            </label>
                            <input
                                id="password"
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-700"
                                placeholder="••••••••"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
                        >
                            {loading ? "Signing in..." : "Sign In"}
                        </button>
                    </form>

                    <p className="mt-6 text-center text-sm text-gray-500">
                        Don&apos;t have an account?{" "}
                        <Link href="/auth/register" className="text-blue-600 hover:underline font-medium">
                            Sign up free
                        </Link>
                    </p>
                </div>
            </main>
        </>
    );
}
