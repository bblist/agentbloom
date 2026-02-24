"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { navIcon, userAvatar, agentAvatar } from "@/lib/dicebear";
import { useAuthStore } from "@/lib/store";
import { toast } from "sonner";

const navItems = [
    { label: "Dashboard", href: "/dashboard", seed: "dashboard-home" },
    { label: "Agent Chat", href: "/dashboard/agent", seed: "ai-agent-bot" },
    { label: "Sites", href: "/dashboard/sites", seed: "website-globe" },
    { label: "Email & CRM", href: "/dashboard/crm", seed: "email-crm-contacts" },
    { label: "Courses", href: "/dashboard/courses", seed: "courses-education" },
    { label: "Bookings", href: "/dashboard/bookings", seed: "calendar-bookings" },
    { label: "Payments", href: "/dashboard/payments", seed: "payments-stripe" },
    { label: "Knowledge Base", href: "/dashboard/kb", seed: "kb-documents" },
    { label: "SEO", href: "/dashboard/seo", seed: "seo-analytics" },
    { label: "Notifications", href: "/dashboard/notifications", seed: "notifications-bell" },
    { label: "Receptionist", href: "/dashboard/receptionist", seed: "receptionist-chat" },
    { label: "Webhooks", href: "/dashboard/webhooks", seed: "webhooks-api" },
    { label: "Admin Panel", href: "/dashboard/admin", seed: "admin-shield" },
    { label: "Settings", href: "/dashboard/settings", seed: "settings-gear" },
];

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    const router = useRouter();
    const { user, org, logout: doLogout } = useAuthStore();

    const handleLogout = () => {
        doLogout();
        toast.success("Logged out successfully");
        router.push("/auth/login");
    };

    return (
        <div className="flex h-screen bg-gray-50 dark:bg-gray-950">
            {/* Sidebar */}
            <aside className="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col">
                {/* Logo */}
                <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex items-center gap-3">
                    <img
                        src={agentAvatar("agentbloom-logo")}
                        alt=""
                        className="w-8 h-8 rounded-lg"
                    />
                    <Link href="/dashboard">
                        <h1 className="text-xl font-bold">
                            <span className="text-blue-600">Agent</span>
                            <span className="text-emerald-500">Bloom</span>
                        </h1>
                    </Link>
                </div>

                {/* Org selector */}
                {org && (
                    <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-800">
                        <p className="text-xs text-gray-500 dark:text-gray-500">Organization</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                            {org.name}
                        </p>
                    </div>
                )}

                {/* Navigation */}
                <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
                    {navItems.map((item) => {
                        const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive
                                        ? "bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-400"
                                        : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
                                    }`}
                            >
                                <img
                                    src={navIcon(item.seed)}
                                    alt=""
                                    className="w-6 h-6 rounded"
                                />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>

                {/* User menu footer */}
                <div className="p-3 border-t border-gray-200 dark:border-gray-800 space-y-1">
                    <div className="flex items-center gap-3 px-3 py-2">
                        <img
                            src={userAvatar(user?.email || "current-user")}
                            alt=""
                            className="w-7 h-7 rounded-full"
                        />
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                                {user ? `${user.first_name} ${user.last_name}`.trim() || user.email : "Account"}
                            </p>
                            {user?.email && (
                                <p className="text-xs text-gray-500 dark:text-gray-500 truncate">
                                    {user.email}
                                </p>
                            )}
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
                    >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        Sign Out
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
