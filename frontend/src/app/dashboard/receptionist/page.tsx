"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { toast } from "sonner";

interface ReceptionistConfig {
  id: number;
  persona_name: string;
  greeting_message: string;
  primary_color: string;
  position: string;
  language: string;
  max_ai_turns: number;
  escalation_keywords: string[];
  custom_instructions: string;
  can_book_appointments: boolean;
  can_collect_leads: boolean;
  can_answer_faq: boolean;
  is_active: boolean;
  embed_key: string;
  embed_snippet: string;
}

interface ChatSession {
  id: string;
  visitor_name: string;
  visitor_email: string;
  status: string;
  channel: string;
  message_count: number;
  last_message: string;
  created_at: string;
}

interface Analytics {
  date: string;
  total_sessions: number;
  ai_resolved: number;
  transferred: number;
  leads_collected: number;
}

export default function ReceptionistPage() {
  const [config, setConfig] = useState<ReceptionistConfig | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [analytics, setAnalytics] = useState<Analytics[]>([]);
  const [tab, setTab] = useState<"config" | "sessions" | "analytics">("config");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [cfgRes, sessRes, analyticsRes] = await Promise.all([
        api.get("/receptionist/config/"),
        api.get("/receptionist/sessions/"),
        api.get("/receptionist/analytics/"),
      ]);
      setConfig(cfgRes.data);
      setSessions(Array.isArray(sessRes.data) ? sessRes.data : sessRes.data.results || []);
      setAnalytics(Array.isArray(analyticsRes.data) ? analyticsRes.data : analyticsRes.data.results || []);
    } catch (err) {
      toast.error("Failed to load receptionist data");
    } finally {
      setLoading(false);
    }
  }

  async function saveConfig() {
    if (!config) return;
    setSaving(true);
    try {
      const res = await api.patch("/receptionist/config/", {
        persona_name: config.persona_name,
        greeting_message: config.greeting_message,
        primary_color: config.primary_color,
        position: config.position,
        language: config.language,
        max_ai_turns: config.max_ai_turns,
        escalation_keywords: config.escalation_keywords,
        custom_instructions: config.custom_instructions,
        can_book_appointments: config.can_book_appointments,
        can_collect_leads: config.can_collect_leads,
        can_answer_faq: config.can_answer_faq,
        is_active: config.is_active,
      });
      setConfig(res.data);
      toast.success("Configuration saved!");
    } catch (err) {
      toast.error("Failed to save configuration");
    } finally {
      setSaving(false);
    }
  }

  async function closeSession(sessionId: string) {
    try {
      await api.post(`/receptionist/sessions/${sessionId}/close/`);
      toast.success("Session closed");
      setSessions((prev) =>
        prev.map((s) => (s.id === sessionId ? { ...s, status: "closed" } : s))
      );
    } catch {
      toast.error("Failed to close session");
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          AI Receptionist
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Configure your 24/7 AI chat assistant for your website
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        {(["config", "sessions", "analytics"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              tab === t
                ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            }`}
          >
            {t === "config"
              ? "Configuration"
              : t === "sessions"
              ? "Chat Sessions"
              : "Analytics"}
          </button>
        ))}
      </div>

      {/* Config Tab */}
      {tab === "config" && config && (
        <div className="space-y-6">
          {/* Active toggle */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  Widget Status
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {config.is_active
                    ? "Your chat widget is live"
                    : "Your chat widget is disabled"}
                </p>
              </div>
              <button
                onClick={() =>
                  setConfig({ ...config, is_active: !config.is_active })
                }
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  config.is_active ? "bg-green-500" : "bg-gray-300"
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    config.is_active ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Persona settings */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Persona
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  value={config.persona_name}
                  onChange={(e) =>
                    setConfig({ ...config, persona_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Language
                </label>
                <select
                  value={config.language}
                  onChange={(e) =>
                    setConfig({ ...config, language: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="pt">Portuguese</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Greeting Message
              </label>
              <textarea
                value={config.greeting_message}
                onChange={(e) =>
                  setConfig({ ...config, greeting_message: e.target.value })
                }
                rows={2}
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Custom Instructions
              </label>
              <textarea
                value={config.custom_instructions}
                onChange={(e) =>
                  setConfig({ ...config, custom_instructions: e.target.value })
                }
                rows={3}
                placeholder="Additional instructions for the AI..."
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
              />
            </div>
          </div>

          {/* Appearance */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Appearance
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Primary Color
                </label>
                <div className="flex gap-2 items-center">
                  <input
                    type="color"
                    value={config.primary_color}
                    onChange={(e) =>
                      setConfig({ ...config, primary_color: e.target.value })
                    }
                    className="w-10 h-10 rounded border cursor-pointer"
                  />
                  <input
                    type="text"
                    value={config.primary_color}
                    onChange={(e) =>
                      setConfig({ ...config, primary_color: e.target.value })
                    }
                    className="flex-1 px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Position
                </label>
                <select
                  value={config.position}
                  onChange={(e) =>
                    setConfig({ ...config, position: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                >
                  <option value="right">Bottom Right</option>
                  <option value="left">Bottom Left</option>
                </select>
              </div>
            </div>
          </div>

          {/* Capabilities */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Capabilities
            </h3>
            <div className="space-y-3">
              {[
                { key: "can_answer_faq", label: "Answer FAQs from Knowledge Base" },
                { key: "can_collect_leads", label: "Collect visitor contact info" },
                { key: "can_book_appointments", label: "Help book appointments" },
              ].map((cap) => (
                <label
                  key={cap.key}
                  className="flex items-center gap-3 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={(config as any)[cap.key]}
                    onChange={(e) =>
                      setConfig({ ...config, [cap.key]: e.target.checked })
                    }
                    className="w-4 h-4 rounded border-gray-300 text-blue-600"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {cap.label}
                  </span>
                </label>
              ))}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Max AI turns before transfer
              </label>
              <input
                type="number"
                min={1}
                max={50}
                value={config.max_ai_turns}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    max_ai_turns: parseInt(e.target.value) || 10,
                  })
                }
                className="w-24 px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Escalation Keywords (comma-separated)
              </label>
              <input
                type="text"
                value={(config.escalation_keywords || []).join(", ")}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    escalation_keywords: e.target.value
                      .split(",")
                      .map((s) => s.trim())
                      .filter(Boolean),
                  })
                }
                placeholder="urgent, speak to human, manager"
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
              />
            </div>
          </div>

          {/* Embed code */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Embed Code
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Add this snippet to any website to enable the chat widget.
            </p>
            <div className="relative">
              <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg text-sm overflow-x-auto">
                <code>{config.embed_snippet || `<script src="https://bloom.nobleblocks.com/widget/chat.js" data-key="${config.embed_key}"></script>`}</code>
              </pre>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(
                    config.embed_snippet || `<script src="https://bloom.nobleblocks.com/widget/chat.js" data-key="${config.embed_key}"></script>`
                  );
                  toast.success("Copied to clipboard!");
                }}
                className="absolute top-2 right-2 px-2 py-1 text-xs bg-white dark:bg-gray-700 border rounded shadow-sm"
              >
                Copy
              </button>
            </div>
          </div>

          {/* Save */}
          <button
            onClick={saveConfig}
            disabled={saving}
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Configuration"}
          </button>
        </div>
      )}

      {/* Sessions Tab */}
      {tab === "sessions" && (
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
          {sessions.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <p className="text-lg font-medium">No chat sessions yet</p>
              <p className="mt-1">
                Sessions will appear here once visitors start chatting
              </p>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">
                    Visitor
                  </th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">
                    Messages
                  </th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">
                    Last Message
                  </th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">
                    Date
                  </th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
                {sessions.map((s) => (
                  <tr key={s.id}>
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {s.visitor_name || "Anonymous"}
                        </p>
                        {s.visitor_email && (
                          <p className="text-xs text-gray-500">
                            {s.visitor_email}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex px-2 py-1 text-xs rounded-full font-medium ${
                          s.status === "active"
                            ? "bg-green-100 text-green-700"
                            : s.status === "transferred"
                            ? "bg-yellow-100 text-yellow-700"
                            : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {s.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600 dark:text-gray-400">
                      {s.message_count}
                    </td>
                    <td className="px-4 py-3 text-gray-600 dark:text-gray-400 max-w-xs truncate">
                      {s.last_message || "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs">
                      {new Date(s.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      {s.status === "active" && (
                        <button
                          onClick={() => closeSession(s.id)}
                          className="text-xs text-red-600 hover:underline"
                        >
                          Close
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

      {/* Analytics Tab */}
      {tab === "analytics" && (
        <div className="space-y-6">
          {/* Summary cards */}
          {analytics.length > 0 ? (
            <>
              <div className="grid grid-cols-4 gap-4">
                {[
                  {
                    label: "Total Sessions",
                    value: analytics.reduce((s, a) => s + a.total_sessions, 0),
                  },
                  {
                    label: "AI Resolved",
                    value: analytics.reduce((s, a) => s + a.ai_resolved, 0),
                  },
                  {
                    label: "Transferred",
                    value: analytics.reduce((s, a) => s + a.transferred, 0),
                  },
                  {
                    label: "Leads Collected",
                    value: analytics.reduce((s, a) => s + a.leads_collected, 0),
                  },
                ].map((card) => (
                  <div
                    key={card.label}
                    className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
                  >
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {card.label}
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                      {card.value}
                    </p>
                  </div>
                ))}
              </div>

              {/* Daily table */}
              <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">
                        Date
                      </th>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">
                        Sessions
                      </th>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">
                        AI Resolved
                      </th>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">
                        Transferred
                      </th>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">
                        Leads
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
                    {analytics.map((a) => (
                      <tr key={a.date}>
                        <td className="px-4 py-3 font-medium">{a.date}</td>
                        <td className="px-4 py-3">{a.total_sessions}</td>
                        <td className="px-4 py-3">{a.ai_resolved}</td>
                        <td className="px-4 py-3">{a.transferred}</td>
                        <td className="px-4 py-3">{a.leads_collected}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-12 text-center text-gray-500">
              <p className="text-lg font-medium">No analytics data yet</p>
              <p className="mt-1">
                Analytics are aggregated daily from chat sessions
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
