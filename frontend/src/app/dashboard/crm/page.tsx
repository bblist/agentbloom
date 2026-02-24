"use client";

import { useEffect, useState, useRef } from "react";
import { crmAPI } from "@/lib/api";

interface Contact {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    phone: string;
    tags: string[];
    lead_score: number;
    is_subscribed: boolean;
    created_at: string;
}

interface Campaign {
    id: string;
    name: string;
    subject: string;
    status: string;
    sent_count: number;
    open_rate: number;
    click_rate: number;
    created_at: string;
}

interface Deal {
    id: string;
    title: string;
    value: string;
    stage: string;
    contact_name: string;
    created_at: string;
}

type Tab = "contacts" | "campaigns" | "deals";

export default function CRMPage() {
    const [tab, setTab] = useState<Tab>("contacts");
    const [contacts, setContacts] = useState<Contact[]>([]);
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [deals, setDeals] = useState<Deal[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddContact, setShowAddContact] = useState(false);
    const [newContact, setNewContact] = useState({ first_name: "", last_name: "", email: "", phone: "" });
    const fileInput = useRef<HTMLInputElement>(null);

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        setLoading(true);
        try {
            const [c, camp, d] = await Promise.all([
                crmAPI.contacts(),
                crmAPI.campaigns(),
                crmAPI.deals(),
            ]);
            setContacts(c.data?.results || c.data || []);
            setCampaigns(camp.data?.results || camp.data || []);
            setDeals(d.data?.results || d.data || []);
        } catch (e) {
            console.error("Failed to load CRM data", e);
        } finally {
            setLoading(false);
        }
    }

    async function addContact() {
        try {
            await crmAPI.createContact(newContact);
            setNewContact({ first_name: "", last_name: "", email: "", phone: "" });
            setShowAddContact(false);
            loadData();
        } catch (e) {
            console.error("Failed to add contact", e);
        }
    }

    async function importCSV() {
        const file = fileInput.current?.files?.[0];
        if (!file) return;
        try {
            await crmAPI.importCSV(file);
            alert("CSV import started. Contacts will appear shortly.");
            loadData();
        } catch (e) {
            console.error("CSV import failed", e);
        }
    }

    async function sendCampaign(id: string) {
        if (!confirm("Send this campaign to all recipients?")) return;
        try {
            await crmAPI.sendCampaign(id);
            loadData();
        } catch (e) {
            console.error("Failed to send campaign", e);
        }
    }

    const tabs: { key: Tab; label: string; count: number }[] = [
        { key: "contacts", label: "Contacts", count: contacts.length },
        { key: "campaigns", label: "Campaigns", count: campaigns.length },
        { key: "deals", label: "Deals", count: deals.length },
    ];

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Email &amp; CRM</h1>
                    <p className="text-gray-500 mt-1">Manage contacts, run campaigns, and track deals.</p>
                </div>
                <div className="flex gap-2">
                    {tab === "contacts" && (
                        <>
                            <label className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800">
                                Import CSV
                                <input ref={fileInput} type="file" accept=".csv" className="hidden" onChange={importCSV} />
                            </label>
                            <button
                                onClick={() => setShowAddContact(!showAddContact)}
                                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                + Add Contact
                            </button>
                        </>
                    )}
                </div>
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
                        <span className="ml-2 px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-800 rounded-full">
                            {t.count}
                        </span>
                    </button>
                ))}
            </div>

            {loading ? (
                <div className="text-center py-20 text-gray-400">Loading...</div>
            ) : (
                <>
                    {/* Add Contact Form */}
                    {showAddContact && tab === "contacts" && (
                        <div className="mb-6 p-4 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                            <h3 className="font-medium mb-3">New Contact</h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                <input
                                    placeholder="First name"
                                    value={newContact.first_name}
                                    onChange={(e) => setNewContact({ ...newContact, first_name: e.target.value })}
                                    className="px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600"
                                />
                                <input
                                    placeholder="Last name"
                                    value={newContact.last_name}
                                    onChange={(e) => setNewContact({ ...newContact, last_name: e.target.value })}
                                    className="px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600"
                                />
                                <input
                                    placeholder="Email"
                                    type="email"
                                    value={newContact.email}
                                    onChange={(e) => setNewContact({ ...newContact, email: e.target.value })}
                                    className="px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600"
                                />
                                <input
                                    placeholder="Phone"
                                    value={newContact.phone}
                                    onChange={(e) => setNewContact({ ...newContact, phone: e.target.value })}
                                    className="px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600"
                                />
                            </div>
                            <div className="flex gap-2 mt-3">
                                <button onClick={addContact} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">
                                    Save
                                </button>
                                <button onClick={() => setShowAddContact(false)} className="px-4 py-2 text-sm text-gray-500">
                                    Cancel
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Contacts Table */}
                    {tab === "contacts" && (
                        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                            {contacts.length === 0 ? (
                                <div className="text-center py-16 text-gray-400">
                                    <p className="text-4xl mb-3">📧</p>
                                    <p>No contacts yet. Add your first contact or import a CSV.</p>
                                </div>
                            ) : (
                                <table className="w-full text-sm">
                                    <thead className="bg-gray-50 dark:bg-gray-800">
                                        <tr>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-300">Name</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-300">Email</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-300">Phone</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-300">Score</th>
                                            <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-300">Status</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                        {contacts.map((c) => (
                                            <tr key={c.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                                                <td className="px-4 py-3 font-medium">{c.first_name} {c.last_name}</td>
                                                <td className="px-4 py-3 text-gray-500">{c.email}</td>
                                                <td className="px-4 py-3 text-gray-500">{c.phone || "—"}</td>
                                                <td className="px-4 py-3">
                                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                                                        c.lead_score >= 70 ? "bg-green-100 text-green-700" :
                                                        c.lead_score >= 40 ? "bg-yellow-100 text-yellow-700" :
                                                        "bg-gray-100 text-gray-600"
                                                    }`}>
                                                        {c.lead_score}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <span className={`px-2 py-0.5 rounded-full text-xs ${
                                                        c.is_subscribed
                                                            ? "bg-green-100 text-green-700"
                                                            : "bg-red-100 text-red-700"
                                                    }`}>
                                                        {c.is_subscribed ? "Subscribed" : "Unsubscribed"}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    )}

                    {/* Campaigns */}
                    {tab === "campaigns" && (
                        <div className="space-y-4">
                            {campaigns.length === 0 ? (
                                <div className="text-center py-16 text-gray-400 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                    <p className="text-4xl mb-3">📨</p>
                                    <p>No campaigns yet. Create your first email campaign.</p>
                                </div>
                            ) : (
                                campaigns.map((c) => (
                                    <div key={c.id} className="p-4 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 flex items-center justify-between">
                                        <div>
                                            <h3 className="font-medium">{c.name}</h3>
                                            <p className="text-sm text-gray-500">{c.subject}</p>
                                        </div>
                                        <div className="flex items-center gap-6">
                                            <div className="text-center">
                                                <p className="text-lg font-semibold">{c.sent_count}</p>
                                                <p className="text-xs text-gray-400">Sent</p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-lg font-semibold">{c.open_rate || 0}%</p>
                                                <p className="text-xs text-gray-400">Opens</p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-lg font-semibold">{c.click_rate || 0}%</p>
                                                <p className="text-xs text-gray-400">Clicks</p>
                                            </div>
                                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                                                c.status === "sent" ? "bg-green-100 text-green-700" :
                                                c.status === "sending" ? "bg-blue-100 text-blue-700" :
                                                c.status === "draft" ? "bg-gray-100 text-gray-600" :
                                                "bg-yellow-100 text-yellow-700"
                                            }`}>
                                                {c.status}
                                            </span>
                                            {c.status === "draft" && (
                                                <button
                                                    onClick={() => sendCampaign(c.id)}
                                                    className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                                >
                                                    Send
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}

                    {/* Deals */}
                    {tab === "deals" && (
                        <div className="space-y-4">
                            {deals.length === 0 ? (
                                <div className="text-center py-16 text-gray-400 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                    <p className="text-4xl mb-3">💼</p>
                                    <p>No deals yet. Deals will appear here as they&apos;re created.</p>
                                </div>
                            ) : (
                                <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                                    <table className="w-full text-sm">
                                        <thead className="bg-gray-50 dark:bg-gray-800">
                                            <tr>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600">Deal</th>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600">Contact</th>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600">Value</th>
                                                <th className="text-left px-4 py-3 font-medium text-gray-600">Stage</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                            {deals.map((d) => (
                                                <tr key={d.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                                                    <td className="px-4 py-3 font-medium">{d.title}</td>
                                                    <td className="px-4 py-3 text-gray-500">{d.contact_name || "—"}</td>
                                                    <td className="px-4 py-3">${d.value}</td>
                                                    <td className="px-4 py-3">
                                                        <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs">
                                                            {d.stage}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
