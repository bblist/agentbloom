"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: "🏠" },
  { label: "Agent Chat", href: "/dashboard/agent", icon: "🤖" },
  { label: "Sites", href: "/dashboard/sites", icon: "🌐" },
  { label: "Email & CRM", href: "/dashboard/crm", icon: "📧" },
  { label: "Courses", href: "/dashboard/courses", icon: "📚" },
  { label: "Bookings", href: "/dashboard/bookings", icon: "📅" },
  { label: "Payments", href: "/dashboard/payments", icon: "💳" },
  { label: "SEO", href: "/dashboard/seo", icon: "📊" },
  { label: "Settings", href: "/dashboard/settings", icon: "⚙️" },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950">
      {/* Sidebar */}
      <aside className="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col">
        {/* Logo */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <Link href="/dashboard">
            <h1 className="text-xl font-bold">
              <span className="text-blue-600">Agent</span>
              <span className="text-emerald-500">Bloom</span>
            </h1>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-400"
                    : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* User menu footer */}
        <div className="p-3 border-t border-gray-200 dark:border-gray-800">
          <button className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            <span className="text-lg">👤</span>
            Account
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
