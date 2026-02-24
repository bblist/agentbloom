import Link from "next/link";

const MENU_CATEGORIES = [
    {
        name: "Starters",
        items: [
            { dish: "Truffle Burrata", desc: "Heirloom tomatoes, aged balsamic, basil oil, grilled sourdough", price: "$18" },
            { dish: "Seared Ahi Tuna", desc: "Sesame crust, wakame salad, ponzu, pickled ginger", price: "$22" },
            { dish: "Roasted Beet Carpaccio", desc: "Goat cheese mousse, candied walnuts, microgreens, honey vinaigrette", price: "$16" },
        ],
    },
    {
        name: "Mains",
        items: [
            { dish: "Pan-Seared Chilean Sea Bass", desc: "Saffron risotto, broccolini, lemon beurre blanc", price: "$42" },
            { dish: "36-Hour Short Ribs", desc: "Creamy polenta, roasted root vegetables, red wine jus", price: "$38" },
            { dish: "Wild Mushroom Ravioli", desc: "Handmade pasta, truffle cream, parmigiano, crispy sage", price: "$28" },
            { dish: "Grass-Fed Filet Mignon", desc: "8oz centre cut, roasted garlic mash, asparagus, peppercorn sauce", price: "$52" },
        ],
    },
    {
        name: "Desserts",
        items: [
            { dish: "Dark Chocolate Fondant", desc: "Molten centre, vanilla bean ice cream, cocoa tuile", price: "$15" },
            { dish: "Lemon Tart", desc: "Italian meringue, raspberry coulis, edible flowers", price: "$14" },
            { dish: "Crème Brûlée", desc: "Tahitian vanilla, caramelised sugar, shortbread biscuit", price: "$13" },
        ],
    },
];

const HOURS = [
    { day: "Monday – Thursday", time: "5:00 PM – 10:00 PM" },
    { day: "Friday – Saturday", time: "5:00 PM – 11:00 PM" },
    { day: "Sunday", time: "10:00 AM – 3:00 PM (Brunch) · 5:00 PM – 9:00 PM" },
];

const REVIEWS = [
    { name: "Michael R.", text: "An absolute gem. The short ribs are the best I've ever had — melt-in-your-mouth perfection. Service was impeccable.", stars: 5 },
    { name: "Claire D.", text: "Perfect spot for a date night. Loved the ambiance — moody lighting, curated playlist, and the cocktails are art.", stars: 5 },
    { name: "Tomás G.", text: "Sunday brunch is now a family tradition. The kids love the French toast and we love the bottomless mimosas!", stars: 5 },
];

export default function RestaurantExample() {
    return (
        <main className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
            {/* Banner */}
            <div className="bg-blue-600 text-white text-center py-2 text-sm font-medium">
                <Link href="/" className="hover:underline">← This is a sample page built with AgentBloom — Create your own for free</Link>
            </div>

            {/* Hero */}
            <section className="relative bg-gradient-to-br from-amber-950 via-stone-900 to-stone-950 text-white overflow-hidden">
                <div className="absolute inset-0 opacity-10" style={{ backgroundImage: "radial-gradient(circle at 25% 50%, #f59e0b44 0%, transparent 50%), radial-gradient(circle at 75% 50%, #d9770644 0%, transparent 50%)" }} />
                <div className="relative max-w-5xl mx-auto px-4 sm:px-6 py-32 sm:py-44 text-center">
                    <p className="text-amber-300 font-medium tracking-[0.25em] text-sm uppercase mb-6">Farm-to-Table · Craft Cocktails · Fine Dining</p>
                    <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight leading-[1.1]">
                        The Artisan<br />
                        <span className="bg-gradient-to-r from-amber-300 to-orange-400 bg-clip-text text-transparent">Kitchen</span>
                    </h1>
                    <p className="mt-6 text-xl text-stone-300 max-w-xl mx-auto leading-relaxed">Seasonal ingredients. Masterful preparation. Unforgettable experiences.</p>
                    <div className="mt-10 flex flex-wrap justify-center gap-4">
                        <span className="px-7 py-3 bg-amber-500 text-stone-900 rounded-xl font-bold hover:bg-amber-400 transition-colors cursor-pointer shadow-lg">Reserve a Table</span>
                        <span className="px-7 py-3 border border-stone-500 rounded-xl font-semibold hover:bg-stone-800 transition-colors cursor-pointer">View Menu</span>
                    </div>
                </div>
            </section>

            {/* Stats */}
            <section className="py-10 bg-stone-50 dark:bg-gray-900/50 border-y border-stone-200 dark:border-gray-800">
                <div className="max-w-4xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                    {[
                        { v: "4.9★", l: "Google Rating" },
                        { v: "800+", l: "Reviews" },
                        { v: "12", l: "Years Open" },
                        { v: "#3", l: "Best in the City" },
                    ].map((s) => (<div key={s.l}><p className="text-2xl font-bold text-amber-600">{s.v}</p><p className="text-xs text-gray-500 mt-1">{s.l}</p></div>))}
                </div>
            </section>

            {/* Menu */}
            <section className="py-24">
                <div className="max-w-5xl mx-auto px-4 sm:px-6">
                    <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">Our Menu</h2>
                    <p className="text-center text-gray-500 mb-16 max-w-lg mx-auto">Seasonally inspired dishes crafted from locally sourced ingredients.</p>

                    {MENU_CATEGORIES.map((cat) => (
                        <div key={cat.name} className="mb-14 last:mb-0">
                            <h3 className="text-xl font-semibold mb-6 text-amber-600 tracking-wide uppercase">{cat.name}</h3>
                            <div className="space-y-5">
                                {cat.items.map((item) => (
                                    <div key={item.dish} className="flex justify-between items-start gap-4 pb-5 border-b border-gray-100 dark:border-gray-800 last:border-0">
                                        <div>
                                            <h4 className="font-semibold text-lg">{item.dish}</h4>
                                            <p className="text-sm text-gray-500 mt-0.5">{item.desc}</p>
                                        </div>
                                        <span className="text-lg font-bold text-amber-600 whitespace-nowrap">{item.price}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Reservation CTA */}
            <section className="py-20 bg-gradient-to-br from-stone-900 to-amber-950 text-white">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
                    <h2 className="text-3xl sm:text-4xl font-bold mb-4">Reserve Your Table</h2>
                    <p className="text-stone-300 text-lg mb-8 max-w-lg mx-auto">Walk-ins welcome, but reservations are recommended — especially on weekends. Book online or call us directly.</p>
                    <div className="flex flex-wrap justify-center gap-4">
                        <span className="px-7 py-3 bg-amber-500 text-stone-900 rounded-xl font-bold cursor-pointer hover:bg-amber-400 transition-colors shadow-lg">Book Online Now</span>
                        <span className="px-7 py-3 border border-stone-500 rounded-xl font-semibold cursor-pointer hover:bg-stone-800 transition-colors">(415) 555-0234</span>
                    </div>
                </div>
            </section>

            {/* Hours & Location */}
            <section className="py-24">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 grid md:grid-cols-2 gap-12">
                    <div>
                        <h2 className="text-2xl font-bold mb-6">Hours</h2>
                        <div className="space-y-4">
                            {HOURS.map((h) => (
                                <div key={h.day} className="flex justify-between gap-4 pb-3 border-b border-gray-100 dark:border-gray-800">
                                    <span className="font-medium">{h.day}</span>
                                    <span className="text-gray-500 text-sm text-right">{h.time}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold mb-6">Find Us</h2>
                        <div className="bg-gray-50 dark:bg-gray-900 rounded-2xl p-8 border border-gray-200 dark:border-gray-800">
                            <p className="font-semibold text-lg mb-1">The Artisan Kitchen</p>
                            <p className="text-gray-500 mb-4">728 Valencia Street<br />San Francisco, CA 94110</p>
                            <p className="text-sm text-gray-500 mb-1">hello@theartisankitchen.com</p>
                            <p className="text-sm text-gray-500">(415) 555-0234</p>
                            <div className="mt-6 h-32 rounded-xl bg-gradient-to-br from-stone-200 to-stone-300 dark:from-stone-700 dark:to-stone-800 flex items-center justify-center text-sm text-stone-500 dark:text-stone-400">Map Preview</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Reviews */}
            <section className="py-24 bg-stone-50 dark:bg-gray-900/50">
                <div className="max-w-5xl mx-auto px-4 sm:px-6">
                    <h2 className="text-3xl font-bold text-center mb-12">What Our Guests Say</h2>
                    <div className="grid sm:grid-cols-3 gap-6">
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
            <footer className="py-12 bg-stone-900 text-stone-400 text-center text-sm">
                <p className="mb-2">The Artisan Kitchen · 728 Valencia Street · San Francisco, CA 94110</p>
                <p>(415) 555-0234 · hello@theartisankitchen.com</p>
                <p className="mt-4 text-stone-500">Sample page created with <Link href="/" className="text-blue-400 hover:underline">AgentBloom</Link></p>
            </footer>
        </main>
    );
}
