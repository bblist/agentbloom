import Link from "next/link";
import { dicebear } from "@/lib/dicebear";

export default function HomePage() {
    return (
        <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-950 dark:to-gray-900">
            <div className="text-center max-w-3xl mx-auto px-6">
                {/* Logo / Brand */}
                <div className="mb-8">
                    <div className="flex items-center justify-center gap-3 mb-3">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                            src={dicebear("bottts", "agentbloom-hero", { backgroundColor: ["b6e3f4", "c0aede"], backgroundType: "gradientLinear", radius: 50 })}
                            alt="AgentBloom"
                            className="w-16 h-16 rounded-2xl shadow-lg"
                        />
                    </div>
                    <h1 className="text-6xl font-bold tracking-tight">
                        <span className="text-blue-600 dark:text-blue-400">Agent</span>
                        <span className="text-emerald-500">Bloom</span>
                    </h1>
                    <p className="mt-3 text-xl text-muted-foreground" style={{ color: "var(--muted-foreground)" }}>
                        Speak it. Build it. Bloom.
                    </p>
                </div>

                {/* Description */}
                <p className="text-lg mb-10" style={{ color: "var(--muted-foreground)" }}>
                    Tell our AI agent what your business needs — websites, email campaigns,
                    courses, bookings, CRM — and watch it all come to life.
                </p>

                {/* CTA Buttons */}
                <div className="flex gap-4 justify-center">
                    <Link
                        href="/auth/register"
                        className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg"
                    >
                        Get Started Free
                    </Link>
                    <Link
                        href="/auth/login"
                        className="px-8 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-semibold hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                    >
                        Sign In
                    </Link>
                </div>

                {/* Feature Pills */}
                <div className="mt-16 flex flex-wrap gap-3 justify-center">
                    {[
                        { name: "AI Website Builder", seed: "feature-ai-builder" },
                        { name: "Email & CRM", seed: "feature-email-crm" },
                        { name: "Online Courses", seed: "feature-courses" },
                        { name: "Booking System", seed: "feature-bookings" },
                        { name: "Payment Processing", seed: "feature-payments" },
                        { name: "SEO Optimization", seed: "feature-seo" },
                        { name: "AI Receptionist", seed: "feature-receptionist" },
                    ].map((feature) => (
                        <span
                            key={feature.name}
                            className="px-4 py-2 text-sm rounded-full bg-white/80 dark:bg-gray-800/80 border border-gray-200 dark:border-gray-700 flex items-center gap-2"
                        >
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img src={dicebear("shapes", feature.seed, { size: 20 })} alt="" className="w-5 h-5 rounded" />
                            {feature.name}
                        </span>
                    ))}
                </div>
            </div>
        </main>
    );
}
