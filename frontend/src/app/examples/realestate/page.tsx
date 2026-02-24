import Link from "next/link";

const LISTINGS = [
    { address: "247 Oceanview Drive", city: "Malibu, CA", price: "$4,250,000", beds: 5, baths: 4, sqft: "4,200", status: "New Listing", gradient: "from-sky-400 to-blue-500" },
    { address: "1892 Cedar Bluff Court", city: "Beverly Hills, CA", price: "$3,875,000", beds: 4, baths: 3, sqft: "3,800", status: "Open House Sun", gradient: "from-emerald-400 to-teal-500" },
    { address: "310 Magnolia Lane", city: "Pasadena, CA", price: "$1,950,000", beds: 4, baths: 3, sqft: "2,900", status: "Price Reduced", gradient: "from-amber-400 to-orange-500" },
    { address: "55 Sunset Strip #PH4", city: "West Hollywood, CA", price: "$2,100,000", beds: 3, baths: 2, sqft: "2,200", status: "Pending", gradient: "from-violet-400 to-purple-500" },
    { address: "8820 Wilshire Blvd #1201", city: "Los Angeles, CA", price: "$1,450,000", beds: 2, baths: 2, sqft: "1,650", status: "New Listing", gradient: "from-rose-400 to-pink-500" },
    { address: "1455 Laurel Canyon Blvd", city: "Studio City, CA", price: "$2,750,000", beds: 5, baths: 4, sqft: "3,500", status: "Just Listed", gradient: "from-indigo-400 to-blue-500" },
];

const SERVICES = [
    { title: "Buying", desc: "From first-time buyers to luxury collectors, we guide you through every step — market analysis, negotiations, inspections, and closing." },
    { title: "Selling", desc: "Professional staging advice, drone photography, targeted digital marketing, and open house coordination to get top dollar for your property." },
    { title: "Investment", desc: "Identify high-ROI opportunities, analyse rental yields, and build a portfolio of income-generating properties with expert guidance." },
    { title: "Relocation", desc: "Moving to LA? We handle neighbourhood matching, school research, virtual tours, and every logistic so you can focus on the exciting part." },
];

const STATS = [
    { value: "$850M+", label: "Total Sales Volume" },
    { value: "1,200+", label: "Properties Sold" },
    { value: "98%", label: "Client Satisfaction" },
    { value: "15", label: "Years of Experience" },
];

export default function RealEstateExample() {
    return (
        <main className="min-h-screen bg-white dark:bg-gray-950">
            {/* Banner */}
            <div className="bg-blue-600 text-white text-center py-2 text-sm font-medium">
                <Link href="/" className="hover:underline">← This is a sample page built with AgentBloom — Create your own for free</Link>
            </div>

            {/* Hero */}
            <section className="relative bg-gradient-to-br from-slate-900 via-slate-800 to-sky-950 text-white overflow-hidden">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImciIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMS41IiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDMpIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCBmaWxsPSJ1cmwoI2cpIiB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIi8+PC9zdmc+')] opacity-60" />
                <div className="relative max-w-6xl mx-auto px-4 sm:px-6 py-28 sm:py-40">
                    <p className="text-sky-300 font-medium tracking-widest text-sm uppercase mb-4">Los Angeles Premium Real Estate</p>
                    <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight leading-[1.1] max-w-3xl">
                        Prestige Realty<br />
                        <span className="bg-gradient-to-r from-sky-400 to-blue-300 bg-clip-text text-transparent">Group</span>
                    </h1>
                    <p className="mt-6 text-xl text-gray-300 max-w-xl leading-relaxed">Curating exceptional properties and delivering white-glove service for discerning buyers and sellers across Los Angeles.</p>
                    <div className="mt-10 flex flex-wrap gap-4">
                        <span className="px-6 py-3 bg-sky-500 text-white rounded-xl font-semibold hover:bg-sky-600 transition-colors cursor-pointer shadow-lg">View Listings</span>
                        <span className="px-6 py-3 border border-gray-500 rounded-xl font-semibold hover:bg-gray-800 transition-colors cursor-pointer">Schedule Consultation</span>
                    </div>
                </div>
            </section>

            {/* Stats */}
            <section className="py-12 bg-gray-50 dark:bg-gray-900/50 border-y border-gray-100 dark:border-gray-800">
                <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                    {STATS.map((s) => (<div key={s.label}><p className="text-3xl font-bold text-sky-600">{s.value}</p><p className="text-sm text-gray-500 mt-1">{s.label}</p></div>))}
                </div>
            </section>

            {/* Featured Listings */}
            <section className="py-24">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">Featured Listings</h2>
                    <p className="text-center text-gray-500 mb-12 max-w-xl mx-auto">Hand-picked properties that represent the best of LA living.</p>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {LISTINGS.map((l) => (
                            <div key={l.address} className="group rounded-2xl border border-gray-200 dark:border-gray-800 overflow-hidden hover:shadow-xl hover:-translate-y-1 transition-all bg-white dark:bg-gray-900 cursor-pointer">
                                <div className={`h-48 bg-gradient-to-br ${l.gradient} relative flex items-end p-5`}>
                                    <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-white/20 text-white backdrop-blur-sm">{l.status}</span>
                                </div>
                                <div className="p-6">
                                    <p className="text-2xl font-bold mb-1">{l.price}</p>
                                    <h3 className="font-semibold text-lg mb-0.5">{l.address}</h3>
                                    <p className="text-sm text-gray-500 mb-4">{l.city}</p>
                                    <div className="flex gap-4 text-sm text-gray-600 dark:text-gray-400">
                                        <span>{l.beds} beds</span>
                                        <span className="text-gray-300">|</span>
                                        <span>{l.baths} baths</span>
                                        <span className="text-gray-300">|</span>
                                        <span>{l.sqft} sqft</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Services */}
            <section className="py-24 bg-gray-50 dark:bg-gray-900/50">
                <div className="max-w-6xl mx-auto px-4 sm:px-6">
                    <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">Our Services</h2>
                    <p className="text-center text-gray-500 mb-12">End-to-end real estate expertise.</p>
                    <div className="grid sm:grid-cols-2 gap-6">
                        {SERVICES.map((s) => (
                            <div key={s.title} className="bg-white dark:bg-gray-900 rounded-2xl p-8 border border-gray-200 dark:border-gray-800 hover:shadow-lg transition-all">
                                <h3 className="text-xl font-semibold mb-3">{s.title}</h3>
                                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{s.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Agent Profile */}
            <section className="py-24">
                <div className="max-w-4xl mx-auto px-4 sm:px-6">
                    <div className="bg-gradient-to-br from-slate-900 to-sky-950 rounded-3xl p-8 sm:p-12 text-white">
                        <div className="flex flex-col md:flex-row items-center gap-8">
                            <div className="w-32 h-32 rounded-2xl bg-gradient-to-br from-sky-400 to-blue-500 flex items-center justify-center text-4xl font-bold flex-shrink-0">RK</div>
                            <div>
                                <h2 className="text-3xl font-bold mb-2">Rebecca Kim</h2>
                                <p className="text-sky-300 font-medium mb-4">Principal Broker · DRE #01234567</p>
                                <p className="text-gray-300 leading-relaxed mb-6">With $850M+ in career sales and 15 years in LA luxury real estate, Rebecca brings unmatched market knowledge, fierce negotiation skills, and a genuine passion for matching people with their dream homes.</p>
                                <div className="flex flex-wrap gap-3">
                                    <span className="px-5 py-2.5 bg-sky-500 rounded-xl font-semibold cursor-pointer hover:bg-sky-600 transition-colors text-sm">Book a Free Consultation</span>
                                    <span className="px-5 py-2.5 border border-gray-500 rounded-xl font-semibold cursor-pointer hover:bg-gray-800 transition-colors text-sm">(310) 555-0198</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="py-24 bg-gradient-to-r from-sky-600 to-blue-700 text-white text-center">
                <div className="max-w-2xl mx-auto px-4">
                    <h2 className="text-3xl sm:text-4xl font-bold mb-4">Find Your Dream Home</h2>
                    <p className="text-lg text-sky-100 mb-8">Whether you&apos;re buying, selling, or investing — let&apos;s talk about your real estate goals.</p>
                    <span className="inline-block px-8 py-3.5 bg-white text-sky-700 rounded-xl font-bold text-lg cursor-pointer hover:bg-sky-50 transition-all shadow-lg">Schedule a Consultation</span>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 bg-gray-900 text-gray-400 text-center text-sm">
                <p className="mb-2">Prestige Realty Group · 9876 Wilshire Blvd, Suite 400 · Beverly Hills, CA 90210</p>
                <p>(310) 555-0198 · rebecca@prestigerealtygroup.com</p>
                <p className="mt-4 text-gray-500">Sample page created with <Link href="/" className="text-blue-400 hover:underline">AgentBloom</Link></p>
            </footer>
        </main>
    );
}
