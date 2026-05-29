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

  // ── Markdown renderer ─────────────────────────────────────
  // Security model:
  //   1. ALL text from the LLM is HTML-escaped via esc() before any processing.
  //   2. The only HTML tags introduced are hard-coded string literals we write.
  //   3. A final allowlist sanitizer strips any tag not in the permitted set,
  //      providing defence-in-depth if the above ever had a gap.
  // Result: innerHTML is safe to use on this output.
  function renderMarkdown(raw) {
    // Step 1 — escape all characters that could form HTML tags or entities
    const esc = s => s
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");

    // Step 2 — apply inline formatting on already-escaped text only
    const inline = s => s
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/(?<!\*)\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)/g, "<em>$1</em>")
      .replace(/`([^`]+)`/g, "<code>$1</code>");

    const lines = raw.split("\n");
    const out = [];
    let listType = null;

    const closeList = () => {
      if (listType) { out.push(`</${listType}>`); listType = null; }
    };

    for (const line of lines) {
      const ul = line.match(/^[\*\-]\s+(.*)/);
      const ol = line.match(/^\d+\.\s+(.*)/);
      if (ul) {
        if (listType !== "ul") { closeList(); out.push("<ul>"); listType = "ul"; }
        out.push(`<li>${inline(esc(ul[1]))}</li>`);
      } else if (ol) {
        if (listType !== "ol") { closeList(); out.push("<ol>"); listType = "ol"; }
        out.push(`<li>${inline(esc(ol[1]))}</li>`);
      } else {
        closeList();
        const t = line.trim();
        if (!t) {
          if (out.length && out[out.length - 1] !== "<br>") out.push("<br>");
        } else {
          out.push(inline(esc(t)) + "<br>");
        }
      }
    }
    closeList();
    let html = out.join("").replace(/^(<br>)+/, "").replace(/(<br>)+$/, "");

    // Step 3 — allowlist sanitizer: strip any tag not explicitly permitted
    html = html.replace(/<\/?(?!(strong|em|code|ul|ol|li|br)\b)[a-z][^>]*>/gi, "");
    return html;
  }

  // ── Helpers ───────────────────────────────────────────────
  function appendMessage(text, role) {
    const div = document.createElement("div");
    div.className = `chat-msg ${role}`;
    // User messages: plain text (no need to render markdown)
    // Bot messages: render markdown to HTML
    if (role === "user") {
      div.textContent = text;
    } else {
      div.innerHTML = renderMarkdown(text);
    }
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

      typing.innerHTML = renderMarkdown(data.answer);
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
