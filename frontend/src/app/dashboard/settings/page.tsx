"use client";

import { useState, useEffect } from "react";
import { agentAPI, authAPI, orgAPI } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { toast } from "sonner";
import { shapeIcon } from "@/lib/dicebear";

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState<"agent" | "profile" | "org">("agent");
    const [agentConfig, setAgentConfig] = useState<Record<string, unknown>>({});
    const [saving, setSaving] = useState(false);
    const { user, org, setUser, setOrg } = useAuthStore();

    // Profile form
    const [profileForm, setProfileForm] = useState({
        first_name: "",
        last_name: "",
        email: "",
    });
    const [passwordForm, setPasswordForm] = useState({
        current_password: "",
        new_password: "",
        confirm_password: "",
    });

    // Org form
    const [orgForm, setOrgForm] = useState({
        name: "",
        slug: "",
        website_url: "",
        industry: "",
        description: "",
    });
    const [members, setMembers] = useState<{ id: string; user_email: string; role: string }[]>([]);
    const [inviteEmail, setInviteEmail] = useState("");

    useEffect(() => {
        async function load() {
            try {
                const { data } = await agentAPI.config();
                setAgentConfig(data);
            } catch { /* not loaded yet */ }
        }
        load();
        if (user) {
            setProfileForm({
                first_name: user.first_name || "",
                last_name: user.last_name || "",
                email: user.email || "",
            });
        }
        if (org) {
            loadOrg();
        }
    }, []);

    async function loadOrg() {
        try {
            const { data } = await orgAPI.get(org!.id);
            setOrgForm({
                name: data.name || "",
                slug: data.slug || "",
                website_url: data.website_url || "",
                industry: data.industry || "",
                description: data.description || "",
            });
            if (data.members) setMembers(data.members);
        } catch { /* not loaded */ }
    }

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

    async function saveProfile() {
        setSaving(true);
        try {
            const { data } = await authAPI.updateProfile(profileForm);
            setUser(data);
            toast.success("Profile updated");
        } catch {
            toast.error("Failed to update profile");
        } finally {
            setSaving(false);
        }
    }

    async function changePassword() {
        if (passwordForm.new_password !== passwordForm.confirm_password) {
            toast.error("Passwords do not match");
            return;
        }
        if (passwordForm.new_password.length < 8) {
            toast.error("Password must be at least 8 characters");
            return;
        }
        setSaving(true);
        try {
            await authAPI.changePassword(passwordForm);
            toast.success("Password changed");
            setPasswordForm({ current_password: "", new_password: "", confirm_password: "" });
        } catch {
            toast.error("Failed to change password");
        } finally {
            setSaving(false);
        }
    }

    async function saveOrg() {
        if (!org) return;
        setSaving(true);
        try {
            const { data } = await orgAPI.update(org.id, orgForm);
            setOrg({ ...org, name: data.name, slug: data.slug });
            toast.success("Organization updated");
        } catch {
            toast.error("Failed to update organization");
        } finally {
            setSaving(false);
        }
    }

    async function inviteMember() {
        if (!inviteEmail || !org) return;
        setSaving(true);
        try {
            await orgAPI.invite(org.id, { email: inviteEmail, role: "member" });
            toast.success(`Invitation sent to ${inviteEmail}`);
            setInviteEmail("");
            loadOrg();
        } catch {
            toast.error("Failed to send invitation");
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
        <div className="p-4 sm:p-8 max-w-4xl mx-auto">
            <h1 className="text-2xl sm:text-3xl font-bold mb-6 flex items-center gap-3">
                <img src={shapeIcon("settings-header")} alt="" className="w-9 h-9 rounded-lg" />
                Settings
            </h1>

            {/* Tabs */}
            <div className="flex gap-1 mb-8 border-b border-gray-200 dark:border-gray-800 overflow-x-auto">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-3 sm:px-4 py-2.5 text-sm font-medium -mb-px transition-colors flex items-center gap-2 whitespace-nowrap ${
                            activeTab === tab.id
                                ? "border-b-2 border-blue-600 text-blue-600"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        <img src={shapeIcon(tab.seed)} alt="" className="w-5 h-5 rounded hidden sm:block" />
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

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                            <span className="text-sm text-gray-500">{String(agentConfig.temperature || 0.7)}</span>
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
                        className="w-full sm:w-auto px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                    >
                        {saving ? "Saving..." : "Save Settings"}
                    </button>
                </div>
            )}

            {/* Profile Tab */}
            {activeTab === "profile" && (
                <div className="space-y-8">
                    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                        <h3 className="font-semibold text-lg">Personal Information</h3>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">First Name</label>
                                <input
                                    type="text"
                                    value={profileForm.first_name}
                                    onChange={(e) => setProfileForm({ ...profileForm, first_name: e.target.value })}
                                    className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Last Name</label>
                                <input
                                    type="text"
                                    value={profileForm.last_name}
                                    onChange={(e) => setProfileForm({ ...profileForm, last_name: e.target.value })}
                                    className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Email</label>
                            <input
                                type="email"
                                value={profileForm.email}
                                disabled
                                className="w-full px-4 py-2.5 border rounded-lg bg-gray-50 dark:bg-gray-800 dark:border-gray-700 text-gray-500"
                            />
                            <p className="text-xs text-gray-400 mt-1">Email cannot be changed</p>
                        </div>
                        <button
                            onClick={saveProfile}
                            disabled={saving}
                            className="w-full sm:w-auto px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                        >
                            {saving ? "Saving..." : "Update Profile"}
                        </button>
                    </div>

                    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                        <h3 className="font-semibold text-lg">Change Password</h3>
                        <div>
                            <label className="block text-sm font-medium mb-1">Current Password</label>
                            <input
                                type="password"
                                value={passwordForm.current_password}
                                onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                                className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                            />
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">New Password</label>
                                <input
                                    type="password"
                                    value={passwordForm.new_password}
                                    onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                                    className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Confirm New Password</label>
                                <input
                                    type="password"
                                    value={passwordForm.confirm_password}
                                    onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                                    className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                />
                            </div>
                        </div>
                        <button
                            onClick={changePassword}
                            disabled={saving || !passwordForm.current_password || !passwordForm.new_password}
                            className="w-full sm:w-auto px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                        >
                            {saving ? "Changing..." : "Change Password"}
                        </button>
                    </div>

                    <div className="bg-red-50 dark:bg-red-950/20 rounded-xl border border-red-200 dark:border-red-800 p-6 space-y-4">
                        <h3 className="font-semibold text-lg text-red-700 dark:text-red-400">Danger Zone</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            Once you delete your account, all data will be permanently removed.
                        </p>
                        <button
                            onClick={async () => {
                                if (!confirm("Are you sure you want to delete your account? This cannot be undone.")) return;
                                try {
                                    await authAPI.deleteAccount();
                                    toast.success("Account deleted");
                                    window.location.href = "/";
                                } catch {
                                    toast.error("Failed to delete account");
                                }
                            }}
                            className="px-6 py-2.5 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700"
                        >
                            Delete Account
                        </button>
                    </div>
                </div>
            )}

            {/* Org Tab */}
            {activeTab === "org" && (
                <div className="space-y-8">
                    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                        <h3 className="font-semibold text-lg">Organization Details</h3>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Organization Name</label>
                                <input
                                    type="text"
                                    value={orgForm.name}
                                    onChange={(e) => setOrgForm({ ...orgForm, name: e.target.value })}
                                    className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Slug</label>
                                <input
                                    type="text"
                                    value={orgForm.slug}
                                    onChange={(e) => setOrgForm({ ...orgForm, slug: e.target.value })}
                                    className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                />
                            </div>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Industry</label>
                                <select
                                    value={orgForm.industry}
                                    onChange={(e) => setOrgForm({ ...orgForm, industry: e.target.value })}
                                    className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                >
                                    <option value="">Select industry</option>
                                    <option value="marketing">Marketing Agency</option>
                                    <option value="ecommerce">E-Commerce</option>
                                    <option value="saas">SaaS / Tech</option>
                                    <option value="coaching">Coaching / Consulting</option>
                                    <option value="real_estate">Real Estate</option>
                                    <option value="health">Health & Wellness</option>
                                    <option value="fitness">Fitness</option>
                                    <option value="restaurant">Restaurant / Food</option>
                                    <option value="legal">Legal Services</option>
                                    <option value="education">Education</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Website</label>
                                <input
                                    type="url"
                                    value={orgForm.website_url}
                                    onChange={(e) => setOrgForm({ ...orgForm, website_url: e.target.value })}
                                    placeholder="https://example.com"
                                    className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Description</label>
                            <textarea
                                value={orgForm.description}
                                onChange={(e) => setOrgForm({ ...orgForm, description: e.target.value })}
                                rows={3}
                                placeholder="Brief description of your business..."
                                className="w-full px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                            />
                        </div>
                        <button
                            onClick={saveOrg}
                            disabled={saving}
                            className="w-full sm:w-auto px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                        >
                            {saving ? "Saving..." : "Save Organization"}
                        </button>
                    </div>

                    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                        <h3 className="font-semibold text-lg">Team Members</h3>
                        {members.length > 0 ? (
                            <div className="divide-y divide-gray-100 dark:divide-gray-800">
                                {members.map((m) => (
                                    <div key={m.id} className="flex items-center justify-between py-3">
                                        <div>
                                            <p className="font-medium text-sm">{m.user_email}</p>
                                            <p className="text-xs text-gray-500 capitalize">{m.role}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-sm text-gray-500">No team members yet</p>
                        )}
                        <div className="flex flex-col sm:flex-row gap-2 pt-2">
                            <input
                                type="email"
                                value={inviteEmail}
                                onChange={(e) => setInviteEmail(e.target.value)}
                                placeholder="team@example.com"
                                className="flex-1 px-4 py-2.5 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                            />
                            <button
                                onClick={inviteMember}
                                disabled={saving || !inviteEmail}
                                className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 whitespace-nowrap"
                            >
                                Send Invite
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
