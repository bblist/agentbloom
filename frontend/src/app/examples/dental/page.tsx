import Link from "next/link";

const SERVICES = [
    { title: "General Dentistry", desc: "Routine exams, cleanings, fillings, and preventive care to keep your smile healthy for life.", gradient: "from-cyan-400 to-teal-500" },
    { title: "Cosmetic Dentistry", desc: "Veneers, teeth whitening, bonding, and smile makeovers tailored to your goals.", gradient: "from-violet-400 to-purple-500" },
    { title: "Orthodontics", desc: "Invisalign clear aligners and traditional braces for children, teens, and adults.", gradient: "from-blue-400 to-indigo-500" },
    { title: "Dental Implants", desc: "Permanent tooth replacement with titanium implants — natural look, lifetime durability.", gradient: "from-emerald-400 to-green-500" },
    { title: "Emergency Care", desc: "Same-day appointments for toothaches, chipped teeth, lost crowns, and dental trauma.", gradient: "from-rose-400 to-red-500" },
    { title: "Pediatric Dentistry", desc: "Gentle, fun dental visits for kids — sealants, fluoride treatments, and early orthodontic screening.", gradient: "from-amber-400 to-orange-500" },
];

const TEAM = [
    { name: "Dr. Sarah Chen, DDS", role: "Lead Dentist · 18 Years Experience", bio: "Columbia University College of Dental Medicine graduate. Board-certified in cosmetic and implant dentistry. Passionate about anxiety-free dentistry.", initials: "SC", color: "from-cyan-400 to-teal-500" },
    { name: "Dr. James Park, DMD", role: "Orthodontist · Invisalign Diamond Provider", bio: "Specialises in clear aligner therapy and complex bite correction. Completed 1,500+ Invisalign cases.", initials: "JP", color: "from-violet-400 to-purple-500" },
    { name: "Monica Alvarez, RDH", role: "Lead Hygienist · 12 Years Experience", bio: "Known for her gentle touch and thorough cleanings. Certified in laser therapy and periodontal treatment.", initials: "MA", color: "from-rose-400 to-pink-500" },
];

const INSURANCE = ["Delta Dental", "Cigna", "Aetna", "MetLife", "Guardian", "United Healthcare", "BlueCross BlueShield", "Humana"];

const REVIEWS = [
    { name: "Jennifer L.", text: "I used to dread the dentist, but Dr. Chen and her team made me feel completely at ease. Best dental experience I've ever had!", stars: 5 },
    { name: "David M.", text: "Got Invisalign with Dr. Park — my teeth look amazing after 10 months. The 3D scans and progress tracking were incredible.", stars: 5 },
    { name: "Amanda T.", text: "My kids actually look forward to their dental visits now. The office is beautiful, the staff is so friendly, and Monica is the best hygienist.", stars: 5 },
    { name: "Robert K.", text: "Emergency appointment for a cracked tooth — they got me in the same day and the crown looks completely natural. Can't recommend enough.", stars: 5 },
];

export default function DentalExample() {
    return (
        <main className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
            {/* Banner */}
            <div className="bg-blue-600 text-white text-center py-2 text-sm font-medium">
                <Link href="/" className="hover:underline">← This is a sample page built with AgentBloom — Create your own for free</Link>
            </div>

            {/* Hero */}
            <section className="relative bg-gradient-to-br from-teal-900 via-cyan-900 to-slate-900 text-white overflow-hidden">
                <div className="absolute inset-0 opacity-10" style={{ backgroundImage: "radial-gradient(circle at 30% 40%, #06b6d444 0%, transparent 50%), radial-gradient(circle at 70% 60%, #14b8a644 0%, transparent 50%)" }} />
                <div className="relative max-w-5xl mx-auto px-4 sm:px-6 py-28 sm:py-40">
                    <p className="text-cyan-300 font-medium tracking-widest text-sm uppercase mb-4">Modern Family & Cosmetic Dentistry</p>
                    <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight leading-[1.1] max-w-3xl">
                        Bright Smile<br />
                        <span className="bg-gradient-to-r from-cyan-300 to-teal-300 bg-clip-text text-transparent">Dental Studio</span>
                    </h1>
                    <p className="mt-6 text-xl text-gray-300 max-w-xl leading-relaxed">Compassionate, state-of-the-art dental care for your whole family. Because everyone deserves a smile they love.</p>
                    <div className="mt-10 flex flex-wrap gap-4">
                        <span className="px-7 py-3 bg-cyan-500 text-white rounded-xl font-bold hover:bg-cyan-600 transition-colors cursor-pointer shadow-lg">Book Appointment</span>
                        <span className="px-7 py-3 border border-gray-500 rounded-xl font-semibold hover:bg-gray-800 transition-colors cursor-pointer">(555) 234-5678</span>
                    </div>
                </div>
            </section>

            {/* Stats */}
            <section className="py-10 bg-gray-50 dark:bg-gray-900/50 border-y border-gray-100 dark:border-gray-800">
                <div className="max-w-4xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                    {[
                        { v: "5,000+", l: "Happy Patients" },
                        { v: "4.9★", l: "Google Rating" },
                        { v: "18", l: "Years in Practice" },
                        { v: "0%", l: "Interest Financing" },
                    ].map((s) => (<div key={s.l}><p className="text-2xl font-bold text-cyan-600">{s.v}</p><p className="text-xs text-gray-500 mt-1">{s.l}</p></div>))}
                </div>
            </section>

            {/* Services */}
            <section className="py-24">
                <div className="max-w-6xl mx-auto px-4 sm:px-6">
                    <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">Our Services</h2>
                    <p className="text-center text-gray-500 mb-12 max-w-lg mx-auto">Comprehensive dental care under one roof — from routine checkups to complete smile transformations.</p>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {SERVICES.map((s) => (
                            <div key={s.title} className="group rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6 hover:shadow-lg hover:-translate-y-1 transition-all cursor-pointer overflow-hidden relative">
                                <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${s.gradient}`} />
                                <h3 className="text-lg font-semibold mb-2 mt-2">{s.title}</h3>
                                <p className="text-gray-500 text-sm leading-relaxed">{s.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Team */}
            <section className="py-24 bg-gray-50 dark:bg-gray-900/50">
                <div className="max-w-5xl mx-auto px-4 sm:px-6">
                    <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">Meet Your Care Team</h2>
                    <p className="text-center text-gray-500 mb-12">Friendly, experienced professionals who genuinely care about your comfort.</p>
                    <div className="grid sm:grid-cols-3 gap-6">
                        {TEAM.map((t) => (
                            <div key={t.name} className="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-200 dark:border-gray-800 text-center">
                                <div className={`w-20 h-20 mx-auto rounded-full bg-gradient-to-br ${t.color} flex items-center justify-center text-2xl font-bold text-white mb-4`}>{t.initials}</div>
                                <h3 className="font-semibold text-lg">{t.name}</h3>
                                <p className="text-cyan-600 text-sm mb-3">{t.role}</p>
                                <p className="text-gray-500 text-sm leading-relaxed">{t.bio}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Insurance */}
            <section className="py-20">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
                    <h2 className="text-3xl font-bold mb-4">Insurance & Payment</h2>
                    <p className="text-gray-500 mb-8 max-w-lg mx-auto">We accept most major dental insurance plans and offer flexible payment options.</p>
                    <div className="flex flex-wrap justify-center gap-3 mb-8">
                        {INSURANCE.map((ins) => (
                            <span key={ins} className="px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-full text-sm font-medium">{ins}</span>
                        ))}
                    </div>
                    <p className="text-sm text-gray-500">No insurance? No problem. We offer 0% interest payment plans and an in-house membership plan starting at $29/month.</p>
                </div>
            </section>

            {/* Special Offer */}
            <section className="py-20 bg-gradient-to-r from-cyan-600 to-teal-600 text-white">
                <div className="max-w-3xl mx-auto px-4 sm:px-6 text-center">
                    <p className="text-cyan-200 font-medium text-sm uppercase tracking-wide mb-3">New Patient Special</p>
                    <h2 className="text-3xl sm:text-4xl font-bold mb-4">Exam, X-Rays & Cleaning — $99</h2>
                    <p className="text-lg text-cyan-100 mb-8">Comprehensive exam, full digital x-rays, and professional cleaning. A $350 value — available for new patients only.</p>
                    <span className="inline-block px-8 py-3.5 bg-white text-cyan-700 rounded-xl font-bold text-lg cursor-pointer hover:bg-cyan-50 transition-all shadow-lg">Claim This Offer</span>
                </div>
            </section>

            {/* Reviews */}
            <section className="py-24">
                <div className="max-w-5xl mx-auto px-4 sm:px-6">
                    <h2 className="text-3xl font-bold text-center mb-12">Patient Reviews</h2>
                    <div className="grid sm:grid-cols-2 gap-6">
                        {REVIEWS.map((r) => (
                            <div key={r.name} className="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-200 dark:border-gray-800">
                                <p className="text-amber-500 text-lg mb-3">{"★".repeat(r.stars)}</p>
                                <p className="text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">&quot;{r.text}&quot;</p>
                                <p className="font-semibold text-sm">{r.name}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 bg-gray-900 text-gray-400 text-center text-sm">
                <p className="mb-2">Bright Smile Dental Studio · 456 Oak Avenue, Suite 200 · Anytown, USA 12345</p>
                <p>(555) 234-5678 · hello@brightsmiledentalstudio.com</p>
                <p className="mt-2 text-gray-500">Mon-Fri 8AM-6PM · Sat 9AM-3PM · Emergency appointments available</p>
                <p className="mt-4 text-gray-500">Sample page created with <Link href="/" className="text-blue-400 hover:underline">AgentBloom</Link></p>
            </footer>
        </main>
    );
}
