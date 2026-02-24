"use client";

import { useEffect, useState } from "react";
import { paymentsAPI } from "@/lib/api";

interface Payment {
    id: string;
    customer_email: string;
    customer_name: string;
    amount: string;
    display_amount: string;
    currency: string;
    status: string;
    payment_method: string;
    created_at: string;
}

interface Subscription {
    id: string;
    customer_email: string;
    plan_name: string;
    amount: string;
    status: string;
    current_period_end: string;
}

interface Invoice {
    id: string;
    invoice_number: string;
    customer_email: string;
    total: string;
    status: string;
    due_date: string;
}

type Tab = "overview" | "payments" | "subscriptions" | "invoices";

export default function PaymentsPage() {
    const [tab, setTab] = useState<Tab>("overview");
    const [payments, setPayments] = useState<Payment[]>([]);
    const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
    const [invoices, setInvoices] = useState<Invoice[]>([]);
    const [loading, setLoading] = useState(true);
    const [stripeConnected, setStripeConnected] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        setLoading(true);
        try {
            const [p, s, i, sc] = await Promise.all([
                paymentsAPI.payments().catch(() => ({ data: [] })),
                paymentsAPI.subscriptions().catch(() => ({ data: [] })),
                paymentsAPI.invoices().catch(() => ({ data: [] })),
                paymentsAPI.stripeConnection().catch(() => ({ data: [] })),
            ]);
            setPayments(p.data?.results || p.data || []);
            setSubscriptions(s.data?.results || s.data || []);
            setInvoices(i.data?.results || i.data || []);
            const conns = Array.isArray(sc.data) ? sc.data : sc.data?.results || [];
            setStripeConnected(conns.some((c: { status: string }) => c.status === "active"));
        } catch (e) {
            console.error("Failed to load payments data", e);
        } finally {
            setLoading(false);
        }
    }

    async function connectStripe() {
        try {
            const res = await paymentsAPI.onboardStripe();
            if (res.data?.onboarding_url) {
                window.open(res.data.onboarding_url, "_blank");
            }
        } catch (e) {
            console.error("Failed to start Stripe onboarding", e);
        }
    }

    async function sendInvoice(id: string) {
        try {
            await paymentsAPI.sendInvoice(id);
            loadData();
        } catch (e) {
            console.error("Failed to send invoice", e);
        }
    }

    const totalRevenue = payments
        .filter((p) => p.status === "completed")
        .reduce((sum, p) => sum + parseFloat(p.amount || "0"), 0);

    const activeSubscriptions = subscriptions.filter((s) => s.status === "active").length;
    const mrr = subscriptions
        .filter((s) => s.status === "active")
        .reduce((sum, s) => sum + parseFloat(s.amount || "0"), 0);

    const statusBadge = (status: string) => {
        const styles: Record<string, string> = {
            completed: "bg-green-100 text-green-700",
            active: "bg-green-100 text-green-700",
            paid: "bg-green-100 text-green-700",
            pending: "bg-yellow-100 text-yellow-700",
            draft: "bg-gray-100 text-gray-600",
            overdue: "bg-red-100 text-red-600",
            cancelled: "bg-red-100 text-red-600",
            refunded: "bg-orange-100 text-orange-700",
            past_due: "bg-red-100 text-red-600",
        };
        return styles[status] || "bg-gray-100 text-gray-600";
    };

    const tabs: { key: Tab; label: string }[] = [
        { key: "overview", label: "Overview" },
        { key: "payments", label: "Payments" },
        { key: "subscriptions", label: "Subscriptions" },
        { key: "invoices", label: "Invoices" },
    ];

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Payments</h1>
                    <p className="text-gray-500 mt-1">Track revenue, manage subscriptions, and send invoices.</p>
                </div>
                {!stripeConnected && (
                    <button
                        onClick={connectStripe}
                        className="px-4 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                    >
                        Connect Stripe
                    </button>
                )}
            </div>

            {/* Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
                {tabs.map((t) => (
                    <button
                        key={t.key}
                        onClick={() => setTab(t.key)}
                        className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                            tab === t.key
                                ? "border-blue-600 text-blue-600"
                                : "border-transparent text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        {t.label}
                    </button>
                ))}
            </div>

            {loading ? (
                <div className="text-center py-20 text-gray-400">Loading...</div>
            ) : (
                <>
                    {/* Overview */}
                    {tab === "overview" && (
                        <>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                                {[
                                    { label: "Total Revenue", value: `$${totalRevenue.toFixed(2)}`, icon: "💰" },
                                    { label: "MRR", value: `$${mrr.toFixed(2)}`, icon: "📈" },
                                    { label: "Active Subs", value: activeSubscriptions.toString(), icon: "🔄" },
                                    { label: "Transactions", value: payments.length.toString(), icon: "💳" },
                                ].map((stat) => (
                                    <div key={stat.label} className="p-5 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-xs text-gray-500">{stat.label}</span>
                                            <span className="text-xl">{stat.icon}</span>
                                        </div>
                                        <span className="text-2xl font-bold">{stat.value}</span>
                                    </div>
                                ))}
                            </div>

                            {!stripeConnected && (
                                <div className="p-8 text-center bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700">
                                    <p className="text-5xl mb-4">💳</p>
                                    <h2 className="text-xl font-semibold mb-2">Connect Stripe to Get Started</h2>
                                    <p className="text-gray-500 mb-4">Accept payments, manage subscriptions, and send invoices.</p>
                                    <button
                                        onClick={connectStripe}
                                        className="px-6 py-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                                    >
                                        Connect Stripe
                                    </button>
                                </div>
                            )}

                            {/* Recent Payments */}
                            {payments.length > 0 && (
                                <div className="mt-6">
                                    <h3 className="font-semibold mb-3">Recent Payments</h3>
                                    <div className="space-y-2">
                                        {payments.slice(0, 5).map((p) => (
                                            <div key={p.id} className="flex items-center justify-between p-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                                <div>
                                                    <span className="font-medium">{p.customer_name || p.customer_email}</span>
                                                    <span className="text-xs text-gray-400 ml-2">{p.payment_method}</span>
                                                </div>
                                                <div className="flex items-center gap-3">
                                                    <span className={`px-2 py-0.5 rounded-full text-xs ${statusBadge(p.status)}`}>{p.status}</span>
                                                    <span className="font-semibold">${p.amount}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    )}

                    {/* Payments Table */}
                    {tab === "payments" && (
                        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                            {payments.length === 0 ? (
                                <div className="text-center py-16 text-gray-400">
                                    <p className="text-4xl mb-3">💳</p>
                                    <p>No payments recorded yet.</p>
                                </div>
                            ) : (
                                <table className="w-full text-sm">
                                    <thead className="bg-gray-50 dark:bg-gray-800">
                                        <tr>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Customer</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Amount</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Method</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Date</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                        {payments.map((p) => (
                                            <tr key={p.id}>
                                                <td className="px-4 py-3">{p.customer_name || p.customer_email}</td>
                                                <td className="px-4 py-3 font-medium">${p.amount}</td>
                                                <td className="px-4 py-3 text-gray-500">{p.payment_method || "—"}</td>
                                                <td className="px-4 py-3">
                                                    <span className={`px-2 py-0.5 rounded-full text-xs ${statusBadge(p.status)}`}>{p.status}</span>
                                                </td>
                                                <td className="px-4 py-3 text-gray-500">{new Date(p.created_at).toLocaleDateString()}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    )}

                    {/* Subscriptions */}
                    {tab === "subscriptions" && (
                        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                            {subscriptions.length === 0 ? (
                                <div className="text-center py-16 text-gray-400">
                                    <p className="text-4xl mb-3">🔄</p>
                                    <p>No subscriptions yet.</p>
                                </div>
                            ) : (
                                <table className="w-full text-sm">
                                    <thead className="bg-gray-50 dark:bg-gray-800">
                                        <tr>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Customer</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Plan</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Amount</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Renews</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                        {subscriptions.map((s) => (
                                            <tr key={s.id}>
                                                <td className="px-4 py-3">{s.customer_email}</td>
                                                <td className="px-4 py-3">{s.plan_name || "—"}</td>
                                                <td className="px-4 py-3 font-medium">${s.amount}/mo</td>
                                                <td className="px-4 py-3">
                                                    <span className={`px-2 py-0.5 rounded-full text-xs ${statusBadge(s.status)}`}>{s.status}</span>
                                                </td>
                                                <td className="px-4 py-3 text-gray-500">
                                                    {s.current_period_end ? new Date(s.current_period_end).toLocaleDateString() : "—"}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    )}

                    {/* Invoices */}
                    {tab === "invoices" && (
                        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                            {invoices.length === 0 ? (
                                <div className="text-center py-16 text-gray-400">
                                    <p className="text-4xl mb-3">📄</p>
                                    <p>No invoices yet.</p>
                                </div>
                            ) : (
                                <table className="w-full text-sm">
                                    <thead className="bg-gray-50 dark:bg-gray-800">
                                        <tr>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Invoice #</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Customer</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Total</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600">Due</th>
                                            <th className="text-right px-4 py-3 font-medium text-gray-600">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                        {invoices.map((inv) => (
                                            <tr key={inv.id}>
                                                <td className="px-4 py-3 font-mono">{inv.invoice_number}</td>
                                                <td className="px-4 py-3">{inv.customer_email}</td>
                                                <td className="px-4 py-3 font-medium">${inv.total}</td>
                                                <td className="px-4 py-3">
                                                    <span className={`px-2 py-0.5 rounded-full text-xs ${statusBadge(inv.status)}`}>{inv.status}</span>
                                                </td>
                                                <td className="px-4 py-3 text-gray-500">
                                                    {inv.due_date ? new Date(inv.due_date).toLocaleDateString() : "—"}
                                                </td>
                                                <td className="px-4 py-3 text-right">
                                                    {inv.status === "draft" && (
                                                        <button
                                                            onClick={() => sendInvoice(inv.id)}
                                                            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                                                        >
                                                            Send
                                                        </button>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
