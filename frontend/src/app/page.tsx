import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-950 dark:to-gray-900">
      <div className="text-center max-w-3xl mx-auto px-6">
        {/* Logo / Brand */}
        <div className="mb-8">
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
            "AI Website Builder",
            "Email & CRM",
            "Online Courses",
            "Booking System",
            "Payment Processing",
            "SEO Optimization",
            "AI Receptionist",
          ].map((feature) => (
            <span
              key={feature}
              className="px-4 py-2 text-sm rounded-full bg-white/80 dark:bg-gray-800/80 border border-gray-200 dark:border-gray-700"
            >
              {feature}
            </span>
          ))}
        </div>
      </div>
    </main>
  );
}
