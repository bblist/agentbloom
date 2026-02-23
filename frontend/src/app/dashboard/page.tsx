export default function DashboardPage() {
  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Welcome to AgentBloom</h1>
        <p className="mt-2 text-gray-500">
          Your AI-powered business command center
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[
          { label: "Sites", value: "0", icon: "🌐" },
          { label: "Contacts", value: "0", icon: "👥" },
          { label: "Bookings", value: "0", icon: "📅" },
          { label: "Revenue", value: "$0", icon: "💰" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">{stat.label}</span>
              <span className="text-2xl">{stat.icon}</span>
            </div>
            <span className="text-3xl font-bold">{stat.value}</span>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-xl text-left hover:bg-blue-100 dark:hover:bg-blue-950/50 transition-colors">
            <span className="text-2xl mb-2 block">🤖</span>
            <span className="font-semibold text-blue-700 dark:text-blue-400">
              Talk to your AI Agent
            </span>
            <p className="text-sm text-gray-500 mt-1">
              Build pages, send emails, manage bookings — just ask
            </p>
          </button>
          <button className="p-4 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 rounded-xl text-left hover:bg-emerald-100 dark:hover:bg-emerald-950/50 transition-colors">
            <span className="text-2xl mb-2 block">🌐</span>
            <span className="font-semibold text-emerald-700 dark:text-emerald-400">
              Create a Website
            </span>
            <p className="text-sm text-gray-500 mt-1">
              Pick a template or let AI build one based on your niche
            </p>
          </button>
          <button className="p-4 bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 rounded-xl text-left hover:bg-purple-100 dark:hover:bg-purple-950/50 transition-colors">
            <span className="text-2xl mb-2 block">📧</span>
            <span className="font-semibold text-purple-700 dark:text-purple-400">
              Import Contacts
            </span>
            <p className="text-sm text-gray-500 mt-1">
              Upload a CSV or add contacts manually to get started
            </p>
          </button>
        </div>
      </div>

      {/* Getting Started Checklist */}
      <div className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
        <h2 className="text-lg font-semibold mb-4">Getting Started</h2>
        <ul className="space-y-3">
          {[
            { text: "Set up your business info", done: false },
            { text: "Choose branding & colors", done: false },
            { text: "Pick a website template", done: false },
            { text: "Connect a custom domain", done: false },
            { text: "Chat with your AI agent", done: false },
            { text: "Take the platform tour", done: false },
          ].map((step, i) => (
            <li key={i} className="flex items-center gap-3">
              <span
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                  step.done
                    ? "bg-emerald-100 dark:bg-emerald-900 text-emerald-600"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-400"
                }`}
              >
                {step.done ? "✓" : i + 1}
              </span>
              <span className={step.done ? "line-through text-gray-400" : ""}>
                {step.text}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
