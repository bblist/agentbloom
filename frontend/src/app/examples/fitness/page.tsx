import Link from "next/link";

const CLASSES = [
    { name: "Gentle Flow Yoga", time: "Tue & Thu 9:00 AM", duration: "60 min", instructor: "Maya Chen", level: "Beginner", color: "from-violet-500 to-purple-600" },
    { name: "HIIT Burn", time: "Mon, Wed, Fri 6:30 AM", duration: "45 min", instructor: "Jake Rivera", level: "Advanced", color: "from-red-500 to-orange-600" },
    { name: "Pilates Core", time: "Tue & Thu 5:30 PM", duration: "50 min", instructor: "Sarah Kim", level: "Intermediate", color: "from-pink-500 to-rose-600" },
    { name: "Spin & Sweat", time: "Mon & Wed 7:00 PM", duration: "45 min", instructor: "Marcus Johnson", level: "All Levels", color: "from-amber-500 to-orange-600" },
    { name: "Power Vinyasa", time: "Sat 8:00 AM", duration: "75 min", instructor: "Maya Chen", level: "Intermediate", color: "from-emerald-500 to-teal-600" },
    { name: "Boxing Bootcamp", time: "Fri 6:00 PM", duration: "55 min", instructor: "Jake Rivera", level: "Advanced", color: "from-blue-500 to-indigo-600" },
];

const TRAINERS = [
    { name: "Maya Chen", specialty: "Yoga & Mindfulness", bio: "500-hour RYT with 12 years of experience. Maya blends traditional Hatha with modern flow techniques to create classes that calm the mind and strengthen the body.", certifications: "RYT-500, ACE-CPT" },
    { name: "Jake Rivera", specialty: "HIIT & Strength", bio: "Former collegiate athlete turned elite trainer. Jake's high-intensity sessions are designed to push your limits while keeping your form perfect and your motivation high.", certifications: "NASM-CPT, CSCS" },
    { name: "Sarah Kim", specialty: "Pilates & Rehabilitation", bio: "Physical therapist turned Pilates instructor. Sarah specialises in corrective exercise and post-injury recovery through controlled, precise movements.", certifications: "PMA-CPT, DPT" },
];

const PLANS = [
    { name: "Drop-In", price: "$25", period: "/class", features: ["Single class access", "Towel & water included", "No commitment", "Book online or at the desk"], popular: false },
    { name: "Unlimited", price: "$129", period: "/month", features: ["Unlimited classes", "1 guest pass per month", "Priority booking", "Locker & towel service", "Free body composition scan"], popular: true },
    { name: "Annual VIP", price: "$99", period: "/month", features: ["Everything in Unlimited", "2 personal training sessions/month", "Nutrition consultation", "Exclusive member events", "Freeze up to 30 days", "Branded water bottle & gear"], popular: false },
];

const TESTIMONIALS = [
    { name: "Rachel M.", quote: "I've been coming to Bloom for 6 months and I've never felt stronger. Maya's yoga classes completely transformed my flexibility and stress levels.", rating: 5 },
    { name: "David L.", quote: "Jake's HIIT classes are no joke. I lost 22 pounds in 3 months and actually enjoy working out now. Best gym decision I ever made.", rating: 5 },
    { name: "Emma S.", quote: "After my knee surgery, Sarah's Pilates classes helped me recover faster than my PT predicted. The personalised attention here is unmatched.", rating: 5 },
];

export default function FitnessExample() {
    return (
        <main className="min-h-screen bg-white dark:bg-gray-950">
            {/* Banner */}
            <div className="bg-blue-600 text-white text-center py-2 text-sm font-medium">
                <Link href="/" className="hover:underline">← This is a sample page built with AgentBloom — Create your own for free</Link>
            </div>

            {/* Hero */}
            <section className="relative bg-gradient-to-br from-gray-900 via-gray-900 to-orange-950 text-white overflow-hidden">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImciIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMS41IiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDUpIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCBmaWxsPSJ1cmwoI2cpIiB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIi8+PC9zdmc+')] opacity-60" />
                <div className="relative max-w-6xl mx-auto px-4 sm:px-6 py-24 sm:py-36">
                    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-orange-500/20 text-orange-300 border border-orange-500/30 mb-6 inline-block">Now Open — Limited Founding Memberships</span>
                    <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight leading-[1.1] max-w-3xl">
                        Bloom Fitness<br />
                        <span className="bg-gradient-to-r from-orange-400 to-rose-500 bg-clip-text text-transparent">Studio</span>
                    </h1>
                    <p className="mt-6 text-xl text-gray-300 max-w-xl leading-relaxed">Where strength meets serenity. Boutique fitness classes, expert trainers, and a community that lifts you up — every single day.</p>
                    <div className="mt-10 flex flex-wrap gap-4">
                        <span className="px-6 py-3 bg-orange-500 text-white rounded-xl font-semibold hover:bg-orange-600 transition-colors cursor-pointer shadow-lg">Book a Free Trial</span>
                        <a href="#classes" className="px-6 py-3 border border-gray-500 rounded-xl font-semibold hover:bg-gray-800 transition-colors">View Schedule</a>
                    </div>
                </div>
            </section>

            {/* Stats */}
            <section className="py-12 bg-gray-50 dark:bg-gray-900/50 border-y border-gray-100 dark:border-gray-800">
                <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                    <div><p className="text-3xl font-bold text-orange-500">500+</p><p className="text-sm text-gray-500 mt-1">Active Members</p></div>
                    <div><p className="text-3xl font-bold text-orange-500">30+</p><p className="text-sm text-gray-500 mt-1">Weekly Classes</p></div>
                    <div><p className="text-3xl font-bold text-orange-500">4.9★</p><p className="text-sm text-gray-500 mt-1">Google Rating</p></div>
                    <div><p className="text-3xl font-bold text-orange-500">6</p><p className="text-sm text-gray-500 mt-1">Expert Trainers</p></div>
                </div>
            </section>

            {/* Classes */}
            <section id="classes" className="py-24">
                <div className="max-w-6xl mx-auto px-4 sm:px-6">
                    <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">Class Schedule</h2>
                    <p className="text-center text-gray-500 mb-12 max-w-xl mx-auto">From gentle flow to all-out sweat. Find the perfect class for your goals, your vibe, and your schedule.</p>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {CLASSES.map((c) => (
                            <div key={c.name} className="group rounded-2xl border border-gray-200 dark:border-gray-800 overflow-hidden hover:shadow-lg hover:-translate-y-1 transition-all bg-white dark:bg-gray-900">
                                <div className={`h-2 bg-gradient-to-r ${c.color}`} />
                                <div className="p-6">
                                    <div className="flex justify-between items-start mb-3">
                                        <h3 className="font-semibold text-lg">{c.name}</h3>
                                        <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">{c.level}</span>
                                    </div>
                                    <p className="text-sm text-gray-500 mb-1">{c.time}</p>
                                    <p className="text-sm text-gray-500 mb-4">{c.duration} · {c.instructor}</p>
                                    <span className="text-sm font-medium text-orange-600 dark:text-orange-400 cursor-pointer hover:underline">Book This Class →</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Trainers */}
            <section className="py-24 bg-gray-50 dark:bg-gray-900/50">
                <div className="max-w-6xl mx-auto px-4 sm:px-6">
                    <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">Meet Your Trainers</h2>
                    <p className="text-center text-gray-500 mb-12 max-w-xl mx-auto">Certified experts who care about your progress as much as you do.</p>
                    <div className="grid md:grid-cols-3 gap-8">
                        {TRAINERS.map((t) => (
                            <div key={t.name} className="bg-white dark:bg-gray-900 rounded-2xl p-8 border border-gray-200 dark:border-gray-800 text-center">
                                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-orange-400 to-rose-500 mx-auto mb-5 flex items-center justify-center text-white text-2xl font-bold">{t.name.split(" ").map(n => n[0]).join("")}</div>
                                <h3 className="font-semibold text-lg">{t.name}</h3>
                                <p className="text-sm text-orange-600 dark:text-orange-400 font-medium mb-3">{t.specialty}</p>
                                <p className="text-sm text-gray-500 leading-relaxed mb-4">{t.bio}</p>
                                <p className="text-xs text-gray-400">{t.certifications}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Pricing */}
            <section className="py-24">
                <div className="max-w-5xl mx-auto px-4 sm:px-6">
                    <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">Membership Plans</h2>
                    <p className="text-center text-gray-500 mb-12">Simple pricing. No hidden fees. Cancel anytime.</p>
                    <div className="grid md:grid-cols-3 gap-6">
                        {PLANS.map((p) => (
                            <div key={p.name} className={`rounded-2xl p-8 border ${p.popular ? "border-orange-500 ring-2 ring-orange-500/20 bg-orange-50 dark:bg-orange-950/20" : "border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900"} relative`}>
                                {p.popular && <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-orange-500 text-white text-xs font-semibold rounded-full">Most Popular</span>}
                                <h3 className="text-xl font-semibold mb-2">{p.name}</h3>
                                <div className="mb-6"><span className="text-4xl font-bold">{p.price}</span><span className="text-gray-500">{p.period}</span></div>
                                <ul className="space-y-3 mb-8">
                                    {p.features.map((f) => (
                                        <li key={f} className="flex items-start gap-2 text-sm">
                                            <svg className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
                                            <span className="text-gray-600 dark:text-gray-400">{f}</span>
                                        </li>
                                    ))}
                                </ul>
                                <span className={`block w-full text-center py-3 rounded-xl font-semibold cursor-pointer transition-colors ${p.popular ? "bg-orange-500 text-white hover:bg-orange-600" : "bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"}`}>
                                    {p.name === "Drop-In" ? "Buy a Class" : "Join Now"}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Testimonials */}
            <section className="py-24 bg-gray-50 dark:bg-gray-900/50">
                <div className="max-w-5xl mx-auto px-4 sm:px-6">
                    <h2 className="text-3xl sm:text-4xl font-bold text-center mb-12">What Our Members Say</h2>
                    <div className="grid md:grid-cols-3 gap-6">
                        {TESTIMONIALS.map((t) => (
                            <div key={t.name} className="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-200 dark:border-gray-800">
                                <div className="flex gap-1 mb-3">{[...Array(t.rating)].map((_, i) => (<svg key={i} className="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>))}</div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 italic leading-relaxed mb-4">&ldquo;{t.quote}&rdquo;</p>
                                <p className="font-semibold text-sm">{t.name}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="py-24 bg-gradient-to-r from-orange-500 to-rose-600 text-white text-center">
                <div className="max-w-2xl mx-auto px-4">
                    <h2 className="text-3xl sm:text-4xl font-bold mb-4">Your First Class Is On Us</h2>
                    <p className="text-lg text-orange-100 mb-8">Book a free trial and experience the Bloom difference. No commitment, no pressure — just great energy.</p>
                    <span className="inline-block px-8 py-3.5 bg-white text-orange-600 rounded-xl font-bold text-lg cursor-pointer hover:bg-orange-50 transition-all shadow-lg">Book Your Free Trial</span>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 bg-gray-900 text-gray-400 text-center text-sm">
                <p className="mb-2">Bloom Fitness Studio · 742 Evergreen Terrace, Suite 200 · Portland, OR 97201</p>
                <p>(503) 555-0172 · hello@bloomfitness.com</p>
                <p className="mt-4 text-gray-500">Sample page created with <Link href="/" className="text-blue-400 hover:underline">AgentBloom</Link></p>
            </footer>
        </main>
    );
}
