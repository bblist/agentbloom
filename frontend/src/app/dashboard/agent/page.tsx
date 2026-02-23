"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { agentAPI } from "@/lib/api";
import Cookies from "js-cookie";

// ─── Types ──────────────────────────────────────────────────────────────────

interface ChatMessage {
    id: string;
    role: "user" | "assistant" | "tool";
    content: string;
    timestamp: string;
    toolCalls?: ToolCall[];
    model?: string;
    tokens?: number;
}

interface ToolCall {
    name: string;
    args?: Record<string, unknown>;
    result?: Record<string, unknown>;
    status: "running" | "completed" | "error";
}

interface Conversation {
    id: string;
    title: string;
    updated_at: string;
}

// ─── Streaming fetch helper ────────────────────────────────────────────────

async function streamChat(
    message: string,
    conversationId: string | null,
    onToken: (token: string) => void,
    onToolStart: (tool: string, args: Record<string, unknown>) => void,
    onToolResult: (tool: string, result: Record<string, unknown>) => void,
    onDone: (data: { message_id?: string; tokens?: number }) => void,
    onError: (error: string) => void,
) {
    const token = Cookies.get("auth_token");
    const orgId = Cookies.get("org_id");
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    const body: Record<string, string> = { message };
    if (conversationId) body.conversation_id = conversationId;

    try {
        const res = await fetch(`${baseUrl}/api/v1/agent/chat/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "text/event-stream",
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
                ...(orgId ? { "X-Org-Id": orgId } : {}),
            },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            onError(errData.error || `Request failed (${res.status})`);
            return;
        }

        // Check if we got a streaming response or regular JSON
        const contentType = res.headers.get("content-type") || "";
        if (contentType.includes("text/event-stream")) {
            // SSE streaming
            const reader = res.body?.getReader();
            if (!reader) { onError("No response body"); return; }
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });

                const lines = buffer.split("\n");
                buffer = lines.pop() || "";

                for (const line of lines) {
                    if (!line.startsWith("data: ")) continue;
                    const data = line.slice(6).trim();
                    if (data === "[DONE]") {
                        onDone({});
                        return;
                    }
                    try {
                        const event = JSON.parse(data);
                        switch (event.type) {
                            case "token":
                                onToken(event.content || "");
                                break;
                            case "tool_start":
                                onToolStart(event.tool, event.args || {});
                                break;
                            case "tool_result":
                                onToolResult(event.tool, event.result || {});
                                break;
                            case "done":
                                onDone({
                                    message_id: event.message_id,
                                    tokens: event.usage?.total_tokens,
                                });
                                return;
                            case "error":
                                onError(event.error || "Stream error");
                                return;
                        }
                    } catch { /* skip malformed */ }
                }
            }
            onDone({});
        } else {
            // Regular JSON response (non-streaming fallback)
            const data = await res.json();
            const content = data.assistant_message?.content || "No response";
            onToken(content);
            onDone({
                message_id: data.assistant_message?.id,
                tokens: data.debug?.tokens,
            });
        }
    } catch (err) {
        onError(err instanceof Error ? err.message : "Network error");
    }
}

// ─── Component ─────────────────────────────────────────────────────────────

export default function AgentChatPage() {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: "welcome",
            role: "assistant",
            content:
                "Hi! I'm your AgentBloom AI assistant. I can help you build websites, " +
                "write copy, manage your business, and more. What would you like to do?",
            timestamp: new Date().toISOString(),
        },
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [conversationId, setConversationId] = useState<string | null>(null);
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [showSidebar, setShowSidebar] = useState(false);
    const [streamingContent, setStreamingContent] = useState("");
    const [activeToolCalls, setActiveToolCalls] = useState<ToolCall[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, streamingContent]);

    // Load conversations list
    useEffect(() => {
        async function loadConversations() {
            try {
                const { data } = await agentAPI.conversations();
                setConversations(data.results || data || []);
            } catch { /* not logged in yet */ }
        }
        loadConversations();
    }, []);

    // Handle send
    const handleSend = useCallback(async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: "user",
            content: input.trim(),
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setLoading(true);
        setStreamingContent("");
        setActiveToolCalls([]);

        let accumulatedContent = "";

        await streamChat(
            userMsg.content,
            conversationId,
            // onToken
            (token) => {
                accumulatedContent += token;
                setStreamingContent(accumulatedContent);
            },
            // onToolStart
            (tool, args) => {
                setActiveToolCalls((prev) => [
                    ...prev,
                    { name: tool, args, status: "running" },
                ]);
            },
            // onToolResult
            (tool, result) => {
                setActiveToolCalls((prev) =>
                    prev.map((tc) =>
                        tc.name === tool && tc.status === "running"
                            ? { ...tc, result, status: "completed" }
                            : tc
                    )
                );
            },
            // onDone
            (data) => {
                const finalContent = accumulatedContent || "I processed your request.";
                const assistantMsg: ChatMessage = {
                    id: data.message_id || crypto.randomUUID(),
                    role: "assistant",
                    content: finalContent,
                    timestamp: new Date().toISOString(),
                    tokens: data.tokens,
                    toolCalls: activeToolCalls.length > 0 ? [...activeToolCalls] : undefined,
                };
                setMessages((prev) => [...prev, assistantMsg]);
                setStreamingContent("");
                setActiveToolCalls([]);
                setLoading(false);
            },
            // onError
            (error) => {
                const errMsg: ChatMessage = {
                    id: crypto.randomUUID(),
                    role: "assistant",
                    content: `Sorry, something went wrong: ${error}`,
                    timestamp: new Date().toISOString(),
                };
                setMessages((prev) => [...prev, errMsg]);
                setStreamingContent("");
                setActiveToolCalls([]);
                setLoading(false);
            },
        );
    }, [input, loading, conversationId, activeToolCalls]);

    // Start new conversation
    const handleNewChat = () => {
        setConversationId(null);
        setMessages([
            {
                id: "welcome",
                role: "assistant",
                content: "Hi! Starting a fresh conversation. What can I help you with?",
                timestamp: new Date().toISOString(),
            },
        ]);
        setShowSidebar(false);
    };

    // Load an existing conversation
    const loadConversation = async (id: string) => {
        try {
            const { data } = await agentAPI.conversation(id);
            setConversationId(id);
            const msgs: ChatMessage[] = (data.messages || []).map((m: Record<string, unknown>) => ({
                id: m.id as string,
                role: m.role as "user" | "assistant",
                content: m.content as string,
                timestamp: m.created_at as string,
            }));
            if (msgs.length === 0) {
                msgs.push({
                    id: "welcome",
                    role: "assistant",
                    content: "Conversation loaded. How can I help?",
                    timestamp: new Date().toISOString(),
                });
            }
            setMessages(msgs);
            setShowSidebar(false);
        } catch {
            /* ignore */
        }
    };

    return (
        <div className="flex h-full">
            {/* Conversation sidebar (mobile toggle) */}
            {showSidebar && (
                <div className="absolute inset-0 z-40 flex md:relative md:z-auto">
                    <div className="w-72 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col h-full">
                        <div className="p-3 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
                            <h2 className="font-semibold text-sm">Conversations</h2>
                            <button
                                onClick={handleNewChat}
                                className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                + New
                            </button>
                        </div>
                        <div className="flex-1 overflow-y-auto p-2 space-y-1">
                            {conversations.map((conv) => (
                                <button
                                    key={conv.id}
                                    onClick={() => loadConversation(conv.id)}
                                    className={`w-full text-left px-3 py-2 rounded-lg text-sm truncate transition-colors ${
                                        conversationId === conv.id
                                            ? "bg-blue-50 dark:bg-blue-950/50 text-blue-700"
                                            : "hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"
                                    }`}
                                >
                                    {conv.title}
                                </button>
                            ))}
                            {conversations.length === 0 && (
                                <p className="text-xs text-gray-400 text-center py-4">No conversations yet</p>
                            )}
                        </div>
                    </div>
                    <div
                        className="flex-1 bg-black/20 md:hidden"
                        onClick={() => setShowSidebar(false)}
                    />
                </div>
            )}

            {/* Main chat area */}
            <div className="flex-1 flex flex-col h-full">
                {/* Header */}
                <div className="p-4 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex items-center gap-3">
                    <button
                        onClick={() => setShowSidebar(!showSidebar)}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
                        title="Conversations"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                    <div className="flex-1">
                        <h1 className="text-lg font-semibold flex items-center gap-2">
                            <span className="text-2xl">🤖</span> AI Agent
                        </h1>
                        <p className="text-xs text-gray-500">
                            Build websites, write copy, manage your business — just ask
                        </p>
                    </div>
                    <button
                        onClick={handleNewChat}
                        className="text-sm px-3 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                        New Chat
                    </button>
                </div>

                {/* Messages area */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                        >
                            <div className={`max-w-[75%] ${msg.role === "user" ? "" : ""}`}>
                                {/* Bubble */}
                                <div
                                    className={`px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap ${
                                        msg.role === "user"
                                            ? "bg-blue-600 text-white rounded-br-sm"
                                            : "bg-gray-100 dark:bg-gray-800 rounded-bl-sm"
                                    }`}
                                >
                                    {msg.content}
                                </div>

                                {/* Tool calls */}
                                {msg.toolCalls && msg.toolCalls.length > 0 && (
                                    <div className="mt-2 space-y-1">
                                        {msg.toolCalls.map((tc, i) => (
                                            <div
                                                key={i}
                                                className="flex items-center gap-2 text-xs px-3 py-1.5 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg"
                                            >
                                                <span>{tc.status === "completed" ? "✅" : "⏳"}</span>
                                                <span className="font-mono font-medium">{tc.name}</span>
                                                <span className="text-gray-400">
                                                    {tc.status === "completed" ? "done" : "running..."}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Meta info */}
                                {msg.tokens && (
                                    <div className="mt-1 text-xs text-gray-400">
                                        {msg.tokens} tokens
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {/* Streaming response */}
                    {streamingContent && (
                        <div className="flex justify-start">
                            <div className="max-w-[75%]">
                                <div className="px-4 py-3 bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-bl-sm text-sm whitespace-pre-wrap">
                                    {streamingContent}
                                    <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-0.5" />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Active tool calls */}
                    {activeToolCalls.length > 0 && !streamingContent && (
                        <div className="flex justify-start">
                            <div className="space-y-1">
                                {activeToolCalls.map((tc, i) => (
                                    <div
                                        key={i}
                                        className="flex items-center gap-2 text-xs px-3 py-2 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg"
                                    >
                                        {tc.status === "running" ? (
                                            <span className="animate-spin">⏳</span>
                                        ) : (
                                            <span>✅</span>
                                        )}
                                        <span className="font-mono font-medium">{tc.name}</span>
                                        <span className="text-gray-400">
                                            {tc.status === "running" ? "running..." : "completed"}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Loading dots */}
                    {loading && !streamingContent && activeToolCalls.length === 0 && (
                        <div className="flex justify-start">
                            <div className="bg-gray-100 dark:bg-gray-800 px-4 py-3 rounded-2xl rounded-bl-sm">
                                <div className="flex gap-1.5">
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Suggestion chips (only show at start) */}
                {messages.length <= 1 && (
                    <div className="px-4 pb-2 flex flex-wrap gap-2">
                        {[
                            "Build me a landing page for my plumbing business",
                            "Write a tagline for a bakery",
                            "Create a pricing page with 3 tiers",
                            "Help me design a professional color palette",
                        ].map((suggestion) => (
                            <button
                                key={suggestion}
                                onClick={() => setInput(suggestion)}
                                className="text-xs px-3 py-1.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-full hover:bg-blue-50 dark:hover:bg-blue-950/30 hover:border-blue-300 transition-colors"
                            >
                                {suggestion}
                            </button>
                        ))}
                    </div>
                )}

                {/* Input bar */}
                <div className="p-4 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
                    <form onSubmit={handleSend} className="flex gap-3">
                        <input
                            ref={inputRef}
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type a message... (e.g., 'Build me a landing page for my HVAC business')"
                            className="flex-1 px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-700"
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || loading}
                            className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center gap-2"
                        >
                            {loading ? (
                                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                </svg>
                            ) : (
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                </svg>
                            )}
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
