"use client";

import { useEffect, useState } from "react";
import { bookingsAPI } from "@/lib/api";
import { shapeIcon, emptyStateAvatar } from "@/lib/dicebear";

interface Service {
    id: string;
    name: string;
    duration_minutes: number;
    price: string;
    is_active: boolean;
    booking_count: number;
}

interface Booking {
    id: string;
    service_name: string;
    client_name: string;
    client_email: string;
    start_time: string;
    end_time: string;
    status: string;
    notes: string;
}

type Tab = "bookings" | "services";

export default function BookingsPage() {
    const [tab, setTab] = useState<Tab>("bookings");
    const [services, setServices] = useState<Service[]>([]);
    const [bookings, setBookings] = useState<Booking[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateService, setShowCreateService] = useState(false);
    const [serviceForm, setServiceForm] = useState({ name: "", duration_minutes: "60", price: "0" });

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        setLoading(true);
        try {
            const [s, b] = await Promise.all([
                bookingsAPI.services(),
                bookingsAPI.bookings(),
            ]);
            setServices(s.data?.results || s.data || []);
            setBookings(b.data?.results || b.data || []);
        } catch (e) {
            console.error("Failed to load booking data", e);
        } finally {
            setLoading(false);
        }
    }

    async function createService() {
        try {
            await bookingsAPI.createService({
                name: serviceForm.name,
                duration_minutes: parseInt(serviceForm.duration_minutes),
                price: serviceForm.price,
            });
            setServiceForm({ name: "", duration_minutes: "60", price: "0" });
            setShowCreateService(false);
            loadData();
        } catch (e) {
            console.error("Failed to create service", e);
        }
    }

    async function confirmBooking(id: string) {
        try {
            await bookingsAPI.confirmBooking(id);
            loadData();
        } catch (e) {
            console.error("Failed to confirm booking", e);
        }
    }

    async function cancelBooking(id: string) {
        if (!confirm("Cancel this booking?")) return;
        try {
            await bookingsAPI.cancelBooking(id);
            loadData();
        } catch (e) {
            console.error("Failed to cancel booking", e);
        }
    }

    function formatDateTime(iso: string) {
        try {
            const d = new Date(iso);
            return d.toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                hour: "numeric",
                minute: "2-digit",
            });
        } catch {
            return iso;
        }
    }

    const statusBadge = (status: string) => {
        const s: Record<string, string> = {
            confirmed: "bg-green-100 text-green-700",
            pending: "bg-yellow-100 text-yellow-700",
            cancelled: "bg-red-100 text-red-600",
            completed: "bg-blue-100 text-blue-700",
            no_show: "bg-gray-100 text-gray-600",
        };
        return s[status] || "bg-gray-100 text-gray-600";
    };

    const upcoming = bookings.filter((b) => b.status === "confirmed" || b.status === "pending");
    const past = bookings.filter((b) => b.status === "completed" || b.status === "cancelled" || b.status === "no_show");

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Bookings</h1>
                    <p className="text-gray-500 mt-1">Manage appointments, services, and availability.</p>
                </div>
                {tab === "services" && (
                    <button
                        onClick={() => setShowCreateService(!showCreateService)}
                        className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        + New Service
                    </button>
                )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                {[
                    { label: "Total Bookings", value: bookings.length, seed: "bookings-total" },
                    { label: "Upcoming", value: upcoming.length, seed: "bookings-upcoming" },
                    { label: "Services", value: services.length, seed: "bookings-services" },
                    { label: "Active Services", value: services.filter((s) => s.is_active).length, seed: "bookings-active" },
                ].map((stat) => (
                    <div key={stat.label} className="p-4 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-gray-500">{stat.label}</span>
                            <img src={shapeIcon(stat.seed)} alt="" className="w-8 h-8 rounded" />
                        </div>
                        <span className="text-2xl font-bold">{stat.value}</span>
                    </div>
                ))}
            </div>

            {/* Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
                {(["bookings", "services"] as Tab[]).map((t) => (
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
                    {/* Services Tab */}
                    {tab === "services" && (
                        <>
                            {showCreateService && (
                                <div className="mb-6 p-4 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                    <h3 className="font-medium mb-3">New Service</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                        <input
                                            placeholder="Service name"
                                            value={serviceForm.name}
                                            onChange={(e) => setServiceForm({ ...serviceForm, name: e.target.value })}
                                            className="px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600"
                                        />
                                        <input
                                            placeholder="Duration (minutes)"
                                            type="number"
                                            value={serviceForm.duration_minutes}
                                            onChange={(e) => setServiceForm({ ...serviceForm, duration_minutes: e.target.value })}
                                            className="px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600"
                                        />
                                        <input
                                            placeholder="Price"
                                            type="number"
                                            value={serviceForm.price}
                                            onChange={(e) => setServiceForm({ ...serviceForm, price: e.target.value })}
                                            className="px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600"
                                        />
                                    </div>
                                    <div className="flex gap-2 mt-3">
                                        <button onClick={createService} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">
                                            Create
                                        </button>
                                        <button onClick={() => setShowCreateService(false)} className="px-4 py-2 text-sm text-gray-500">
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            )}

                            {services.length === 0 ? (
                                <div className="text-center py-16 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                    <img src={emptyStateAvatar("no-services")} alt="" className="w-16 h-16 mx-auto mb-4 rounded-xl" />
                                    <h2 className="text-xl font-semibold mb-2">No services yet</h2>
                                    <p className="text-gray-500 mb-4">Create bookable services for your clients.</p>
                                    <button onClick={() => setShowCreateService(true)} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">
                                        Create Service
                                    </button>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {services.map((s) => (
                                        <div key={s.id} className="p-4 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                            <div className="flex items-start justify-between mb-2">
                                                <h3 className="font-semibold">{s.name}</h3>
                                                <span className={`px-2 py-0.5 rounded-full text-xs ${s.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                                                    {s.is_active ? "Active" : "Inactive"}
                                                </span>
                                            </div>
                                            <div className="flex gap-4 text-sm text-gray-500">
                                                <span>{s.duration_minutes} min</span>
                                                <span>{parseFloat(s.price) > 0 ? `$${s.price}` : "Free"}</span>
                                                <span>{s.booking_count || 0} bookings</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </>
                    )}

                    {/* Bookings Tab */}
                    {tab === "bookings" && (
                        <>
                            {bookings.length === 0 ? (
                                <div className="text-center py-16 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                    <img src={emptyStateAvatar("no-bookings")} alt="" className="w-16 h-16 mx-auto mb-4 rounded-xl" />
                                    <h2 className="text-xl font-semibold mb-2">No bookings yet</h2>
                                    <p className="text-gray-500">Bookings will appear here when clients schedule appointments.</p>
                                </div>
                            ) : (
                                <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                                    <table className="w-full text-sm">
                                        <thead className="bg-gray-50 dark:bg-gray-800">
                                            <tr>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-300">Client</th>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-300">Service</th>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-300">Date & Time</th>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-300">Status</th>
                                                <th className="text-right px-4 py-3 font-medium text-gray-600 dark:text-gray-300">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                            {bookings.map((b) => (
                                                <tr key={b.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                                                    <td className="px-4 py-3">
                                                        <div className="font-medium">{b.client_name}</div>
                                                        <div className="text-xs text-gray-400">{b.client_email}</div>
                                                    </td>
                                                    <td className="px-4 py-3 text-gray-500">{b.service_name}</td>
                                                    <td className="px-4 py-3 text-gray-500">{formatDateTime(b.start_time)}</td>
                                                    <td className="px-4 py-3">
                                                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge(b.status)}`}>
                                                            {b.status}
                                                        </span>
                                                    </td>
                                                    <td className="px-4 py-3 text-right">
                                                        {b.status === "pending" && (
                                                            <div className="flex gap-1 justify-end">
                                                                <button
                                                                    onClick={() => confirmBooking(b.id)}
                                                                    className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                                                                >
                                                                    Confirm
                                                                </button>
                                                                <button
                                                                    onClick={() => cancelBooking(b.id)}
                                                                    className="px-2 py-1 text-xs border border-red-300 text-red-600 rounded hover:bg-red-50"
                                                                >
                                                                    Cancel
                                                                </button>
                                                            </div>
                                                        )}
                                                        {b.status === "confirmed" && (
                                                            <button
                                                                onClick={() => cancelBooking(b.id)}
                                                                className="px-2 py-1 text-xs text-gray-500 hover:text-red-600"
                                                            >
                                                                Cancel
                                                            </button>
                                                        )}
                                                    </td>
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
