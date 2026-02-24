"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { sitesAPI } from "@/lib/api";
import { toast } from "sonner";

interface Site {
    id: string;
    name: string;
    slug: string;
    status: string;
    custom_domain: string;
    theme_config: Record<string, unknown>;
    created_at: string;
}

interface Page {
    id: string;
    title: string;
    slug: string;
    page_type: string;
    is_published: boolean;
    sort_order: number;
    created_at: string;
}

export default function SiteDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const [site, setSite] = useState<Site | null>(null);
    const [pages, setPages] = useState<Page[]>([]);
    const [loading, setLoading] = useState(true);
    const [tab, setTab] = useState<"pages" | "settings" | "domain">("pages");
    const [showNewPage, setShowNewPage] = useState(false);
    const [newPage, setNewPage] = useState({ title: "", slug: "", page_type: "landing" });
    const [editingSite, setEditingSite] = useState({ name: "", slug: "", custom_domain: "" });

    useEffect(() => {
        loadSite();
    }, [id]);

    async function loadSite() {
        setLoading(true);
        try {
            const [siteRes, pagesRes] = await Promise.all([
                sitesAPI.get(id),
                sitesAPI.pages(id),
            ]);
            setSite(siteRes.data);
            setPages(pagesRes.data?.results || pagesRes.data || []);
            setEditingSite({
                name: siteRes.data.name,
                slug: siteRes.data.slug,
                custom_domain: siteRes.data.custom_domain || "",
            });
        } catch {
            toast.error("Failed to load site");
        } finally {
            setLoading(false);
        }
    }

    async function createPage() {
        if (!newPage.title) return;
        try {
            await sitesAPI.createPage(id, {
                ...newPage,
                slug: newPage.slug || newPage.title.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
            });
            toast.success("Page created!");
            setShowNewPage(false);
            setNewPage({ title: "", slug: "", page_type: "landing" });
            loadSite();
        } catch {
            toast.error("Failed to create page");
        }
    }

    async function publishSite() {
        try {
            await sitesAPI.publish(id);
            toast.success("Site published!");
            loadSite();
        } catch {
            toast.error("Failed to publish site");
        }
    }

    async function updateSite() {
        try {
            await sitesAPI.update(id, editingSite);
            toast.success("Site updated!");
            loadSite();
        } catch {
            toast.error("Failed to update");
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
            </div>
        );
    }

    if (!site) {
        return (
            <div className="p-4 sm:p-8 text-center">
                <p className="text-gray-500">Site not found</p>
                <Link href="/dashboard/sites" className="text-blue-600 hover:underline mt-2 inline-block">Back to Sites</Link>
            </div>
        );
    }

    return (
        <div className="p-4 sm:p-8 max-w-5xl mx-auto">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                <div>
                    <Link href="/dashboard/sites" className="text-sm text-blue-600 hover:underline mb-1 inline-block">&larr; Back to Sites</Link>
                    <h1 className="text-2xl sm:text-3xl font-bold">{site.name}</h1>
                    <p className="text-sm text-gray-500">{site.custom_domain || `${site.slug}.agentbloom.com`}</p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={publishSite}
                        className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700"
                    >
                        Publish Site
                    </button>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1 mb-6 overflow-x-auto">
                {(["pages", "settings", "domain"] as const).map((t) => (
                    <button
                        key={t}
                        onClick={() => setTab(t)}
                        className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap ${
                            tab === t
                                ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                                : "text-gray-600 dark:text-gray-400"
                        }`}
                    >
                        {t === "pages" ? "Pages" : t === "settings" ? "Site Settings" : "Custom Domain"}
                    </button>
                ))}
            </div>

            {/* Pages Tab */}
            {tab === "pages" && (
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h2 className="font-semibold text-lg">{pages.length} Pages</h2>
                        <button
                            onClick={() => setShowNewPage(true)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
                        >
                            + Add Page
                        </button>
                    </div>

                    {/* New page form */}
                    {showNewPage && (
                        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4 space-y-3">
                            <h3 className="font-medium">New Page</h3>
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                <input
                                    type="text"
                                    value={newPage.title}
                                    onChange={(e) => setNewPage({ ...newPage, title: e.target.value })}
                                    placeholder="Page title"
                                    className="px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                />
                                <input
                                    type="text"
                                    value={newPage.slug}
                                    onChange={(e) => setNewPage({ ...newPage, slug: e.target.value })}
                                    placeholder="url-slug (auto)"
                                    className="px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                />
                                <select
                                    value={newPage.page_type}
                                    onChange={(e) => setNewPage({ ...newPage, page_type: e.target.value })}
                                    className="px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                >
                                    <option value="landing">Landing Page</option>
                                    <option value="sales">Sales Page</option>
                                    <option value="squeeze">Squeeze Page</option>
                                    <option value="thank_you">Thank You Page</option>
                                    <option value="webinar">Webinar Registration</option>
                                    <option value="blog">Blog Post</option>
                                    <option value="about">About Page</option>
                                    <option value="contact">Contact Page</option>
                                    <option value="custom">Custom Page</option>
                                </select>
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={createPage}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
                                >
                                    Create
                                </button>
                                <button
                                    onClick={() => setShowNewPage(false)}
                                    className="px-4 py-2 text-gray-600 text-sm"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Page list */}
                    {pages.length === 0 ? (
                        <div className="text-center py-12 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                            <p className="text-gray-500 mb-2">No pages yet</p>
                            <p className="text-sm text-gray-400">Create a page or ask your AI agent to build one</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {pages.map((page) => (
                                <div
                                    key={page.id}
                                    className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                                >
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <h3 className="font-medium">{page.title}</h3>
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                                                page.is_published
                                                    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                                                    : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                                            }`}>
                                                {page.is_published ? "Published" : "Draft"}
                                            </span>
                                            <span className="text-xs text-gray-400 capitalize">{page.page_type?.replace("_", " ")}</span>
                                        </div>
                                        <p className="text-sm text-gray-500">/{page.slug}</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <Link
                                            href={`/dashboard/sites/${id}/pages/${page.id}`}
                                            className="px-3 py-1.5 text-sm bg-blue-50 dark:bg-blue-950/30 text-blue-600 rounded-lg hover:bg-blue-100"
                                        >
                                            Edit
                                        </Link>
                                        <Link
                                            href={`/dashboard/sites/${id}/pages/${page.id}/preview`}
                                            className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200"
                                        >
                                            Preview
                                        </Link>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="bg-blue-50 dark:bg-blue-950/20 rounded-xl border border-blue-200 dark:border-blue-800 p-4">
                        <p className="text-sm text-blue-700 dark:text-blue-300">
                            <strong>Tip:</strong> Go to <Link href="/dashboard/agent" className="underline">Agent Chat</Link> and say
                            {" "}<em>&quot;Build me a landing page for {site.name}&quot;</em> — the AI will design and create it for you.
                        </p>
                    </div>
                </div>
            )}

            {/* Settings Tab */}
            {tab === "settings" && (
                <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-1">Site Name</label>
                        <input
                            type="text"
                            value={editingSite.name}
                            onChange={(e) => setEditingSite({ ...editingSite, name: e.target.value })}
                            className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1">Site Slug</label>
                        <input
                            type="text"
                            value={editingSite.slug}
                            onChange={(e) => setEditingSite({ ...editingSite, slug: e.target.value })}
                            className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                        />
                    </div>
                    <button
                        onClick={updateSite}
                        className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
                    >
                        Save
                    </button>
                </div>
            )}

            {/* Domain Tab */}
            {tab === "domain" && (
                <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                    <h3 className="font-semibold">Custom Domain</h3>
                    <p className="text-sm text-gray-500">Point your domain to AgentBloom to use a custom URL for your site.</p>
                    <div>
                        <label className="block text-sm font-medium mb-1">Domain</label>
                        <input
                            type="text"
                            value={editingSite.custom_domain}
                            onChange={(e) => setEditingSite({ ...editingSite, custom_domain: e.target.value })}
                            placeholder="www.yourdomain.com"
                            className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                        />
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                        <p className="text-sm font-medium mb-2">DNS Configuration</p>
                        <p className="text-xs text-gray-500 font-mono">
                            CNAME record: {editingSite.custom_domain || "yourdomain.com"} → sites.agentbloom.com
                        </p>
                    </div>
                    <button
                        onClick={updateSite}
                        className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
                    >
                        Save Domain
                    </button>
                </div>
            )}
        </div>
    );
}
