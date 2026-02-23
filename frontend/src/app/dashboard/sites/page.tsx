"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { sitesAPI } from "@/lib/api";

interface Site {
    id: string;
    name: string;
    slug: string;
    status: "draft" | "published" | "archived";
    custom_domain: string;
    page_count?: number;
    created_at: string;
    published_at?: string;
}

export default function SitesPage() {
    const [sites, setSites] = useState<Site[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const { data } = await sitesAPI.list();
                setSites(data.results || data || []);
            } catch {
                /* Not logged in */
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    const statusBadge = (status: string) => {
        const colors: Record<string, string> = {
            draft: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
            published: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
            archived: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
        };
        return (
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${colors[status] || colors.draft}`}>
                {status}
            </span>
        );
    };

    return (
        <div className="p-8">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold">🌐 Websites</h1>
                    <p className="mt-1 text-gray-500">Manage your published sites and pages</p>
                </div>
                <Link
                    href="/dashboard/agent"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors text-sm"
                >
                    + Ask Agent to Build
                </Link>
            </div>

            {/* Sites Grid */}
            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-48 bg-gray-100 dark:bg-gray-800 rounded-xl animate-pulse" />
                    ))}
                </div>
            ) : sites.length === 0 ? (
                <div className="text-center py-16">
                    <div className="text-5xl mb-4">🌐</div>
                    <h2 className="text-xl font-semibold mb-2">No sites yet</h2>
                    <p className="text-gray-500 mb-6">
                        Ask your AI agent to build your first website
                    </p>
                    <Link
                        href="/dashboard/agent"
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
                    >
                        Start Building
                    </Link>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {sites.map((site) => (
                        <div
                            key={site.id}
                            className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden hover:shadow-lg transition-shadow"
                        >
                            {/* Preview area */}
                            <div className="h-36 bg-gradient-to-br from-blue-100 to-indigo-200 dark:from-blue-950 dark:to-indigo-950 flex items-center justify-center">
                                <span className="text-4xl opacity-60">🌐</span>
                            </div>

                            {/* Info */}
                            <div className="p-4">
                                <div className="flex items-center justify-between mb-2">
                                    <h3 className="font-semibold truncate">{site.name}</h3>
                                    {statusBadge(site.status)}
                                </div>
                                <p className="text-sm text-gray-500 mb-3">
                                    {site.custom_domain || `${site.slug}.agentbloom.com`}
                                </p>
                                <div className="flex gap-2">
                                    <Link
                                        href={`/dashboard/sites/${site.id}`}
                                        className="text-sm px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700"
                                    >
                                        Manage
                                    </Link>
                                    <Link
                                        href={`/dashboard/sites/${site.id}/pages`}
                                        className="text-sm px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700"
                                    >
                                        Pages
                                    </Link>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
