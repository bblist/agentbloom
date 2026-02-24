"use client";

import { useEffect, useState } from "react";
import { webhooksAPI } from "@/lib/api";
import { shapeIcon, emptyStateAvatar, thumbnailAvatar } from "@/lib/dicebear";

interface WebhookEndpoint {
    id: string;
    url: string;
    description: string;
    events: string[];
    is_active: boolean;
    secret: string;
    created_at: string;
    last_triggered_at: string | null;
    delivery_count: number;
    failure_count: number;
}

interface Delivery {
    id: string;
    event: string;
    status_code: number;
    success: boolean;
    response_time_ms: number;
    created_at: string;
    attempts: number;
}

const AVAILABLE_EVENTS = [
    "contact.created",
    "contact.updated",
    "booking.created",
    "booking.confirmed",
    "booking.cancelled",
    "payment.completed",
    "payment.refunded",
    "course.enrolled",
    "course.completed",
    "site.published",
    "form.submitted",
];

export default function WebhooksPage() {
    const [endpoints, setEndpoints] = useState<WebhookEndpoint[]>([]);
    const [selectedEndpoint, setSelectedEndpoint] = useState<WebhookEndpoint | null>(null);
    const [deliveries, setDeliveries] = useState<Delivery[]>([]);
    const [showCreate, setShowCreate] = useState(false);
    const [newEndpoint, setNewEndpoint] = useState({
        url: "",
        description: "",
        events: [] as string[],
    });

    useEffect(() => {
        loadEndpoints();
    }, []);

    async function loadEndpoints() {
        try {
            const res = await webhooksAPI.list();
            setEndpoints(res.data?.results || res.data || []);
        } catch (e) {
            console.error("Failed to load webhooks", e);
        }
    }

    async function loadDeliveries(endpointId: string) {
        try {
            const res = await webhooksAPI.deliveries(endpointId);
            setDeliveries(res.data?.results || res.data || []);
        } catch (e) {
            console.error("Failed to load deliveries", e);
        }
    }

    async function handleCreate() {
        try {
            await webhooksAPI.create(newEndpoint);
            setShowCreate(false);
            setNewEndpoint({ url: "", description: "", events: [] });
            await loadEndpoints();
        } catch (err) {
            console.error("Create failed", err);
        }
    }

    async function handleDelete(id: string) {
        try {
            await webhooksAPI.delete(id);
            setEndpoints((prev) => prev.filter((e) => e.id !== id));
            if (selectedEndpoint?.id === id) {
                setSelectedEndpoint(null);
                setDeliveries([]);
            }
        } catch (err) {
            console.error("Delete failed", err);
        }
    }

    async function handleToggle(endpoint: WebhookEndpoint) {
        try {
            await webhooksAPI.update(endpoint.id, { is_active: !endpoint.is_active });
            setEndpoints((prev) =>
                prev.map((e) =>
                    e.id === endpoint.id ? { ...e, is_active: !e.is_active } : e
                )
            );
        } catch (err) {
            console.error("Toggle failed", err);
        }
    }

    async function handleRetry(endpointId: string, deliveryId: string) {
        try {
            await webhooksAPI.retryDelivery(endpointId, deliveryId);
            await loadDeliveries(endpointId);
        } catch (err) {
            console.error("Retry failed", err);
        }
    }

    function toggleEvent(event: string) {
        setNewEndpoint((prev) => ({
            ...prev,
            events: prev.events.includes(event)
                ? prev.events.filter((e) => e !== event)
                : [...prev.events, event],
        }));
    }

    return (
        <div className="p-4 sm:p-8">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold">Webhooks</h1>
                    <p className="mt-1 text-gray-500">
                        Connect external services with real-time event notifications
                    </p>
                </div>
                <button
                    onClick={() => setShowCreate(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                >
                    Add Endpoint
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {[
                    { label: "Endpoints", value: endpoints.length.toString(), seed: "wh-endpoints" },
                    {
                        label: "Active",
                        value: endpoints.filter((e) => e.is_active).length.toString(),
                        seed: "wh-active",
                    },
                    {
                        label: "Total Deliveries",
                        value: endpoints.reduce((s, e) => s + (e.delivery_count || 0), 0).toString(),
                        seed: "wh-deliveries",
                    },
                ].map((stat) => (
                    <div
                        key={stat.label}
                        className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800"
                    >
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-500">{stat.label}</span>
                            <img src={shapeIcon(stat.seed)} alt="" className="w-10 h-10 rounded-lg" />
                        </div>
                        <span className="text-2xl sm:text-3xl font-bold">{stat.value}</span>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Endpoints list */}
                <div className="lg:col-span-2">
                    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                        {endpoints.length === 0 ? (
                            <div className="p-12 text-center">
                                <img
                                    src={emptyStateAvatar("webhooks-empty")}
                                    alt=""
                                    className="w-20 h-20 mx-auto mb-4 rounded-full"
                                />
                                <h3 className="text-lg font-semibold mb-2">No webhook endpoints</h3>
                                <p className="text-gray-500 mb-4">
                                    Create an endpoint to start receiving real-time event notifications
                                </p>
                                <button
                                    onClick={() => setShowCreate(true)}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                                >
                                    Create Your First Endpoint
                                </button>
                            </div>
                        ) : (
                            <div className="divide-y divide-gray-200 dark:divide-gray-800">
                                {endpoints.map((ep) => (
                                    <div
                                        key={ep.id}
                                        className={`p-4 cursor-pointer transition-colors ${
                                            selectedEndpoint?.id === ep.id
                                                ? "bg-blue-50 dark:bg-blue-950/20"
                                                : "hover:bg-gray-50 dark:hover:bg-gray-800/50"
                                        }`}
                                        onClick={() => {
                                            setSelectedEndpoint(ep);
                                            loadDeliveries(ep.id);
                                        }}
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3 min-w-0">
                                                <img
                                                    src={thumbnailAvatar(`wh-${ep.id}`)}
                                                    alt=""
                                                    className="w-10 h-10 rounded-lg"
                                                />
                                                <div className="min-w-0">
                                                    <p className="font-medium text-sm truncate">
                                                        {ep.url}
                                                    </p>
                                                    <p className="text-xs text-gray-500">
                                                        {ep.description || "No description"} &middot;{" "}
                                                        {ep.events?.length || 0} events
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                <span
                                                    className={`w-2.5 h-2.5 rounded-full ${
                                                        ep.is_active ? "bg-green-500" : "bg-gray-400"
                                                    }`}
                                                />
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleToggle(ep);
                                                    }}
                                                    className="text-xs px-2 py-1 border border-gray-300 dark:border-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-800"
                                                >
                                                    {ep.is_active ? "Disable" : "Enable"}
                                                </button>
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDelete(ep.id);
                                                    }}
                                                    className="text-xs px-2 py-1 text-red-600 border border-red-200 dark:border-red-800 rounded hover:bg-red-50 dark:hover:bg-red-900/20"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Delivery log */}
                <div>
                    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
                            <h3 className="font-semibold text-sm">
                                {selectedEndpoint ? "Recent Deliveries" : "Delivery Log"}
                            </h3>
                        </div>
                        {!selectedEndpoint ? (
                            <div className="p-8 text-center text-sm text-gray-500">
                                Select an endpoint to view deliveries
                            </div>
                        ) : deliveries.length === 0 ? (
                            <div className="p-8 text-center text-sm text-gray-500">
                                No deliveries yet for this endpoint
                            </div>
                        ) : (
                            <div className="divide-y divide-gray-200 dark:divide-gray-800 max-h-96 overflow-y-auto">
                                {deliveries.map((d) => (
                                    <div key={d.id} className="p-3 text-xs">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="font-medium">{d.event}</span>
                                            <span
                                                className={`px-1.5 py-0.5 rounded ${
                                                    d.success
                                                        ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                                                        : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                                                }`}
                                            >
                                                {d.status_code || "ERR"}
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between text-gray-500">
                                            <span>
                                                {d.response_time_ms}ms &middot; {d.attempts} attempt
                                                {d.attempts > 1 ? "s" : ""}
                                            </span>
                                            <div className="flex items-center gap-2">
                                                <span>{new Date(d.created_at).toLocaleTimeString()}</span>
                                                {!d.success && selectedEndpoint && (
                                                    <button
                                                        onClick={() => handleRetry(selectedEndpoint.id, d.id)}
                                                        className="text-blue-600 hover:underline"
                                                    >
                                                        Retry
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Create Endpoint Modal */}
            {showCreate && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 w-full max-w-lg shadow-xl">
                        <h3 className="text-lg font-semibold mb-4">Create Webhook Endpoint</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    Endpoint URL
                                </label>
                                <input
                                    type="url"
                                    value={newEndpoint.url}
                                    onChange={(e) =>
                                        setNewEndpoint({ ...newEndpoint, url: e.target.value })
                                    }
                                    className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                    placeholder="https://your-app.com/webhooks/agentbloom"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    Description
                                </label>
                                <input
                                    type="text"
                                    value={newEndpoint.description}
                                    onChange={(e) =>
                                        setNewEndpoint({ ...newEndpoint, description: e.target.value })
                                    }
                                    className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                    placeholder="Production webhook handler"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Events</label>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                                    {AVAILABLE_EVENTS.map((event) => (
                                        <label
                                            key={event}
                                            className="flex items-center gap-2 text-sm p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
                                        >
                                            <input
                                                type="checkbox"
                                                checked={newEndpoint.events.includes(event)}
                                                onChange={() => toggleEvent(event)}
                                                className="rounded border-gray-300 dark:border-gray-600"
                                            />
                                            <code className="text-xs">{event}</code>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        </div>
                        <div className="flex gap-3 justify-end mt-6">
                            <button
                                onClick={() => setShowCreate(false)}
                                className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleCreate}
                                disabled={!newEndpoint.url || newEndpoint.events.length === 0}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
                            >
                                Create Endpoint
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
