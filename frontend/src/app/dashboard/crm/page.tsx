export default function CRMPage() {
    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-2">📧 Email & CRM</h1>
            <p className="text-gray-500 mb-8">Manage contacts, send campaigns, and track deals</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {[
                    { label: "Contacts", value: "0", icon: "👥" },
                    { label: "Campaigns", value: "0", icon: "📨" },
                    { label: "Deals", value: "0", icon: "💰" },
                ].map((stat) => (
                    <div key={stat.label} className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-500">{stat.label}</span>
                            <span className="text-2xl">{stat.icon}</span>
                        </div>
                        <span className="text-3xl font-bold">{stat.value}</span>
                    </div>
                ))}
            </div>
            <div className="p-8 text-center bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                <div className="text-5xl mb-4">📧</div>
                <h2 className="text-xl font-semibold mb-2">Coming in Phase 2</h2>
                <p className="text-gray-500">Contact management, email campaigns, CRM pipeline, and more</p>
            </div>
        </div>
    );
}
