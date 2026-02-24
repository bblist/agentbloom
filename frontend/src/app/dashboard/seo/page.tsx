"use client";

import { useEffect, useState } from "react";
import { seoAPI, sitesAPI } from "@/lib/api";

interface Audit {
    id: string;
    overall_score: number;
    pages_analyzed: number;
    issues_found: number;
    issues: Array<{
        type: string;
        severity: string;
        message: string;
        slug: string;
    }>;
    created_at: string;
    status: string;
}

interface Keyword {
    id: string;
    keyword: string;
    current_position: number | null;
    previous_position: number | null;
    rank_change: number | null;
    search_volume: number | null;
    is_active: boolean;
}

interface Site {
    id: string;
    domain: string;
    name: string;
}

type Tab = "audits" | "keywords";

export default function SEOPage() {
    const [tab, setTab] = useState<Tab>("audits");
    const [audits, setAudits] = useState<Audit[]>([]);
    const [keywords, setKeywords] = useState<Keyword[]>([]);
    const [sites, setSites] = useState<Site[]>([]);
    const [selectedSite, setSelectedSite] = useState<string>("");
    const [loading, setLoading] = useState(true);
    const [runningAudit, setRunningAudit] = useState(false);
    const [newKeywords, setNewKeywords] = useState("");

    useEffect(() => {
        loadSites();
    }, []);

    async function loadSites() {
        try {
            const res = await sitesAPI.list();
            const siteList = res.data?.results || res.data || [];
            setSites(siteList);
            if (siteList.length > 0) {
                setSelectedSite(siteList[0].id);
            }
            loadData();
        } catch (e) {
            console.error("Failed to load sites", e);
            setLoading(false);
        }
    }

    async function loadData() {
        setLoading(true);
        try {
            const [a, k] = await Promise.all([
                seoAPI.audits().catch(() => ({ data: [] })),
                seoAPI.keywords().catch(() => ({ data: [] })),
            ]);
            setAudits(a.data?.results || a.data || []);
            setKeywords(k.data?.results || k.data || []);
        } catch (e) {
            console.error("Failed to load SEO data", e);
        } finally {
            setLoading(false);
        }
    }

    async function runAudit() {
        if (!selectedSite) return alert("Select a site first");
        setRunningAudit(true);
        try {
            await seoAPI.runAudit(selectedSite);
            await loadData();
        } catch (e) {
            console.error("Failed to run audit", e);
        } finally {
            setRunningAudit(false);
        }
    }

    async function addKeywords() {
        const kws = newKeywords.split(",").map((k) => k.trim()).filter(Boolean);
        if (kws.length === 0) return;
        try {
            await seoAPI.addKeywords({ keywords: kws });
            setNewKeywords("");
            loadData();
        } catch (e) {
            console.error("Failed to add keywords", e);
        }
    }

    async function generateSitemap() {
        if (!selectedSite) return;
        try {
            await seoAPI.generateSitemap(selectedSite);
            alert("Sitemap generated successfully!");
        } catch (e) {
            console.error("Failed to generate sitemap", e);
        }
    }

    const latestAudit = audits[0];
    const scoreColor = (score: number) => {
        if (score >= 80) return "text-green-600";
        if (score >= 50) return "text-yellow-600";
        return "text-red-600";
    };

    const severityBadge = (s: string) => {
        const styles: Record<string, string> = {
            high: "bg-red-100 text-red-700",
            medium: "bg-yellow-100 text-yellow-700",
            low: "bg-blue-100 text-blue-600",
        };
        return styles[s] || "bg-gray-100 text-gray-600";
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">SEO</h1>
                    <p className="text-gray-500 mt-1">Audit your site, track keywords, and optimize for search engines.</p>
                </div>
                <div className="flex gap-2">
                    {sites.length > 0 && (
                        <select
                            value={selectedSite}
                            onChange={(e) => setSelectedSite(e.target.value)}
                            className="px-3 py-2 text-sm border rounded-lg dark:bg-gray-800 dark:border-gray-600"
                        >
                            {sites.map((s) => (
                                <option key={s.id} value={s.id}>{s.name || s.domain}</option>
                            ))}
                        </select>
                    )}
                    <button
                        onClick={generateSitemap}
                        className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                        Generate Sitemap
                    </button>
                    <button
                        onClick={runAudit}
                        disabled={runningAudit}
                        className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                        {runningAudit ? "Running..." : "Run Audit"}
                    </button>
                </div>
            </div>

            {/* Score Overview */}
            {latestAudit && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="p-5 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 text-center">
                        <p className="text-xs text-gray-500 mb-1">SEO Score</p>
                        <p className={`text-4xl font-bold ${scoreColor(latestAudit.overall_score)}`}>
                            {latestAudit.overall_score}
                        </p>
                    </div>
                    <div className="p-5 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 text-center">
                        <p className="text-xs text-gray-500 mb-1">Pages Analyzed</p>
                        <p className="text-3xl font-bold">{latestAudit.pages_analyzed}</p>
                    </div>
                    <div className="p-5 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 text-center">
                        <p className="text-xs text-gray-500 mb-1">Issues Found</p>
                        <p className="text-3xl font-bold text-red-600">{latestAudit.issues_found}</p>
                    </div>
                    <div className="p-5 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 text-center">
                        <p className="text-xs text-gray-500 mb-1">Tracked Keywords</p>
                        <p className="text-3xl font-bold">{keywords.length}</p>
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
                {(["audits", "keywords"] as Tab[]).map((t) => (
                    <button
                        key={t}
                        onClick={() => setTab(t)}
                        className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors capitalize ${
                            tab === t
                                ? "border-blue-600 text-blue-600"
                                : "border-transparent text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        {t}
                    </button>
                ))}
            </div>

            {loading ? (
                <div className="text-center py-20 text-gray-400">Loading...</div>
            ) : (
                <>
                    {/* Audit Issues */}
                    {tab === "audits" && (
                        <>
                            {!latestAudit ? (
                                <div className="text-center py-16 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                    <p className="text-5xl mb-4">📊</p>
                                    <h2 className="text-xl font-semibold mb-2">No audits yet</h2>
                                    <p className="text-gray-500 mb-4">Run your first SEO audit to find optimization opportunities.</p>
                                    <button onClick={runAudit} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">
                                        Run Audit
                                    </button>
                                </div>
                            ) : latestAudit.issues?.length > 0 ? (
                                <div className="space-y-2">
                                    {latestAudit.issues.map((issue, idx) => (
                                        <div key={idx} className="flex items-start gap-3 p-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                            <span className={`px-2 py-0.5 rounded text-xs font-medium mt-0.5 ${severityBadge(issue.severity)}`}>
                                                {issue.severity}
                                            </span>
                                            <div className="flex-1">
                                                <p className="text-sm">{issue.message}</p>
                                                <p className="text-xs text-gray-400 mt-0.5">/{issue.slug} &middot; {issue.type.replace(/_/g, " ")}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-12 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                    <p className="text-4xl mb-3">🎉</p>
                                    <p className="text-green-600 font-medium">No issues found! Your site is well-optimized.</p>
                                </div>
                            )}
                        </>
                    )}

                    {/* Keywords */}
                    {tab === "keywords" && (
                        <>
                            {/* Add keywords */}
                            <div className="flex gap-2 mb-4">
                                <input
                                    placeholder="Enter keywords (comma-separated)"
                                    value={newKeywords}
                                    onChange={(e) => setNewKeywords(e.target.value)}
                                    className="flex-1 px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600"
                                />
                                <button onClick={addKeywords} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">
                                    Add Keywords
                                </button>
                            </div>

                            {keywords.length === 0 ? (
                                <div className="text-center py-12 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                    <p className="text-4xl mb-3">🔍</p>
                                    <p className="text-gray-500">No keywords tracked yet. Add keywords above to start tracking rankings.</p>
                                </div>
                            ) : (
                                <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                                    <table className="w-full text-sm">
                                        <thead className="bg-gray-50 dark:bg-gray-800">
                                            <tr>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600">Keyword</th>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600">Position</th>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600">Change</th>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600">Volume</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                            {keywords.map((kw) => (
                                                <tr key={kw.id}>
                                                    <td className="px-4 py-3 font-medium">{kw.keyword}</td>
                                                    <td className="px-4 py-3">{kw.current_position ?? "—"}</td>
                                                    <td className="px-4 py-3">
                                                        {kw.rank_change !== null && kw.rank_change !== 0 ? (
                                                            <span className={kw.rank_change > 0 ? "text-green-600" : "text-red-600"}>
                                                                {kw.rank_change > 0 ? "▲" : "▼"} {Math.abs(kw.rank_change)}
                                                            </span>
                                                        ) : (
                                                            <span className="text-gray-400">—</span>
                                                        )}
                                                    </td>
                                                    <td className="px-4 py-3 text-gray-500">{kw.search_volume ?? "—"}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </>
                    )}
                </>
            )}
        </div>
    );
}
