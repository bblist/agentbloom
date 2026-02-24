"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authAPI } from "@/lib/api";
import { dicebear } from "@/lib/dicebear";

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

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
    );
}
