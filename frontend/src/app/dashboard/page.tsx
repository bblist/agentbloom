"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { sitesAPI, crmAPI, bookingsAPI, paymentsAPI } from "@/lib/api";
import { shapeIcon, agentAvatar, thumbnailAvatar, emptyStateAvatar } from "@/lib/dicebear";

interface Stats {
    sites: number;
    contacts: number;
    bookings: number;
    revenue: number;
}

export default function DashboardPage() {
    const [stats, setStats] = useState<Stats>({ sites: 0, contacts: 0, bookings: 0, revenue: 0 });

    useEffect(() => {
        async function loadStats() {
            try {
                const [s, c, b, p] = await Promise.all([
                    sitesAPI.list().catch(() => ({ data: [] })),
                    crmAPI.contacts().catch(() => ({ data: [] })),
                    bookingsAPI.bookings().catch(() => ({ data: [] })),
                    paymentsAPI.payments().catch(() => ({ data: [] })),
                ]);
                const siteList = s.data?.results || s.data || [];
                const contactList = c.data?.results || c.data || [];
                const bookingList = b.data?.results || b.data || [];
                const paymentList = p.data?.results || p.data || [];
                const rev = paymentList
                    .filter((p: { status: string }) => p.status === "completed")
                    .reduce((sum: number, p: { amount: string }) => sum + parseFloat(p.amount || "0"), 0);
                setStats({
                    sites: siteList.length,
                    contacts: contactList.length,
                    bookings: bookingList.length,
                    revenue: rev,
                });
            } catch (e) {
                console.error("Failed to load dashboard stats", e);
            }
        }
        loadStats();
    }, []);
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
                    { label: "Sites", value: stats.sites.toString(), seed: "stat-sites-globe" },
                    { label: "Contacts", value: stats.contacts.toString(), seed: "stat-contacts-people" },
                    { label: "Bookings", value: stats.bookings.toString(), seed: "stat-bookings-calendar" },
                    { label: "Revenue", value: `$${stats.revenue.toFixed(2)}`, seed: "stat-revenue-money" },
                ].map((stat) => (
                    <div
                        key={stat.label}
                        className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800"
                    >
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-500">{stat.label}</span>
                            <img src={shapeIcon(stat.seed)} alt="" className="w-10 h-10 rounded-lg" />
                        </div>
                        <span className="text-3xl font-bold">{stat.value}</span>
                    </div>
                ))}
            </div>

            {/* Quick Actions */}
            <div className="mb-8">
                <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Link href="/dashboard/agent" className="p-4 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-xl text-left hover:bg-blue-100 dark:hover:bg-blue-950/50 transition-colors">
                        <img src={agentAvatar("quick-action-agent")} alt="" className="w-10 h-10 rounded-xl mb-2" />
                        <span className="font-semibold text-blue-700 dark:text-blue-400">
                            Talk to your AI Agent
                        </span>
                        <p className="text-sm text-gray-500 mt-1">
                            Build pages, send emails, manage bookings — just ask
                        </p>
                    </Link>
                    <Link href="/dashboard/sites" className="p-4 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 rounded-xl text-left hover:bg-emerald-100 dark:hover:bg-emerald-950/50 transition-colors">
                        <img src={thumbnailAvatar("quick-action-sites")} alt="" className="w-10 h-10 rounded-xl mb-2" />
                        <span className="font-semibold text-emerald-700 dark:text-emerald-400">
                            Create a Website
                        </span>
                        <p className="text-sm text-gray-500 mt-1">
                            Pick a template or let AI build one based on your niche
                        </p>
                    </Link>
                    <Link href="/dashboard/crm" className="p-4 bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 rounded-xl text-left hover:bg-purple-100 dark:hover:bg-purple-950/50 transition-colors">
                        <img src={emptyStateAvatar("quick-action-crm")} alt="" className="w-10 h-10 rounded-xl mb-2" />
                        <span className="font-semibold text-purple-700 dark:text-purple-400">
                            Import Contacts
                        </span>
                        <p className="text-sm text-gray-500 mt-1">
                            Upload a CSV or add contacts manually to get started
                        </p>
                    </Link>
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
                                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${step.done
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
