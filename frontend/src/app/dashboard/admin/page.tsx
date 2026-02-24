"use client";

import { useEffect, useState } from "react";
import { adminAPI } from "@/lib/api";
import { shapeIcon, emptyStateAvatar, userAvatar } from "@/lib/dicebear";

interface FeatureFlag {
    id: string;
    name: string;
    key: string;
    enabled: boolean;
    description: string;
    rollout_percentage: number;
}

interface SupportTicket {
    id: string;
    subject: string;
    status: string;
    priority: string;
    user_email: string;
    created_at: string;
    updated_at: string;
}

interface SystemHealth {
    database: string;
    redis: string;
    celery: string;
    disk_usage: number;
    memory_usage: number;
    uptime: string;
}

interface AuditEntry {
    id: string;
    action: string;
    user_email: string;
    resource_type: string;
    resource_id: string;
    timestamp: string;
}

export default function AdminPanelPage() {
    const [activeTab, setActiveTab] = useState<
        "overview" | "flags" | "tickets" | "moderation" | "audit"
    >("overview");
    const [flags, setFlags] = useState<FeatureFlag[]>([]);
    const [tickets, setTickets] = useState<SupportTicket[]>([]);
    const [health, setHealth] = useState<SystemHealth | null>(null);
    const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
    const [users, setUsers] = useState<{ id: string; email: string; full_name: string; plan: string; created_at: string }[]>([]);

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        try {
            const [flagsRes, ticketsRes, healthRes, auditRes, usersRes] = await Promise.all([
                adminAPI.featureFlags().catch(() => ({ data: [] })),
                adminAPI.supportTickets().catch(() => ({ data: [] })),
                adminAPI.systemHealth().catch(() => ({ data: null })),
                adminAPI.auditLog().catch(() => ({ data: [] })),
                adminAPI.users().catch(() => ({ data: [] })),
            ]);
            setFlags(flagsRes.data?.results || flagsRes.data || []);
            setTickets(ticketsRes.data?.results || ticketsRes.data || []);
            setHealth(healthRes.data);
            setAuditLog(auditRes.data?.results || auditRes.data || []);
            setUsers(usersRes.data?.results || usersRes.data || []);
        } catch (e) {
            console.error("Failed to load admin data", e);
        }
    }

    async function toggleFlag(flag: FeatureFlag) {
        try {
            await adminAPI.updateFeatureFlag(flag.id, { enabled: !flag.enabled });
            setFlags((prev) =>
                prev.map((f) => (f.id === flag.id ? { ...f, enabled: !f.enabled } : f))
            );
        } catch (err) {
            console.error("Toggle failed", err);
        }
    }

    async function updateTicketStatus(id: string, newStatus: string) {
        try {
            await adminAPI.updateTicket(id, { status: newStatus });
            setTickets((prev) =>
                prev.map((t) => (t.id === id ? { ...t, status: newStatus } : t))
            );
        } catch (err) {
            console.error("Status update failed", err);
        }
    }

    const statusColor: Record<string, string> = {
        open: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
        in_progress: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
        resolved: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
        closed: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
    };

    const priorityColor: Record<string, string> = {
        low: "text-gray-500",
        medium: "text-yellow-600",
        high: "text-orange-600",
        urgent: "text-red-600 font-bold",
    };

    const healthColor = (status: string) =>
        status === "healthy" || status === "ok"
            ? "text-green-600"
            : status === "warning"
                ? "text-yellow-600"
                : "text-red-600";

    return (
        <div className="p-4 sm:p-8">
            <div className="mb-8">
                <h1 className="text-2xl sm:text-3xl font-bold">Admin Panel</h1>
                <p className="mt-1 text-gray-500">
                    System administration, feature flags, support, and monitoring
                </p>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 mb-6 bg-gray-100 dark:bg-gray-800 rounded-lg p-1 w-fit">
                {(["overview", "flags", "tickets", "moderation", "audit"] as const).map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 rounded-md text-sm font-medium capitalize transition-colors ${
                            activeTab === tab
                                ? "bg-white dark:bg-gray-700 shadow-sm"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        {tab === "flags" ? "Feature Flags" : tab}
                    </button>
                ))}
            </div>

            {/* Overview Tab */}
            {activeTab === "overview" && (
                <div className="space-y-6">
                    {/* Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        {[
                            { label: "Total Users", value: users.length.toString(), seed: "admin-users" },
                            { label: "Open Tickets", value: tickets.filter((t) => t.status === "open").length.toString(), seed: "admin-tickets" },
                            { label: "Feature Flags", value: flags.filter((f) => f.enabled).length.toString() + ` / ${flags.length}`, seed: "admin-flags" },
                            { label: "System Status", value: health ? "Operational" : "Unknown", seed: "admin-health" },
                        ].map((stat) => (
                            <div
                                key={stat.label}
                                className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800"
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm text-gray-500">{stat.label}</span>
                                    <img src={shapeIcon(stat.seed)} alt="" className="w-10 h-10 rounded-lg" />
                                </div>
                                <span className="text-2xl font-bold">{stat.value}</span>
                            </div>
                        ))}
                    </div>

                    {/* System Health */}
                    {health && (
                        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
                            <h3 className="text-lg font-semibold mb-4">System Health</h3>
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                                {[
                                    { label: "Database", value: health.database },
                                    { label: "Redis", value: health.redis },
                                    { label: "Celery", value: health.celery },
                                    { label: "Disk Usage", value: `${health.disk_usage || 0}%` },
                                    { label: "Memory", value: `${health.memory_usage || 0}%` },
                                ].map((item) => (
                                    <div key={item.label} className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                                        <p className="text-xs text-gray-500 mb-1">{item.label}</p>
                                        <p className={`text-sm font-semibold ${healthColor(String(item.value))}`}>
                                            {item.value}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Recent Users */}
                    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
                        <h3 className="text-lg font-semibold mb-4">Recent Users</h3>
                        {users.length === 0 ? (
                            <p className="text-gray-500 text-sm">No users yet.</p>
                        ) : (
                            <div className="space-y-3">
                                {users.slice(0, 10).map((user) => (
                                    <div
                                        key={user.id}
                                        className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
                                    >
                                        <div className="flex items-center gap-3">
                                            <img
                                                src={userAvatar(user.email)}
                                                alt=""
                                                className="w-9 h-9 rounded-full"
                                            />
                                            <div>
                                                <p className="text-sm font-medium">{user.full_name || user.email}</p>
                                                <p className="text-xs text-gray-500">{user.email}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <span className="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
                                                {user.plan || "free"}
                                            </span>
                                            <span className="text-xs text-gray-500">
                                                {new Date(user.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Feature Flags Tab */}
            {activeTab === "flags" && (
                <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                    {flags.length === 0 ? (
                        <div className="p-12 text-center">
                            <img
                                src={emptyStateAvatar("admin-flags-empty")}
                                alt=""
                                className="w-20 h-20 mx-auto mb-4 rounded-full"
                            />
                            <h3 className="text-lg font-semibold mb-2">No feature flags</h3>
                            <p className="text-gray-500">
                                Feature flags will appear here once created via the management commands.
                            </p>
                        </div>
                    ) : (
                        <div className="divide-y divide-gray-200 dark:divide-gray-800">
                            {flags.map((flag) => (
                                <div
                                    key={flag.id}
                                    className="p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50"
                                >
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3">
                                            <p className="font-medium">{flag.name}</p>
                                            <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded text-gray-600 dark:text-gray-400">
                                                {flag.key}
                                            </code>
                                        </div>
                                        <p className="text-sm text-gray-500 mt-1">{flag.description}</p>
                                        {flag.rollout_percentage < 100 && (
                                            <p className="text-xs text-gray-400 mt-1">
                                                Rollout: {flag.rollout_percentage}%
                                            </p>
                                        )}
                                    </div>
                                    <button
                                        onClick={() => toggleFlag(flag)}
                                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                                            flag.enabled ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"
                                        }`}
                                    >
                                        <span
                                            className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                                                flag.enabled ? "translate-x-6" : "translate-x-1"
                                            }`}
                                        />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Tickets Tab */}
            {activeTab === "tickets" && (
                <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                    {tickets.length === 0 ? (
                        <div className="p-12 text-center">
                            <img
                                src={emptyStateAvatar("admin-tickets-empty")}
                                alt=""
                                className="w-20 h-20 mx-auto mb-4 rounded-full"
                            />
                            <h3 className="text-lg font-semibold mb-2">No support tickets</h3>
                            <p className="text-gray-500">All clear! No tickets to review.</p>
                        </div>
                    ) : (
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200 dark:border-gray-800">
                                    <th className="text-left p-4 text-sm font-medium text-gray-500">Subject</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-500">User</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-500">Priority</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-500">Status</th>
                                    <th className="text-right p-4 text-sm font-medium text-gray-500">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tickets.map((ticket) => (
                                    <tr
                                        key={ticket.id}
                                        className="border-b border-gray-100 dark:border-gray-800 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                                    >
                                        <td className="p-4">
                                            <p className="font-medium text-sm">{ticket.subject}</p>
                                            <p className="text-xs text-gray-500">
                                                {new Date(ticket.created_at).toLocaleDateString()}
                                            </p>
                                        </td>
                                        <td className="p-4">
                                            <div className="flex items-center gap-2">
                                                <img
                                                    src={userAvatar(ticket.user_email)}
                                                    alt=""
                                                    className="w-7 h-7 rounded-full"
                                                />
                                                <span className="text-sm">{ticket.user_email}</span>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <span className={`text-sm ${priorityColor[ticket.priority] || ""}`}>
                                                {ticket.priority}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            <span
                                                className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                                                    statusColor[ticket.status] || statusColor.open
                                                }`}
                                            >
                                                {ticket.status.replace("_", " ")}
                                            </span>
                                        </td>
                                        <td className="p-4 text-right">
                                            <select
                                                value={ticket.status}
                                                onChange={(e) => updateTicketStatus(ticket.id, e.target.value)}
                                                className="text-xs border border-gray-300 dark:border-gray-700 rounded-lg px-2 py-1 dark:bg-gray-800"
                                            >
                                                <option value="open">Open</option>
                                                <option value="in_progress">In Progress</option>
                                                <option value="resolved">Resolved</option>
                                                <option value="closed">Closed</option>
                                            </select>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}

            {/* Moderation Tab */}
            {activeTab === "moderation" && (
                <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-12 text-center">
                    <img
                        src={emptyStateAvatar("admin-moderation")}
                        alt=""
                        className="w-20 h-20 mx-auto mb-4 rounded-full"
                    />
                    <h3 className="text-lg font-semibold mb-2">Content Moderation</h3>
                    <p className="text-gray-500">
                        No content pending moderation. Flagged content from users will appear here.
                    </p>
                </div>
            )}

            {/* Audit Log Tab */}
            {activeTab === "audit" && (
                <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                    {auditLog.length === 0 ? (
                        <div className="p-12 text-center">
                            <img
                                src={emptyStateAvatar("admin-audit-empty")}
                                alt=""
                                className="w-20 h-20 mx-auto mb-4 rounded-full"
                            />
                            <h3 className="text-lg font-semibold mb-2">No audit entries</h3>
                            <p className="text-gray-500">System activity will be logged here.</p>
                        </div>
                    ) : (
                        <div className="divide-y divide-gray-200 dark:divide-gray-800">
                            {auditLog.map((entry) => (
                                <div
                                    key={entry.id}
                                    className="p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50"
                                >
                                    <div className="flex items-center gap-3">
                                        <img
                                            src={userAvatar(entry.user_email)}
                                            alt=""
                                            className="w-8 h-8 rounded-full"
                                        />
                                        <div>
                                            <p className="text-sm">
                                                <span className="font-medium">{entry.user_email}</span>{" "}
                                                <span className="text-gray-500">{entry.action}</span>{" "}
                                                <span className="font-medium">
                                                    {entry.resource_type} #{entry.resource_id}
                                                </span>
                                            </p>
                                        </div>
                                    </div>
                                    <span className="text-xs text-gray-500">
                                        {new Date(entry.timestamp).toLocaleString()}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
