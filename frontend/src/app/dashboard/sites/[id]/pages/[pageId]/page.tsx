"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { sitesAPI } from "@/lib/api";
import { toast } from "sonner";

interface ContentBlock {
    id: string;
    block_type: string;
    content: Record<string, string>;
    sort_order: number;
}

const BLOCK_TYPES = [
    { value: "hero", label: "Hero Section", icon: "🏔️" },
    { value: "text", label: "Text Block", icon: "📝" },
    { value: "cta", label: "Call-to-Action", icon: "🎯" },
    { value: "features", label: "Features Grid", icon: "⭐" },
    { value: "testimonials", label: "Testimonials", icon: "💬" },
    { value: "pricing", label: "Pricing Table", icon: "💰" },
    { value: "faq", label: "FAQ Section", icon: "❓" },
    { value: "image", label: "Image / Media", icon: "🖼️" },
    { value: "form", label: "Lead Capture Form", icon: "📋" },
    { value: "video", label: "Video Embed", icon: "🎬" },
    { value: "countdown", label: "Countdown Timer", icon: "⏳" },
    { value: "social_proof", label: "Social Proof", icon: "🏆" },
];

const BLOCK_FIELDS: Record<string, { key: string; label: string; type: "text" | "textarea" | "url" }[]> = {
    hero: [
        { key: "headline", label: "Headline", type: "text" },
        { key: "subheadline", label: "Sub-headline", type: "text" },
        { key: "button_text", label: "Button Text", type: "text" },
        { key: "button_url", label: "Button URL", type: "url" },
        { key: "background_image", label: "Background Image URL", type: "url" },
    ],
    text: [
        { key: "heading", label: "Heading", type: "text" },
        { key: "body", label: "Body Text", type: "textarea" },
    ],
    cta: [
        { key: "headline", label: "Headline", type: "text" },
        { key: "description", label: "Description", type: "textarea" },
        { key: "button_text", label: "Button Text", type: "text" },
        { key: "button_url", label: "Button URL", type: "url" },
    ],
    features: [
        { key: "heading", label: "Section Heading", type: "text" },
        { key: "feature_1", label: "Feature 1", type: "text" },
        { key: "feature_2", label: "Feature 2", type: "text" },
        { key: "feature_3", label: "Feature 3", type: "text" },
        { key: "feature_4", label: "Feature 4", type: "text" },
    ],
    testimonials: [
        { key: "heading", label: "Section Heading", type: "text" },
        { key: "quote_1", label: "Testimonial 1", type: "textarea" },
        { key: "author_1", label: "Author 1", type: "text" },
        { key: "quote_2", label: "Testimonial 2", type: "textarea" },
        { key: "author_2", label: "Author 2", type: "text" },
    ],
    pricing: [
        { key: "heading", label: "Section Heading", type: "text" },
        { key: "plan_name", label: "Plan Name", type: "text" },
        { key: "price", label: "Price", type: "text" },
        { key: "features", label: "Features (one per line)", type: "textarea" },
        { key: "cta_text", label: "CTA Text", type: "text" },
        { key: "cta_url", label: "CTA URL", type: "url" },
    ],
    faq: [
        { key: "heading", label: "Section Heading", type: "text" },
        { key: "q1", label: "Question 1", type: "text" },
        { key: "a1", label: "Answer 1", type: "textarea" },
        { key: "q2", label: "Question 2", type: "text" },
        { key: "a2", label: "Answer 2", type: "textarea" },
    ],
    image: [
        { key: "src", label: "Image URL", type: "url" },
        { key: "alt", label: "Alt Text", type: "text" },
        { key: "caption", label: "Caption", type: "text" },
    ],
    form: [
        { key: "heading", label: "Form Heading", type: "text" },
        { key: "description", label: "Description", type: "textarea" },
        { key: "button_text", label: "Submit Button Text", type: "text" },
        { key: "fields", label: "Fields (name,email,phone etc.)", type: "text" },
    ],
    video: [
        { key: "embed_url", label: "Video Embed URL", type: "url" },
        { key: "caption", label: "Caption", type: "text" },
    ],
    countdown: [
        { key: "headline", label: "Headline", type: "text" },
        { key: "end_date", label: "End Date (YYYY-MM-DD)", type: "text" },
        { key: "cta_text", label: "CTA Text", type: "text" },
        { key: "cta_url", label: "CTA URL", type: "url" },
    ],
    social_proof: [
        { key: "heading", label: "Heading", type: "text" },
        { key: "stat_1", label: "Stat 1 (e.g., 10k+ Users)", type: "text" },
        { key: "stat_2", label: "Stat 2", type: "text" },
        { key: "stat_3", label: "Stat 3", type: "text" },
    ],
};

export default function PageEditorPage({
    params,
}: {
    params: Promise<{ id: string; pageId: string }>;
}) {
    const { id: siteId, pageId } = use(params);
    const [pageData, setPageData] = useState<{
        title: string;
        slug: string;
        page_type: string;
        meta_title: string;
        meta_description: string;
        is_published: boolean;
    }>({ title: "", slug: "", page_type: "landing", meta_title: "", meta_description: "", is_published: false });
    const [blocks, setBlocks] = useState<ContentBlock[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [activeBlock, setActiveBlock] = useState<string | null>(null);
    const [showAddBlock, setShowAddBlock] = useState(false);

    useEffect(() => {
        loadPage();
    }, [siteId, pageId]);

    async function loadPage() {
        setLoading(true);
        try {
            const res = await sitesAPI.getPage(siteId, pageId);
            const p = res.data;
            setPageData({
                title: p.title || "",
                slug: p.slug || "",
                page_type: p.page_type || "landing",
                meta_title: p.meta_title || "",
                meta_description: p.meta_description || "",
                is_published: p.is_published || false,
            });
            setBlocks(p.content_blocks || []);
        } catch {
            toast.error("Failed to load page");
        } finally {
            setLoading(false);
        }
    }

    async function savePage() {
        setSaving(true);
        try {
            await sitesAPI.updatePage(siteId, pageId, {
                ...pageData,
                content_blocks: blocks.map((b, i) => ({
                    ...b,
                    sort_order: i,
                })),
            });
            toast.success("Page saved!");
        } catch {
            toast.error("Failed to save");
        } finally {
            setSaving(false);
        }
    }

    async function publishPage() {
        try {
            await sitesAPI.publishPage(siteId, pageId);
            setPageData({ ...pageData, is_published: true });
            toast.success("Page published!");
        } catch {
            toast.error("Failed to publish");
        }
    }

    function addBlock(type: string) {
        const newBlock: ContentBlock = {
            id: `new-${Date.now()}`,
            block_type: type,
            content: {},
            sort_order: blocks.length,
        };
        setBlocks([...blocks, newBlock]);
        setActiveBlock(newBlock.id);
        setShowAddBlock(false);
    }

    function updateBlockContent(blockId: string, key: string, value: string) {
        setBlocks(
            blocks.map((b) =>
                b.id === blockId
                    ? { ...b, content: { ...b.content, [key]: value } }
                    : b
            )
        );
    }

    function removeBlock(blockId: string) {
        setBlocks(blocks.filter((b) => b.id !== blockId));
        if (activeBlock === blockId) setActiveBlock(null);
    }

    function moveBlock(idx: number, dir: -1 | 1) {
        if (idx + dir < 0 || idx + dir >= blocks.length) return;
        const newBlocks = [...blocks];
        [newBlocks[idx], newBlocks[idx + dir]] = [newBlocks[idx + dir], newBlocks[idx]];
        setBlocks(newBlocks);
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
            </div>
        );
    }

    return (
        <div className="p-4 sm:p-6 max-w-5xl mx-auto">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
                <div>
                    <Link
                        href={`/dashboard/sites/${siteId}`}
                        className="text-sm text-blue-600 hover:underline mb-1 inline-block"
                    >
                        &larr; Back to Site
                    </Link>
                    <h1 className="text-xl sm:text-2xl font-bold">{pageData.title || "Untitled Page"}</h1>
                </div>
                <div className="flex gap-2 flex-wrap">
                    <button
                        onClick={savePage}
                        disabled={saving}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
                    >
                        {saving ? "Saving..." : "Save"}
                    </button>
                    <button
                        onClick={publishPage}
                        className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700"
                    >
                        {pageData.is_published ? "Published ✓" : "Publish"}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left: Page Settings + SEO */}
                <div className="lg:col-span-1 space-y-4">
                    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4 space-y-3">
                        <h3 className="font-semibold text-sm">Page Settings</h3>
                        <div>
                            <label className="block text-xs text-gray-500 mb-1">Title</label>
                            <input
                                type="text"
                                value={pageData.title}
                                onChange={(e) => setPageData({ ...pageData, title: e.target.value })}
                                className="w-full px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-700"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-500 mb-1">URL Slug</label>
                            <input
                                type="text"
                                value={pageData.slug}
                                onChange={(e) => setPageData({ ...pageData, slug: e.target.value })}
                                className="w-full px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-700"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-500 mb-1">Page Type</label>
                            <select
                                value={pageData.page_type}
                                onChange={(e) => setPageData({ ...pageData, page_type: e.target.value })}
                                className="w-full px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-700"
                            >
                                <option value="landing">Landing Page</option>
                                <option value="sales">Sales Page</option>
                                <option value="squeeze">Squeeze Page</option>
                                <option value="thank_you">Thank You</option>
                                <option value="webinar">Webinar</option>
                                <option value="blog">Blog</option>
                                <option value="about">About</option>
                                <option value="contact">Contact</option>
                                <option value="custom">Custom</option>
                            </select>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4 space-y-3">
                        <h3 className="font-semibold text-sm">SEO Settings</h3>
                        <div>
                            <label className="block text-xs text-gray-500 mb-1">Meta Title</label>
                            <input
                                type="text"
                                value={pageData.meta_title}
                                onChange={(e) => setPageData({ ...pageData, meta_title: e.target.value })}
                                className="w-full px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-700"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-500 mb-1">Meta Description</label>
                            <textarea
                                value={pageData.meta_description}
                                onChange={(e) => setPageData({ ...pageData, meta_description: e.target.value })}
                                rows={3}
                                className="w-full px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-700"
                            />
                        </div>
                    </div>
                </div>

                {/* Right: Content Blocks */}
                <div className="lg:col-span-2 space-y-3">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold">Content Blocks ({blocks.length})</h3>
                        <button
                            onClick={() => setShowAddBlock(!showAddBlock)}
                            className="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
                        >
                            + Add Block
                        </button>
                    </div>

                    {/* Add block picker */}
                    {showAddBlock && (
                        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
                            <p className="text-sm font-medium mb-3">Choose a block type:</p>
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                                {BLOCK_TYPES.map((bt) => (
                                    <button
                                        key={bt.value}
                                        onClick={() => addBlock(bt.value)}
                                        className="flex items-center gap-2 px-3 py-2 border rounded-lg text-sm hover:bg-blue-50 dark:hover:bg-blue-950/20 dark:border-gray-700 text-left"
                                    >
                                        <span>{bt.icon}</span>
                                        <span>{bt.label}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Blocks list */}
                    {blocks.length === 0 ? (
                        <div className="text-center py-12 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                            <p className="text-gray-500 mb-2">No content blocks yet</p>
                            <p className="text-sm text-gray-400">
                                Add blocks above or ask the AI agent to build this page for you
                            </p>
                        </div>
                    ) : (
                        blocks.map((block, idx) => {
                            const bt = BLOCK_TYPES.find((t) => t.value === block.block_type);
                            const fields = BLOCK_FIELDS[block.block_type] || [];
                            const isActive = activeBlock === block.id;

                            return (
                                <div
                                    key={block.id}
                                    className={`bg-white dark:bg-gray-900 rounded-xl border transition-colors ${
                                        isActive
                                            ? "border-blue-400 dark:border-blue-600"
                                            : "border-gray-200 dark:border-gray-800"
                                    }`}
                                >
                                    {/* Block header */}
                                    <div
                                        className="flex items-center justify-between p-3 cursor-pointer"
                                        onClick={() => setActiveBlock(isActive ? null : block.id)}
                                    >
                                        <div className="flex items-center gap-2">
                                            <span>{bt?.icon || "📦"}</span>
                                            <span className="font-medium text-sm">
                                                {bt?.label || block.block_type}
                                            </span>
                                            {block.content.headline || block.content.heading ? (
                                                <span className="text-xs text-gray-400 truncate max-w-[200px]">
                                                    — {block.content.headline || block.content.heading}
                                                </span>
                                            ) : null}
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <button
                                                onClick={(e) => { e.stopPropagation(); moveBlock(idx, -1); }}
                                                className="p-1 text-gray-400 hover:text-gray-600 text-xs"
                                                title="Move up"
                                            >
                                                ▲
                                            </button>
                                            <button
                                                onClick={(e) => { e.stopPropagation(); moveBlock(idx, 1); }}
                                                className="p-1 text-gray-400 hover:text-gray-600 text-xs"
                                                title="Move down"
                                            >
                                                ▼
                                            </button>
                                            <button
                                                onClick={(e) => { e.stopPropagation(); removeBlock(block.id); }}
                                                className="p-1 text-red-400 hover:text-red-600 text-xs ml-1"
                                                title="Remove"
                                            >
                                                ✕
                                            </button>
                                        </div>
                                    </div>

                                    {/* Block editor (expanded) */}
                                    {isActive && (
                                        <div className="border-t border-gray-100 dark:border-gray-800 p-4 space-y-3">
                                            {fields.map((field) => (
                                                <div key={field.key}>
                                                    <label className="block text-xs text-gray-500 mb-1">
                                                        {field.label}
                                                    </label>
                                                    {field.type === "textarea" ? (
                                                        <textarea
                                                            value={block.content[field.key] || ""}
                                                            onChange={(e) =>
                                                                updateBlockContent(block.id, field.key, e.target.value)
                                                            }
                                                            rows={3}
                                                            className="w-full px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-700"
                                                        />
                                                    ) : (
                                                        <input
                                                            type={field.type}
                                                            value={block.content[field.key] || ""}
                                                            onChange={(e) =>
                                                                updateBlockContent(block.id, field.key, e.target.value)
                                                            }
                                                            className="w-full px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-700"
                                                        />
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            );
                        })
                    )}

                    <div className="bg-blue-50 dark:bg-blue-950/20 rounded-xl border border-blue-200 dark:border-blue-800 p-4 mt-4">
                        <p className="text-sm text-blue-700 dark:text-blue-300">
                            <strong>Pro tip:</strong> Go to{" "}
                            <Link href="/dashboard/agent" className="underline">
                                Agent Chat
                            </Link>{" "}
                            and say <em>&quot;Build the content for my {pageData.page_type} page&quot;</em> — the AI agent will
                            auto-populate the blocks.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
