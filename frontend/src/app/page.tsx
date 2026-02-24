import Link from "next/link";

/* ─────────────────────── Static Data ─────────────────────── */

const FEATURES = [
    {
        title: "AI Website Builder",
        desc: "Describe your vision in plain English and watch a stunning, mobile-optimised website materialise in seconds. Drag-and-drop editing, 50+ block types, custom domains, and one-click publishing.",
        color: "from-blue-500 to-indigo-600",
        stat: "< 60 s",
        statLabel: "avg build time",
    },
    {
        title: "Email & CRM",
        desc: "Manage every lead, deal, and campaign from one inbox. Visual pipeline boards, automated follow-ups, segmented email blasts, and real-time open/click analytics.",
        color: "from-emerald-500 to-teal-600",
        stat: "3.2×",
        statLabel: "higher reply rate",
    },
    {
        title: "Online Courses",
        desc: "Create, host, and sell courses with a built-in LMS. Drip content, quizzes, certificates, community spaces, and Stripe-powered checkout — all included.",
        color: "from-violet-500 to-purple-600",
        stat: "∞",
        statLabel: "students",
    },
    {
        title: "Booking System",
        desc: "Let clients self-book appointments 24/7. Google Calendar sync, buffer times, payment collection, automated reminders, and timezone-aware scheduling.",
        color: "from-amber-500 to-orange-600",
        stat: "0",
        statLabel: "no-shows",
    },
    {
        title: "Payment Processing",
        desc: "Accept one-time and recurring payments via Stripe. Invoices, checkout pages, subscription management, coupon codes, and detailed revenue dashboards.",
        color: "from-pink-500 to-rose-600",
        stat: "140+",
        statLabel: "currencies",
    },
    {
        title: "SEO Optimisation",
        desc: "Automated meta tags, sitemaps, structured data, Core Web Vitals monitoring, and keyword tracking. Rank higher without lifting a finger.",
        color: "from-cyan-500 to-sky-600",
        stat: "Top 10",
        statLabel: "rankings",
    },
    {
        title: "AI Receptionist",
        desc: "A 24/7 virtual front-desk that greets visitors, answers FAQs, qualifies leads, books appointments, and hands off to your team — all via a chat widget on your site.",
        color: "from-fuchsia-500 to-pink-600",
        stat: "24/7",
        statLabel: "availability",
    },
];

const SHOWCASE = [
    {
        title: "Bloom Fitness Studio",
        niche: "Fitness & Wellness",
        desc: "A high-energy landing page for a boutique fitness studio with class bookings, trainer profiles, and membership plans.",
        href: "/examples/fitness",
        gradient: "from-orange-400 to-rose-500",
    },
    {
        title: "Prestige Realty Group",
        niche: "Real Estate",
        desc: "A sophisticated property listing site with virtual tour embeds, mortgage calculator, and agent booking system.",
        href: "/examples/realestate",
        gradient: "from-sky-400 to-indigo-500",
    },
    {
        title: "The Artisan Kitchen",
        niche: "Restaurant",
        desc: "A mouth-watering restaurant page with an interactive menu, reservation system, and Instagram-style food gallery.",
        href: "/examples/restaurant",
        gradient: "from-amber-400 to-orange-500",
    },
    {
        title: "Dr. Sarah Chen, DDS",
        niche: "Dental / Healthcare",
        desc: "A trust-building dental practice page with service cards, patient testimonials, insurance info, and online booking.",
        href: "/examples/dental",
        gradient: "from-teal-400 to-emerald-500",
    },
];

const STEPS = [
    { num: "01", title: "Describe Your Business", desc: "Tell our AI what you do, who you serve, and the vibe you want. That's it." },
    { num: "02", title: "Review & Customise", desc: "Your site, CRM, courses, and automations appear instantly. Tweak anything with drag-and-drop." },
    { num: "03", title: "Go Live & Grow", desc: "Hit publish. Your AI receptionist starts greeting visitors and booking appointments on day one." },
];

const TESTIMONIALS = [
    { name: "Maria G.", role: "Yoga Instructor", quote: "I went from zero online presence to a fully booked calendar in one afternoon. AgentBloom is magic." },
    { name: "James T.", role: "Real Estate Agent", quote: "My old site cost $5k and took 3 months. AgentBloom built something better in under a minute." },
    { name: "Dr. Priya S.", role: "Dentist", quote: "The AI receptionist handles 80% of patient questions. My front desk team can finally focus on care." },
    { name: "Alex R.", role: "Course Creator", quote: "I launched my first online course and made $12k in the first month. The built-in LMS is incredible." },
];

/* ─────────────────── Page Component ──────────────────────── */

export default function HomePage() {
    return (
        <main className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">

            {/* ═══════════════ NAV ═══════════════ */}
            <nav className="fixed top-0 inset-x-0 z-50 bg-white/80 dark:bg-gray-950/80 backdrop-blur-lg border-b border-gray-100 dark:border-gray-800">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-2">
                        <span className="text-2xl font-bold">
                            <span className="text-blue-600">Agent</span>
                            <span className="text-emerald-500">Bloom</span>
                        </span>
                    </Link>
                    <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600 dark:text-gray-400">
                        <a href="#features" className="hover:text-gray-900 dark:hover:text-white transition-colors">Features</a>
                        <a href="#how-it-works" className="hover:text-gray-900 dark:hover:text-white transition-colors">How It Works</a>
                        <a href="#examples" className="hover:text-gray-900 dark:hover:text-white transition-colors">Examples</a>
                        <a href="#receptionist" className="hover:text-gray-900 dark:hover:text-white transition-colors">AI Receptionist</a>
                    </div>
                    <div className="flex items-center gap-3">
                        <Link href="/auth/login" className="text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                            Sign In
                        </Link>
                        <Link href="/auth/register" className="px-5 py-2 text-sm font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm">
                            Get Started Free
                        </Link>
                    </div>
                </div>
            </nav>

            {/* ═══════════════ HERO ═══════════════ */}
            <section className="pt-32 pb-20 sm:pt-40 sm:pb-28 relative overflow-hidden">
                {/* Gradient blobs */}
                <div className="absolute top-20 -left-32 w-96 h-96 bg-blue-200/40 dark:bg-blue-900/20 rounded-full blur-3xl" />
                <div className="absolute top-40 -right-32 w-96 h-96 bg-emerald-200/40 dark:bg-emerald-900/20 rounded-full blur-3xl" />

                <div className="relative max-w-5xl mx-auto px-4 sm:px-6 text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm font-medium mb-8 border border-blue-100 dark:border-blue-800">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                        </span>
                        Now in Public Beta — Free to use
                    </div>

                    <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight leading-[1.1]">
                        Build Your Entire Business{" "}
                        <span className="bg-gradient-to-r from-blue-600 via-indigo-500 to-emerald-500 bg-clip-text text-transparent">
                            With One Conversation
                        </span>
                    </h1>

                    <p className="mt-6 text-lg sm:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed">
                        Tell our AI what your business needs — a website, CRM, email campaigns,
                        online courses, appointment booking, payments — and watch everything
                        come to life in seconds. No code. No designers. No hassle.
                    </p>

                    <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
                        <Link
                            href="/auth/register"
                            className="px-8 py-3.5 bg-blue-600 text-white rounded-xl font-semibold text-lg hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/25 hover:shadow-xl hover:shadow-blue-600/30 hover:-translate-y-0.5"
                        >
                            Start Building — It&apos;s Free
                        </Link>
                        <a
                            href="#examples"
                            className="px-8 py-3.5 border border-gray-200 dark:border-gray-700 rounded-xl font-semibold text-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-all"
                        >
                            See Examples
                        </a>
                    </div>

                    {/* Feature pills — NO icons */}
                    <div className="mt-14 flex flex-wrap gap-2.5 justify-center">
                        {["AI Website Builder", "Email & CRM", "Online Courses", "Booking System", "Payment Processing", "SEO Optimisation", "AI Receptionist"].map((f) => (
                            <span
                                key={f}
                                className="px-4 py-2 text-sm rounded-full bg-gray-50 dark:bg-gray-800/60 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 font-medium"
                            >
                                {f}
                            </span>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════ SOCIAL PROOF BAR ═══════════════ */}
            <section className="py-10 border-y border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50">
                <div className="max-w-5xl mx-auto px-4 sm:px-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                        <div>
                            <p className="text-3xl font-bold text-blue-600">10k+</p>
                            <p className="text-sm text-gray-500 mt-1">Businesses Launched</p>
                        </div>
                        <div>
                            <p className="text-3xl font-bold text-emerald-500">50k+</p>
                            <p className="text-sm text-gray-500 mt-1">Pages Created</p>
                        </div>
                        <div>
                            <p className="text-3xl font-bold text-violet-500">2M+</p>
                            <p className="text-sm text-gray-500 mt-1">Emails Sent</p>
                        </div>
                        <div>
                            <p className="text-3xl font-bold text-amber-500">99.9%</p>
                            <p className="text-sm text-gray-500 mt-1">Uptime</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* ═══════════════ FEATURES ═══════════════ */}
            <section id="features" className="py-24 sm:py-32">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl sm:text-5xl font-bold tracking-tight">
                            Everything You Need.{" "}
                            <span className="bg-gradient-to-r from-blue-600 to-emerald-500 bg-clip-text text-transparent">
                                Nothing You Don&apos;t.
                            </span>
                        </h2>
                        <p className="mt-4 text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                            Seven powerful tools, one platform, zero complexity. Each feature is designed
                            to work seamlessly together — powered by AI.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {FEATURES.map((f) => (
                            <div
                                key={f.title}
                                className="group relative p-6 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 hover:border-gray-300 dark:hover:border-gray-700 transition-all hover:shadow-lg hover:-translate-y-1"
                            >
                                {/* Gradient accent bar */}
                                <div className={`h-1 w-12 rounded-full bg-gradient-to-r ${f.color} mb-5`} />
                                <h3 className="text-xl font-semibold mb-2">{f.title}</h3>
                                <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed mb-6">{f.desc}</p>
                                <div className="flex items-end gap-2">
                                    <span className={`text-2xl font-bold bg-gradient-to-r ${f.color} bg-clip-text text-transparent`}>{f.stat}</span>
                                    <span className="text-xs text-gray-400 pb-0.5">{f.statLabel}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════ HOW IT WORKS ═══════════════ */}
            <section id="how-it-works" className="py-24 sm:py-32 bg-gray-50 dark:bg-gray-900/50">
                <div className="max-w-5xl mx-auto px-4 sm:px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl sm:text-5xl font-bold tracking-tight">
                            Three Steps to{" "}
                            <span className="bg-gradient-to-r from-emerald-500 to-blue-600 bg-clip-text text-transparent">
                                Launch Day
                            </span>
                        </h2>
                        <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
                            From idea to live business in minutes, not months.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {STEPS.map((s) => (
                            <div key={s.num} className="text-center md:text-left">
                                <span className="text-5xl font-black text-gray-100 dark:text-gray-800">{s.num}</span>
                                <h3 className="text-xl font-semibold mt-2 mb-3">{s.title}</h3>
                                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{s.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════ EXAMPLES SHOWCASE ═══════════════ */}
            <section id="examples" className="py-24 sm:py-32">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl sm:text-5xl font-bold tracking-tight">
                            See What You Can Build{" "}
                            <span className="bg-gradient-to-r from-violet-500 to-pink-500 bg-clip-text text-transparent">
                                In Minutes
                            </span>
                        </h2>
                        <p className="mt-4 text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                            Real sample pages generated by AgentBloom. Click any card to explore a fully designed,
                            content-rich example.
                        </p>
                    </div>

                    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {SHOWCASE.map((s) => (
                            <Link
                                key={s.title}
                                href={s.href}
                                className="group relative rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700 transition-all hover:shadow-xl hover:-translate-y-1 bg-white dark:bg-gray-900"
                            >
                                {/* Gradient header */}
                                <div className={`h-36 bg-gradient-to-br ${s.gradient} flex items-end p-5`}>
                                    <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-white/20 text-white backdrop-blur-sm">
                                        {s.niche}
                                    </span>
                                </div>
                                <div className="p-5">
                                    <h3 className="font-semibold text-lg mb-1.5 group-hover:text-blue-600 transition-colors">{s.title}</h3>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{s.desc}</p>
                                    <span className="mt-4 inline-flex items-center text-sm font-medium text-blue-600 dark:text-blue-400 group-hover:gap-2 transition-all gap-1">
                                        View Example
                                        <svg className="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
                                    </span>
                                </div>
                            </Link>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════ AI RECEPTIONIST ═══════════════ */}
            <section id="receptionist" className="py-24 sm:py-32 bg-gradient-to-br from-gray-900 via-gray-900 to-indigo-950 text-white">
                <div className="max-w-6xl mx-auto px-4 sm:px-6">
                    <div className="grid lg:grid-cols-2 gap-12 items-center">
                        {/* Left — copy */}
                        <div>
                            <span className="px-3 py-1 text-xs font-semibold rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 mb-6 inline-block">
                                Most Popular Feature
                            </span>
                            <h2 className="text-3xl sm:text-5xl font-bold tracking-tight leading-tight">
                                Your AI Receptionist Never Sleeps
                            </h2>
                            <p className="mt-6 text-lg text-gray-300 leading-relaxed">
                                Imagine a receptionist that works 24/7, knows your business inside-out,
                                answers questions instantly, qualifies leads, and books appointments —
                                all from a friendly chat widget on your website.
                            </p>
                            <ul className="mt-8 space-y-4">
                                {[
                                    "Greets every visitor by name and context",
                                    "Answers FAQs using your knowledge base",
                                    "Qualifies leads with smart follow-up questions",
                                    "Books appointments directly into your calendar",
                                    "Hands off to your team when human touch is needed",
                                    "Works across desktop and mobile, day and night",
                                ].map((item) => (
                                    <li key={item} className="flex items-start gap-3">
                                        <svg className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                                        <span className="text-gray-200">{item}</span>
                                    </li>
                                ))}
                            </ul>
                            <div className="mt-10 flex flex-col sm:flex-row gap-4">
                                <Link
                                    href="/examples/receptionist"
                                    className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-all shadow-lg text-center"
                                >
                                    Try the Live Demo
                                </Link>
                                <Link
                                    href="/auth/register"
                                    className="px-6 py-3 border border-gray-600 rounded-xl font-semibold hover:bg-gray-800 transition-all text-center"
                                >
                                    Add to Your Site
                                </Link>
                            </div>
                        </div>

                        {/* Right — Chat mockup */}
                        <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-1 shadow-2xl">
                            <div className="bg-gray-800 rounded-xl overflow-hidden">
                                {/* Chat header */}
                                <div className="px-5 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center text-lg">🤖</div>
                                    <div>
                                        <p className="font-semibold text-sm">AgentBloom Assistant</p>
                                        <p className="text-xs text-blue-200">Online — typically replies instantly</p>
                                    </div>
                                </div>
                                {/* Messages */}
                                <div className="p-5 space-y-4 min-h-[320px]">
                                    <div className="flex gap-3">
                                        <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-sm flex-shrink-0">🤖</div>
                                        <div className="bg-gray-700/50 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%]">
                                            <p className="text-sm text-gray-200">Hi there! 👋 Welcome to Bloom Fitness Studio. I&apos;m here to help you find the perfect class, learn about memberships, or book a free trial. What brings you in today?</p>
                                        </div>
                                    </div>
                                    <div className="flex gap-3 justify-end">
                                        <div className="bg-blue-600 rounded-2xl rounded-tr-sm px-4 py-3 max-w-[85%]">
                                            <p className="text-sm">I&apos;m interested in yoga classes. Do you have any for beginners?</p>
                                        </div>
                                    </div>
                                    <div className="flex gap-3">
                                        <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-sm flex-shrink-0">🤖</div>
                                        <div className="bg-gray-700/50 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%]">
                                            <p className="text-sm text-gray-200">Absolutely! We have <strong className="text-white">Gentle Flow Yoga</strong> every Tuesday & Thursday at 9 AM — perfect for beginners. It&apos;s a 60-minute class with instructor Maya Chen. Want me to book you a free trial session?</p>
                                        </div>
                                    </div>
                                    <div className="flex gap-3 justify-end">
                                        <div className="bg-blue-600 rounded-2xl rounded-tr-sm px-4 py-3 max-w-[85%]">
                                            <p className="text-sm">Yes please! Thursday works for me.</p>
                                        </div>
                                    </div>
                                    <div className="flex gap-3">
                                        <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-sm flex-shrink-0">🤖</div>
                                        <div className="bg-gray-700/50 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%]">
                                            <p className="text-sm text-gray-200">Done! ✅ I&apos;ve booked you for <strong className="text-white">Gentle Flow Yoga — Thursday 9 AM</strong> with Maya. I&apos;ll send a confirmation to your email. Anything else I can help with?</p>
                                        </div>
                                    </div>
                                </div>
                                {/* Input */}
                                <div className="px-5 pb-5">
                                    <div className="flex items-center gap-2 bg-gray-700/50 rounded-xl px-4 py-3">
                                        <span className="text-sm text-gray-400 flex-1">Type your message...</span>
                                        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                                            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" /></svg>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ═══════════════ TESTIMONIALS ═══════════════ */}
            <section className="py-24 sm:py-32">
                <div className="max-w-6xl mx-auto px-4 sm:px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl sm:text-5xl font-bold tracking-tight">
                            Loved by{" "}
                            <span className="bg-gradient-to-r from-amber-500 to-rose-500 bg-clip-text text-transparent">
                                Business Owners
                            </span>
                        </h2>
                    </div>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {TESTIMONIALS.map((t) => (
                            <div key={t.name} className="p-6 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
                                <div className="flex gap-1 mb-4">
                                    {[...Array(5)].map((_, i) => (
                                        <svg key={i} className="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                                    ))}
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 italic leading-relaxed mb-4">&ldquo;{t.quote}&rdquo;</p>
                                <div>
                                    <p className="font-semibold text-sm">{t.name}</p>
                                    <p className="text-xs text-gray-500">{t.role}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════ FINAL CTA ═══════════════ */}
            <section className="py-24 sm:py-32 bg-gradient-to-br from-blue-600 via-indigo-600 to-blue-700 text-white relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZyIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIxIiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDcpIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCBmaWxsPSJ1cmwoI2cpIiB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIi8+PC9zdmc+')] opacity-50" />
                <div className="relative max-w-3xl mx-auto px-4 sm:px-6 text-center">
                    <h2 className="text-3xl sm:text-5xl font-bold tracking-tight leading-tight">
                        Ready to Build Your Business<br />in Minutes, Not Months?
                    </h2>
                    <p className="mt-6 text-lg text-blue-100 max-w-xl mx-auto">
                        Join thousands of entrepreneurs who launched their entire online business
                        with a single conversation. No credit card required.
                    </p>
                    <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
                        <Link
                            href="/auth/register"
                            className="px-10 py-4 bg-white text-blue-700 rounded-xl font-bold text-lg hover:bg-blue-50 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5"
                        >
                            Start Building for Free
                        </Link>
                    </div>
                    <p className="mt-6 text-sm text-blue-200">
                        Free forever plan · No credit card · Set up in 60 seconds
                    </p>
                </div>
            </section>

            {/* ═══════════════ FOOTER ═══════════════ */}
            <footer className="py-12 border-t border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-950">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-8 mb-12">
                        <div>
                            <span className="text-xl font-bold">
                                <span className="text-blue-600">Agent</span>
                                <span className="text-emerald-500">Bloom</span>
                            </span>
                            <p className="mt-3 text-sm text-gray-500 leading-relaxed">
                                AI-powered business builder. Websites, CRM, courses, bookings & more — built by conversation.
                            </p>
                        </div>
                        <div>
                            <p className="font-semibold text-sm mb-3">Product</p>
                            <ul className="space-y-2 text-sm text-gray-500">
                                <li><a href="#features" className="hover:text-gray-900 dark:hover:text-white transition-colors">Features</a></li>
                                <li><a href="#examples" className="hover:text-gray-900 dark:hover:text-white transition-colors">Examples</a></li>
                                <li><a href="#receptionist" className="hover:text-gray-900 dark:hover:text-white transition-colors">AI Receptionist</a></li>
                            </ul>
                        </div>
                        <div>
                            <p className="font-semibold text-sm mb-3">Company</p>
                            <ul className="space-y-2 text-sm text-gray-500">
                                <li><Link href="/terms" className="hover:text-gray-900 dark:hover:text-white transition-colors">Terms of Service</Link></li>
                                <li><Link href="/privacy" className="hover:text-gray-900 dark:hover:text-white transition-colors">Privacy Policy</Link></li>
                            </ul>
                        </div>
                        <div>
                            <p className="font-semibold text-sm mb-3">Get Started</p>
                            <ul className="space-y-2 text-sm text-gray-500">
                                <li><Link href="/auth/register" className="hover:text-gray-900 dark:hover:text-white transition-colors">Create Account</Link></li>
                                <li><Link href="/auth/login" className="hover:text-gray-900 dark:hover:text-white transition-colors">Sign In</Link></li>
                            </ul>
                        </div>
                    </div>
                    <div className="pt-8 border-t border-gray-100 dark:border-gray-800 text-center text-sm text-gray-400">
                        &copy; {new Date().getFullYear()} NobleBlocks LLC. All rights reserved.
                    </div>
                </div>
            </footer>
        </main>
    );
}
