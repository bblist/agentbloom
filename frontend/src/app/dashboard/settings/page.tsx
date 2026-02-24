"use client";

import { useState, useEffect } from "react";
import { agentAPI, authAPI, orgAPI } from "@/lib/api";
import { toast } from "sonner";
import { shapeIcon } from "@/lib/dicebear";

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState<"agent" | "profile" | "org">("agent");
    const [agentConfig, setAgentConfig] = useState<Record<string, unknown>>({});
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        async function load() {
            try {
                const { data } = await agentAPI.config();
                setAgentConfig(data);
            } catch { /* not loaded yet */ }
        }
        load();
    }, []);

    async function saveAgentConfig() {
        setSaving(true);
        try {
            const { data } = await agentAPI.updateConfig(agentConfig);
            setAgentConfig(data);
            toast.success("Agent settings saved");
        } catch {
            toast.error("Failed to save settings");
        } finally {
            setSaving(false);
        }
    }

    const tabs = [
        { id: "agent" as const, label: "AI Agent", seed: "settings-agent-tab" },
        { id: "profile" as const, label: "Profile", seed: "settings-profile-tab" },
        { id: "org" as const, label: "Organization", seed: "settings-org-tab" },
    ];

    return (
        <div className="p-8 max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-6 flex items-center gap-3">
                <img src={shapeIcon("settings-header")} alt="" className="w-9 h-9 rounded-lg" />
                Settings
            </h1>

            {/* Tabs */}
            <div className="flex gap-1 mb-8 border-b border-gray-200 dark:border-gray-800">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-4 py-2.5 text-sm font-medium -mb-px transition-colors flex items-center gap-2 ${
                            activeTab === tab.id
                                ? "border-b-2 border-blue-600 text-blue-600"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        <img src={shapeIcon(tab.seed)} alt="" className="w-5 h-5 rounded" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Agent Config Tab */}
            {activeTab === "agent" && (
                <div className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium mb-1">Display Name</label>
                        <input
                            type="text"
                            value={(agentConfig.display_name as string) || ""}
                            onChange={(e) => setAgentConfig({ ...agentConfig, display_name: e.target.value })}
                            className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">Persona / System Prompt</label>
                        <textarea
                            value={(agentConfig.persona as string) || ""}
                            onChange={(e) => setAgentConfig({ ...agentConfig, persona: e.target.value })}
                            rows={4}
                            className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Tone</label>
                            <select
                                value={(agentConfig.tone as string) || "friendly"}
                                onChange={(e) => setAgentConfig({ ...agentConfig, tone: e.target.value })}
                                className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                            >
                                <option value="professional">Professional</option>
                                <option value="friendly">Friendly</option>
                                <option value="casual">Casual</option>
                                <option value="formal">Formal</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1">Primary LLM</label>
                            <select
                                value={(agentConfig.llm_provider as string) || "openai"}
                                onChange={(e) => setAgentConfig({ ...agentConfig, llm_provider: e.target.value })}
                                className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                            >
                                <option value="openai">OpenAI (GPT-4o)</option>
                                <option value="claude">Claude (Anthropic)</option>
                                <option value="gemini">Gemini (Google)</option>
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Temperature</label>
                            <input
                                type="range"
                                min="0"
                                max="1"
                                step="0.1"
                                value={(agentConfig.temperature as number) || 0.7}
                                onChange={(e) => setAgentConfig({ ...agentConfig, temperature: parseFloat(e.target.value) })}
                                className="w-full"
                            />
                            <span className="text-sm text-gray-500">{agentConfig.temperature || 0.7}</span>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1">Design LLM</label>
                            <select
                                value={(agentConfig.design_provider as string) || "claude"}
                                onChange={(e) => setAgentConfig({ ...agentConfig, design_provider: e.target.value })}
                                className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                            >
                                <option value="claude">Claude (recommended)</option>
                                <option value="gemini">Gemini</option>
                                <option value="openai">OpenAI</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={(agentConfig.debug_mode as boolean) || false}
                                onChange={(e) => setAgentConfig({ ...agentConfig, debug_mode: e.target.checked })}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600" />
                        </label>
                        <span className="text-sm">Debug mode (show reasoning steps)</span>
                    </div>

                    <button
                        onClick={saveAgentConfig}
                        disabled={saving}
                        className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                    >
                        {saving ? "Saving..." : "Save Settings"}
                    </button>
                </div>
            )}

            {/* Profile Tab */}
            {activeTab === "profile" && (
                <div className="space-y-6">
                    <p className="text-gray-500">
                        Profile settings — name, email, password, and 2FA will be available here.
                    </p>
                    <div className="p-6 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                        <p className="font-mono text-sm text-gray-400">
                            Coming in Phase 2: Profile management, 2FA setup, API keys
                        </p>
                    </div>
                </div>
            )}

            {/* Org Tab */}
            {activeTab === "org" && (
                <div className="space-y-6">
                    <p className="text-gray-500">
                        Organization settings — name, branding, team members, billing.
                    </p>
                    <div className="p-6 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
                        <p className="font-mono text-sm text-gray-400">
                            Coming in Phase 2: Team management, billing, custom branding
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}
