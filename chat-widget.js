/**
 * Portfolio Chat Widget
 *
 * Key concepts:
 *
 * 1. SESSION ID — The first message creates a session on the server (UUID).
 *    The server returns that ID and we store it in `sessionId`.
 *    Every subsequent message sends the same ID so the server knows which
 *    conversation history to load. No login required.
 *
 * 2. FETCH API — Native browser API for HTTP requests. We POST JSON to the
 *    FastAPI backend and await the JSON response. No libraries needed.
 *
 * 3. CORS — The browser will block the request if the server does not send
 *    the right Access-Control headers. Our FastAPI already handles this.
 *
 * 4. PROGRESSIVE ENHANCEMENT — The widget injects its own HTML into the page
 *    so you only need two lines in your index.html (link + script).
 */

(function () {
  // ── Config ────────────────────────────────────────────────
  // Change this to your deployed API URL when you go to production
  const API_URL = "https://manumezog-portfolio-chat-agent.hf.space/chat";

  // ── State ─────────────────────────────────────────────────
  let sessionId = null;   // null until first message is sent

  // ── Inject HTML ───────────────────────────────────────────
  document.body.insertAdjacentHTML("beforeend", `
    <button id="chat-widget-btn" title="Ask about Manuel">💬</button>

    <div id="chat-widget-panel">
      <div id="chat-widget-header">
        <span>Ask about Manuel</span>
        <button id="chat-widget-close" title="Close">✕</button>
      </div>
      <div id="chat-widget-messages">
        <div class="chat-msg bot">
          Hi! I'm Manuel's AI assistant. Ask me anything about his education,
          experience, or projects.
        </div>
      </div>
      <div id="chat-widget-input-row">
        <input id="chat-widget-input" type="text"
               placeholder="Ask a question…" autocomplete="off" />
        <button id="chat-widget-send">Send</button>
      </div>
    </div>
  `);

  // ── DOM refs ──────────────────────────────────────────────
  const btn      = document.getElementById("chat-widget-btn");
  const panel    = document.getElementById("chat-widget-panel");
  const closeBtn = document.getElementById("chat-widget-close");
  const messages = document.getElementById("chat-widget-messages");
  const input    = document.getElementById("chat-widget-input");
  const sendBtn  = document.getElementById("chat-widget-send");

  // ── Toggle panel ──────────────────────────────────────────
  btn.addEventListener("click", () => panel.classList.toggle("open"));
  closeBtn.addEventListener("click", () => panel.classList.remove("open"));

  // ── Send on Enter key ─────────────────────────────────────
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) sendMessage();
  });
  sendBtn.addEventListener("click", sendMessage);

  // ── Helpers ───────────────────────────────────────────────
  function appendMessage(text, role) {
    const div = document.createElement("div");
    div.className = `chat-msg ${role}`;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;   // auto-scroll to bottom
    return div;
  }

  // ── Main send function ────────────────────────────────────
  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    sendBtn.disabled = true;
    appendMessage(text, "user");

    // Show "typing…" placeholder while waiting for the server
    const typing = appendMessage("Thinking…", "bot typing");

    try {
      /**
       * POST /chat
       * Body: { message: string, session_id: string | null }
       *
       * On the first call session_id is null — the server creates one and
       * returns it. We store it and send it on every subsequent call so
       * the server can retrieve the right conversation history.
       */
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      if (!response.ok) throw new Error(`Server error ${response.status}`);

      const data = await response.json();
      sessionId = data.session_id;   // save for follow-up questions

      typing.textContent = data.answer;
      typing.classList.remove("typing");

    } catch (err) {
      typing.textContent = "Sorry, I couldn't reach the server. Is the API running?";
      typing.classList.remove("typing");
      console.error("Chat widget error:", err);
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }
})();
