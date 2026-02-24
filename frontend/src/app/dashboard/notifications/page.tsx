"use client";

import { useEffect, useState } from "react";
import { notificationsAPI } from "@/lib/api";
import { shapeIcon, emptyStateAvatar, userAvatar } from "@/lib/dicebear";

interface Notification {
    id: string;
    title: string;
    body: string;
    category: string;
    is_read: boolean;
    created_at: string;
    action_url?: string;
}

interface NotificationPreferences {
    email_enabled: boolean;
    push_enabled: boolean;
    marketing_enabled: boolean;
    digest_frequency: string;
}

export default function NotificationsPage() {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
    const [activeTab, setActiveTab] = useState<"inbox" | "preferences">("inbox");
    const [filter, setFilter] = useState<"all" | "unread">("all");

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        try {
            const [notifRes, prefsRes] = await Promise.all([
                notificationsAPI.list().catch(() => ({ data: [] })),
                notificationsAPI.preferences().catch(() => ({ data: null })),
            ]);
            setNotifications(notifRes.data?.results || notifRes.data || []);
            setPreferences(prefsRes.data);
        } catch (e) {
            console.error("Failed to load notifications", e);
        }
    }

    async function markRead(id: string) {
        try {
            await notificationsAPI.markRead(id);
            setNotifications((prev) =>
                prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
            );
        } catch (err) {
            console.error("Mark read failed", err);
        }
    }

    async function markAllRead() {
        try {
            await notificationsAPI.markAllRead();
            setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
        } catch (err) {
            console.error("Mark all read failed", err);
        }
    }

    async function updatePreference(key: string, value: boolean | string) {
        if (!preferences) return;
        const updated = { ...preferences, [key]: value };
        setPreferences(updated);
        try {
            await notificationsAPI.updatePreferences(updated);
        } catch (err) {
            console.error("Preference update failed", err);
        }
    }

    const filtered =
        filter === "unread" ? notifications.filter((n) => !n.is_read) : notifications;
    const unreadCount = notifications.filter((n) => !n.is_read).length;

    const categoryColor: Record<string, string> = {
        system: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
        billing: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
        support: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
        agent: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
        marketing: "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400",
    };

    return (
        <div className="p-4 sm:p-8">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold">Notifications</h1>
                    <p className="mt-1 text-gray-500">
                        {unreadCount > 0
                            ? `${unreadCount} unread notification${unreadCount > 1 ? "s" : ""}`
                            : "You're all caught up"}
                    </p>
                </div>
                {unreadCount > 0 && activeTab === "inbox" && (
                    <button
                        onClick={markAllRead}
                        className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 font-medium"
                    >
                        Mark all as read
                    </button>
                )}
            </div>

            {/* Tabs */}
            <div className="flex gap-1 mb-6 bg-gray-100 dark:bg-gray-800 rounded-lg p-1 w-fit">
                {(["inbox", "preferences"] as const).map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 rounded-md text-sm font-medium capitalize transition-colors ${
                            activeTab === tab
                                ? "bg-white dark:bg-gray-700 shadow-sm"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        {tab}
                    </button>
                ))}
            </div>

            {activeTab === "inbox" && (
                <>
                    {/* Filter */}
                    <div className="flex gap-3 mb-4">
                        {(["all", "unread"] as const).map((f) => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-3 py-1.5 text-sm rounded-lg capitalize ${
                                    filter === f
                                        ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 font-medium"
                                        : "text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
                                }`}
                            >
                                {f} {f === "unread" && unreadCount > 0 && `(${unreadCount})`}
                            </button>
                        ))}
                    </div>

                    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                        {filtered.length === 0 ? (
                            <div className="p-12 text-center">
                                <img
                                    src={emptyStateAvatar("notif-empty")}
                                    alt=""
                                    className="w-20 h-20 mx-auto mb-4 rounded-full"
                                />
                                <h3 className="text-lg font-semibold mb-2">
                                    {filter === "unread" ? "No unread notifications" : "No notifications yet"}
                                </h3>
                                <p className="text-gray-500">
                                    {filter === "unread"
                                        ? "You've read all your notifications."
                                        : "Notifications about your account, subscriptions, and agent activity will appear here."}
                                </p>
                            </div>
                        ) : (
                            <div className="divide-y divide-gray-200 dark:divide-gray-800">
                                {filtered.map((notif) => (
                                    <div
                                        key={notif.id}
                                        onClick={() => !notif.is_read && markRead(notif.id)}
                                        className={`p-4 flex items-start gap-4 cursor-pointer transition-colors ${
                                            notif.is_read
                                                ? "hover:bg-gray-50 dark:hover:bg-gray-800/50"
                                                : "bg-blue-50/50 dark:bg-blue-950/20 hover:bg-blue-50 dark:hover:bg-blue-950/30"
                                        }`}
                                    >
                                        <img
                                            src={shapeIcon(`notif-${notif.category}-${notif.id}`)}
                                            alt=""
                                            className="w-10 h-10 rounded-lg mt-0.5"
                                        />
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-1">
                                                <p className={`text-sm ${notif.is_read ? "" : "font-semibold"}`}>
                                                    {notif.title}
                                                </p>
                                                {notif.category && (
                                                    <span
                                                        className={`px-2 py-0.5 rounded-full text-xs ${
                                                            categoryColor[notif.category] ||
                                                            "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                                                        }`}
                                                    >
                                                        {notif.category}
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-sm text-gray-500 line-clamp-2">{notif.body}</p>
                                            <p className="text-xs text-gray-400 mt-1">
                                                {new Date(notif.created_at).toLocaleString()}
                                            </p>
                                        </div>
                                        {!notif.is_read && (
                                            <span className="w-2.5 h-2.5 rounded-full bg-blue-500 mt-2 flex-shrink-0" />
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </>
            )}

            {activeTab === "preferences" && preferences && (
                <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-6">
                    <h3 className="text-lg font-semibold">Notification Preferences</h3>

                    {[
                        {
                            key: "email_enabled",
                            label: "Email Notifications",
                            description: "Receive notifications via email",
                            value: preferences.email_enabled,
                        },
                        {
                            key: "push_enabled",
                            label: "Push Notifications",
                            description: "Receive browser push notifications",
                            value: preferences.push_enabled,
                        },
                        {
                            key: "marketing_enabled",
                            label: "Marketing Emails",
                            description: "Product updates and feature announcements",
                            value: preferences.marketing_enabled,
                        },
                    ].map((pref) => (
                        <div
                            key={pref.key}
                            className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-800 last:border-0"
                        >
                            <div>
                                <p className="font-medium text-sm">{pref.label}</p>
                                <p className="text-xs text-gray-500">{pref.description}</p>
                            </div>
                            <button
                                onClick={() => updatePreference(pref.key, !pref.value)}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                                    pref.value ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"
                                }`}
                            >
                                <span
                                    className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                                        pref.value ? "translate-x-6" : "translate-x-1"
                                    }`}
                                />
                            </button>
                        </div>
                    ))}

                    <div className="pt-3">
                        <label className="block text-sm font-medium mb-2">Digest Frequency</label>
                        <select
                            value={preferences.digest_frequency}
                            onChange={(e) => updatePreference("digest_frequency", e.target.value)}
                            className="w-full max-w-xs px-4 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                        >
                            <option value="realtime">Real-time</option>
                            <option value="hourly">Hourly digest</option>
                            <option value="daily">Daily digest</option>
                            <option value="weekly">Weekly digest</option>
                        </select>
                    </div>
                </div>
            )}
        </div>
    );
}
