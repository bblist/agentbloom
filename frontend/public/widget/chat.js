/**
 * AgentBloom AI Receptionist Chat Widget
 * 
 * Embed on any site:
 *   <script src="https://bloom.nobleblocks.com/widget/chat.js"
 *           data-key="YOUR_EMBED_KEY"></script>
 */
(function () {
  "use strict";

  const SCRIPT = document.currentScript;
  const EMBED_KEY = SCRIPT?.getAttribute("data-key") || "";
  const API_BASE = SCRIPT?.getAttribute("data-api") || "https://bloom.nobleblocks.com";
  const POSITION = SCRIPT?.getAttribute("data-position") || "right";

  if (!EMBED_KEY) {
    console.error("[AgentBloom] Missing data-key attribute");
    return;
  }

  /* ─── State ───────────────────────────────── */
  let config = null;
  let sessionId = null;
  let visitorId = localStorage.getItem("ab_visitor_id") || crypto.randomUUID();
  localStorage.setItem("ab_visitor_id", visitorId);

  let isOpen = false;
  let isLoading = false;
  let messages = [];

  /* ─── Fetch widget config ──────────────────── */
  async function fetchConfig() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/receptionist/widget/config/?key=${EMBED_KEY}`);
      if (!res.ok) return null;
      return await res.json();
    } catch (e) {
      console.error("[AgentBloom] Config fetch error:", e);
      return null;
    }
  }

  /* ─── Send message via REST ────────────────── */
  async function sendMessage(text) {
    try {
      const res = await fetch(`${API_BASE}/api/v1/receptionist/widget/chat/?key=${EMBED_KEY}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
          visitor_id: visitorId,
          source_url: window.location.href,
        }),
      });
      if (!res.ok) throw new Error("Chat API error");
      const data = await res.json();
      sessionId = data.session_id;
      return data;
    } catch (e) {
      console.error("[AgentBloom] Chat error:", e);
      return { response: "Sorry, something went wrong. Please try again.", transferred: false };
    }
  }

  /* ─── Build UI ────────────────────────────── */
  function injectStyles(primaryColor) {
    const style = document.createElement("style");
    style.textContent = `
      #ab-widget-root * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
      #ab-widget-fab {
        position: fixed; bottom: 20px; ${POSITION}: 20px; z-index: 99999;
        width: 60px; height: 60px; border-radius: 50%;
        background: ${primaryColor}; color: #fff; border: none; cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        display: flex; align-items: center; justify-content: center;
        transition: transform 0.2s;
      }
      #ab-widget-fab:hover { transform: scale(1.1); }
      #ab-widget-fab svg { width: 28px; height: 28px; fill: currentColor; }
      #ab-widget-panel {
        position: fixed; bottom: 90px; ${POSITION}: 20px; z-index: 99999;
        width: 380px; max-width: calc(100vw - 40px); height: 520px; max-height: calc(100vh - 120px);
        background: #fff; border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        display: none; flex-direction: column; overflow: hidden;
      }
      #ab-widget-panel.ab-open { display: flex; }
      .ab-header {
        background: ${primaryColor}; color: #fff; padding: 16px;
        display: flex; align-items: center; gap: 12px;
      }
      .ab-header-avatar {
        width: 40px; height: 40px; border-radius: 50%;
        background: rgba(255,255,255,0.2); display: flex; align-items: center;
        justify-content: center; font-size: 18px; font-weight: bold;
      }
      .ab-header-name { font-weight: 600; font-size: 16px; }
      .ab-header-status { font-size: 12px; opacity: 0.8; }
      .ab-close { margin-left: auto; background: none; border: none; color: #fff; cursor: pointer; font-size: 20px; }
      .ab-messages {
        flex: 1; overflow-y: auto; padding: 16px; display: flex;
        flex-direction: column; gap: 8px;
      }
      .ab-msg {
        max-width: 85%; padding: 10px 14px; border-radius: 16px;
        font-size: 14px; line-height: 1.4; word-wrap: break-word;
      }
      .ab-msg-assistant {
        background: #f1f3f5; color: #333; align-self: flex-start;
        border-bottom-left-radius: 4px;
      }
      .ab-msg-visitor {
        background: ${primaryColor}; color: #fff; align-self: flex-end;
        border-bottom-right-radius: 4px;
      }
      .ab-msg-system {
        background: #fff3cd; color: #856404; align-self: center;
        font-size: 12px; text-align: center; border-radius: 8px;
      }
      .ab-typing { display: flex; gap: 4px; padding: 10px 14px; align-self: flex-start; }
      .ab-typing span {
        width: 8px; height: 8px; border-radius: 50%;
        background: #ccc; animation: ab-bounce 1.4s infinite ease-in-out;
      }
      .ab-typing span:nth-child(2) { animation-delay: 0.2s; }
      .ab-typing span:nth-child(3) { animation-delay: 0.4s; }
      @keyframes ab-bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
      }
      .ab-input-bar {
        display: flex; padding: 12px; border-top: 1px solid #eee; gap: 8px;
      }
      .ab-input-bar input {
        flex: 1; padding: 10px 14px; border: 1px solid #ddd;
        border-radius: 24px; outline: none; font-size: 14px;
      }
      .ab-input-bar input:focus { border-color: ${primaryColor}; }
      .ab-input-bar button {
        width: 40px; height: 40px; border-radius: 50%;
        background: ${primaryColor}; color: #fff; border: none;
        cursor: pointer; display: flex; align-items: center; justify-content: center;
      }
      .ab-input-bar button:disabled { opacity: 0.5; cursor: not-allowed; }
      .ab-powered {
        text-align: center; padding: 6px; font-size: 11px; color: #999;
      }
      .ab-powered a { color: #777; text-decoration: none; }
    `;
    document.head.appendChild(style);
  }

  function createWidget() {
    const root = document.createElement("div");
    root.id = "ab-widget-root";

    const primaryColor = config?.primary_color || "#6366f1";
    const personaName = config?.persona_name || "Assistant";

    injectStyles(primaryColor);

    // FAB button
    const fab = document.createElement("button");
    fab.id = "ab-widget-fab";
    fab.setAttribute("aria-label", "Open chat");
    fab.innerHTML = `<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>`;
    fab.onclick = togglePanel;

    // Panel
    const panel = document.createElement("div");
    panel.id = "ab-widget-panel";
    panel.innerHTML = `
      <div class="ab-header">
        <div class="ab-header-avatar">${personaName.charAt(0)}</div>
        <div>
          <div class="ab-header-name">${personaName}</div>
          <div class="ab-header-status">Online</div>
        </div>
        <button class="ab-close" aria-label="Close chat">&times;</button>
      </div>
      <div class="ab-messages" id="ab-messages"></div>
      <div class="ab-input-bar">
        <input type="text" id="ab-input" placeholder="Type a message..." autocomplete="off" />
        <button id="ab-send" aria-label="Send">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </button>
      </div>
      <div class="ab-powered">Powered by <a href="https://bloom.nobleblocks.com" target="_blank">AgentBloom</a></div>
    `;

    root.appendChild(fab);
    root.appendChild(panel);
    document.body.appendChild(root);

    // Event listeners
    panel.querySelector(".ab-close").onclick = togglePanel;
    const input = panel.querySelector("#ab-input");
    const sendBtn = panel.querySelector("#ab-send");

    sendBtn.onclick = () => handleSend(input);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend(input);
      }
    });
  }

  function togglePanel() {
    isOpen = !isOpen;
    const panel = document.getElementById("ab-widget-panel");
    panel.classList.toggle("ab-open", isOpen);

    if (isOpen && messages.length === 0 && config?.greeting) {
      addMessage("assistant", config.greeting);
    }
  }

  function addMessage(role, content) {
    messages.push({ role, content });
    renderMessages();
  }

  function renderMessages() {
    const container = document.getElementById("ab-messages");
    if (!container) return;

    container.innerHTML = messages
      .map((m) => `<div class="ab-msg ab-msg-${m.role}">${escapeHtml(m.content)}</div>`)
      .join("");

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
  }

  function showTyping() {
    const container = document.getElementById("ab-messages");
    if (!container) return;
    const typing = document.createElement("div");
    typing.className = "ab-typing";
    typing.id = "ab-typing";
    typing.innerHTML = "<span></span><span></span><span></span>";
    container.appendChild(typing);
    container.scrollTop = container.scrollHeight;
  }

  function hideTyping() {
    const el = document.getElementById("ab-typing");
    if (el) el.remove();
  }

  async function handleSend(input) {
    const text = input.value.trim();
    if (!text || isLoading) return;

    input.value = "";
    addMessage("visitor", text);
    isLoading = true;

    const sendBtn = document.getElementById("ab-send");
    if (sendBtn) sendBtn.disabled = true;

    showTyping();

    const data = await sendMessage(text);

    hideTyping();
    isLoading = false;
    if (sendBtn) sendBtn.disabled = false;

    if (data.response) {
      addMessage("assistant", data.response);
    }
    if (data.transferred) {
      addMessage("system", "You have been transferred to a team member.");
    }
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  /* ─── Init ────────────────────────────────── */
  async function init() {
    config = await fetchConfig();
    if (!config) {
      console.error("[AgentBloom] Failed to load widget config");
      return;
    }
    createWidget();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
