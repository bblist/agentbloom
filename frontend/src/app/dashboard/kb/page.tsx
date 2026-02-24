"use client";

import { useEffect, useState, useRef } from "react";
import { kbAPI } from "@/lib/api";
import { shapeIcon, emptyStateAvatar, thumbnailAvatar } from "@/lib/dicebear";

interface KBDocument {
    id: string;
    title: string;
    source_type: string;
    status: string;
    chunk_count: number;
    file_size: number;
    created_at: string;
}

interface KBSource {
    id: string;
    name: string;
    source_type: string;
    url?: string;
    document_count: number;
    last_synced_at: string | null;
}

interface SearchResult {
    id: string;
    content: string;
    document_title: string;
    similarity: number;
}

export default function KBPage() {
    const [documents, setDocuments] = useState<KBDocument[]>([]);
    const [sources, setSources] = useState<KBSource[]>([]);
    const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [activeTab, setActiveTab] = useState<"documents" | "sources" | "search">("documents");
    const [uploading, setUploading] = useState(false);
    const [showAddSource, setShowAddSource] = useState(false);
    const [newSource, setNewSource] = useState({ name: "", url: "", source_type: "url" });
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        try {
            const [docsRes, sourcesRes] = await Promise.all([
                kbAPI.documents().catch(() => ({ data: [] })),
                kbAPI.sources().catch(() => ({ data: [] })),
            ]);
            setDocuments(docsRes.data?.results || docsRes.data || []);
            setSources(sourcesRes.data?.results || sourcesRes.data || []);
        } catch (e) {
            console.error("Failed to load KB data", e);
        }
    }

    async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0];
        if (!file) return;
        setUploading(true);
        try {
            await kbAPI.uploadDocument(file, file.name);
            await loadData();
        } catch (err) {
            console.error("Upload failed", err);
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    }

    async function handleSearch() {
        if (!searchQuery.trim()) return;
        try {
            const res = await kbAPI.search(searchQuery);
            setSearchResults(res.data?.results || res.data || []);
        } catch (err) {
            console.error("Search failed", err);
        }
    }

    async function handleDelete(id: string) {
        try {
            await kbAPI.deleteDocument(id);
            setDocuments((prev) => prev.filter((d) => d.id !== id));
        } catch (err) {
            console.error("Delete failed", err);
        }
    }

    async function handleReprocess(id: string) {
        try {
            await kbAPI.reprocessDocument(id);
            await loadData();
        } catch (err) {
            console.error("Reprocess failed", err);
        }
    }

    async function handleAddSource() {
        try {
            await kbAPI.createSource(newSource);
            setShowAddSource(false);
            setNewSource({ name: "", url: "", source_type: "url" });
            await loadData();
        } catch (err) {
            console.error("Add source failed", err);
        }
    }

    function formatBytes(bytes: number) {
        if (!bytes) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
    }

    const statusColor: Record<string, string> = {
        processed: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
        processing: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
        pending: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
        failed: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    };

    return (
        <div className="p-8">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold">Knowledge Base</h1>
                    <p className="mt-1 text-gray-500">
                        Train your AI agent with documents, URLs, and data sources
                    </p>
                </div>
                <div className="flex gap-3">
                    <input
                        ref={fileInputRef}
                        type="file"
                        className="hidden"
                        accept=".pdf,.docx,.txt,.md,.csv"
                        onChange={handleUpload}
                    />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={uploading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
                    >
                        {uploading ? "Uploading..." : "Upload Document"}
                    </button>
                    <button
                        onClick={() => setShowAddSource(true)}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 font-medium"
                    >
                        Add Source
                    </button>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {[
                    { label: "Documents", value: documents.length.toString(), seed: "kb-docs-total" },
                    {
                        label: "Total Chunks",
                        value: documents.reduce((s, d) => s + (d.chunk_count || 0), 0).toString(),
                        seed: "kb-chunks-total",
                    },
                    { label: "Sources", value: sources.length.toString(), seed: "kb-sources-total" },
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

            {/* Tabs */}
            <div className="flex gap-1 mb-6 bg-gray-100 dark:bg-gray-800 rounded-lg p-1 w-fit">
                {(["documents", "sources", "search"] as const).map((tab) => (
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

            {/* Documents Tab */}
            {activeTab === "documents" && (
                <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                    {documents.length === 0 ? (
                        <div className="p-12 text-center">
                            <img
                                src={emptyStateAvatar("kb-empty")}
                                alt=""
                                className="w-20 h-20 mx-auto mb-4 rounded-full"
                            />
                            <h3 className="text-lg font-semibold mb-2">No documents yet</h3>
                            <p className="text-gray-500 mb-4">
                                Upload PDFs, Word docs, or text files to train your AI agent
                            </p>
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                            >
                                Upload Your First Document
                            </button>
                        </div>
                    ) : (
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200 dark:border-gray-800">
                                    <th className="text-left p-4 text-sm font-medium text-gray-500">Document</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-500">Status</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-500">Chunks</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-500">Size</th>
                                    <th className="text-right p-4 text-sm font-medium text-gray-500">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {documents.map((doc) => (
                                    <tr
                                        key={doc.id}
                                        className="border-b border-gray-100 dark:border-gray-800 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                                    >
                                        <td className="p-4">
                                            <div className="flex items-center gap-3">
                                                <img
                                                    src={thumbnailAvatar(`kb-doc-${doc.id}`)}
                                                    alt=""
                                                    className="w-10 h-10 rounded-lg"
                                                />
                                                <div>
                                                    <p className="font-medium">{doc.title}</p>
                                                    <p className="text-xs text-gray-500">
                                                        {new Date(doc.created_at).toLocaleDateString()}
                                                    </p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <span
                                                className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                                                    statusColor[doc.status] || statusColor.pending
                                                }`}
                                            >
                                                {doc.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-sm text-gray-600 dark:text-gray-400">
                                            {doc.chunk_count || 0}
                                        </td>
                                        <td className="p-4 text-sm text-gray-600 dark:text-gray-400">
                                            {formatBytes(doc.file_size)}
                                        </td>
                                        <td className="p-4 text-right">
                                            <div className="flex gap-2 justify-end">
                                                <button
                                                    onClick={() => handleReprocess(doc.id)}
                                                    className="px-3 py-1.5 text-xs border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
                                                >
                                                    Reprocess
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(doc.id)}
                                                    className="px-3 py-1.5 text-xs text-red-600 border border-red-200 dark:border-red-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}

            {/* Sources Tab */}
            {activeTab === "sources" && (
                <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                    {sources.length === 0 ? (
                        <div className="p-12 text-center">
                            <img
                                src={emptyStateAvatar("kb-sources-empty")}
                                alt=""
                                className="w-20 h-20 mx-auto mb-4 rounded-full"
                            />
                            <h3 className="text-lg font-semibold mb-2">No data sources</h3>
                            <p className="text-gray-500 mb-4">
                                Connect URLs, sitemaps, or APIs to automatically import content
                            </p>
                            <button
                                onClick={() => setShowAddSource(true)}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                            >
                                Add Your First Source
                            </button>
                        </div>
                    ) : (
                        <div className="divide-y divide-gray-200 dark:divide-gray-800">
                            {sources.map((source) => (
                                <div
                                    key={source.id}
                                    className="p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50"
                                >
                                    <div className="flex items-center gap-3">
                                        <img
                                            src={thumbnailAvatar(`kb-source-${source.id}`)}
                                            alt=""
                                            className="w-10 h-10 rounded-lg"
                                        />
                                        <div>
                                            <p className="font-medium">{source.name}</p>
                                            <p className="text-xs text-gray-500">
                                                {source.source_type} &middot; {source.document_count} docs
                                                {source.last_synced_at &&
                                                    ` &middot; Synced ${new Date(source.last_synced_at).toLocaleDateString()}`}
                                            </p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={async () => {
                                            await kbAPI.deleteSource(source.id);
                                            await loadData();
                                        }}
                                        className="px-3 py-1.5 text-xs text-red-600 border border-red-200 dark:border-red-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20"
                                    >
                                        Remove
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Search Tab */}
            {activeTab === "search" && (
                <div>
                    <div className="flex gap-3 mb-6">
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                            placeholder="Search your knowledge base..."
                            className="flex-1 px-4 py-2.5 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-900"
                        />
                        <button
                            onClick={handleSearch}
                            className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                        >
                            Search
                        </button>
                    </div>

                    {searchResults.length > 0 ? (
                        <div className="space-y-4">
                            {searchResults.map((result, i) => (
                                <div
                                    key={result.id || i}
                                    className="p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800"
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm font-medium text-blue-600">
                                            {result.document_title}
                                        </span>
                                        <span className="text-xs text-gray-500">
                                            {(result.similarity * 100).toFixed(1)}% match
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-700 dark:text-gray-300">{result.content}</p>
                                </div>
                            ))}
                        </div>
                    ) : searchQuery ? (
                        <div className="p-12 text-center bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                            <img
                                src={emptyStateAvatar("kb-search-empty")}
                                alt=""
                                className="w-16 h-16 mx-auto mb-4 rounded-full"
                            />
                            <p className="text-gray-500">No results found. Try a different query.</p>
                        </div>
                    ) : null}
                </div>
            )}

            {/* Add Source Modal */}
            {showAddSource && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 w-full max-w-md shadow-xl">
                        <h3 className="text-lg font-semibold mb-4">Add Data Source</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Name</label>
                                <input
                                    type="text"
                                    value={newSource.name}
                                    onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
                                    className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                    placeholder="Company Blog"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Type</label>
                                <select
                                    value={newSource.source_type}
                                    onChange={(e) => setNewSource({ ...newSource, source_type: e.target.value })}
                                    className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                >
                                    <option value="url">URL / Web Page</option>
                                    <option value="sitemap">Sitemap</option>
                                    <option value="rss">RSS Feed</option>
                                    <option value="api">API Endpoint</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">URL</label>
                                <input
                                    type="url"
                                    value={newSource.url}
                                    onChange={(e) => setNewSource({ ...newSource, url: e.target.value })}
                                    className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                    placeholder="https://example.com/blog"
                                />
                            </div>
                        </div>
                        <div className="flex gap-3 justify-end mt-6">
                            <button
                                onClick={() => setShowAddSource(false)}
                                className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleAddSource}
                                disabled={!newSource.name || !newSource.url}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
                            >
                                Add Source
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
