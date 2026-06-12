// CardioCare Gemini Floating Chat — report-aware

let chatHistory  = [];
let chatOpen     = false;
const reportCtx  = window.REPORT_CONTEXT || null;

function toggleChat() {
  chatOpen = !chatOpen;
  const panel  = document.getElementById("chatPanel");
  const bubble = document.getElementById("chatBubble");
  const unread = document.getElementById("chatUnread");

  panel.classList.toggle("open", chatOpen);
  bubble.classList.toggle("active", chatOpen);
  unread.style.display = "none";

  if (chatOpen) {
    document.getElementById("chatInput").focus();

    // If on result page and chat opened for first time, show context badge + greeting
    if (reportCtx && chatHistory.length === 0) {
      const badge = document.getElementById("chatContextBadge");
      if (badge) badge.style.display = "flex";
      // Auto greeting based on risk
      const greet = reportCtx.score >= 60
        ? `I can see your latest report shows <strong>${reportCtx.risk}</strong> with a score of <strong>${reportCtx.score}/100</strong>. That's something worth discussing. Ask me anything about your results — I'm here to help! 💙`
        : reportCtx.score >= 30
        ? `Your latest report shows <strong>${reportCtx.risk}</strong> (score: <strong>${reportCtx.score}/100</strong>). There are some things to keep an eye on. Ask me anything!`
        : `Great news — your latest report shows <strong>${reportCtx.risk}</strong> with a score of <strong>${reportCtx.score}/100</strong>. Ask me anything about your results! ✅`;

      setTimeout(() => appendMessage("assistant", greet), 400);
    }
  }
}

async function sendMessage() {
  const input = document.getElementById("chatInput");
  const text  = input.value.trim();
  if (!text) return;

  input.value = "";
  appendMessage("user", text);
  chatHistory.push({ role: "user", text });

  const typingId = appendTyping();

  try {
    const body = { messages: chatHistory };
    if (reportCtx) body.report_context = reportCtx;

    const res  = await fetch("/api/chat", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(body),
    });
    const data = await res.json();
    removeTyping(typingId);
    appendMessage("assistant", data.reply);
    chatHistory.push({ role: "model", text: data.reply });
    if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);

  } catch (err) {
    removeTyping(typingId);
    appendMessage("assistant", "Sorry, couldn't reach the assistant right now.");
  }
}

function appendMessage(role, text) {
  const messages = document.getElementById("chatMessages");
  const div      = document.createElement("div");
  div.className  = `chat-msg ${role}`;
  const formatted = text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
  div.innerHTML = `<div class="msg-bubble">${formatted}</div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function appendTyping() {
  const messages = document.getElementById("chatMessages");
  const div = document.createElement("div");
  div.className = "chat-msg assistant";
  div.id = "typing-" + Date.now();
  div.innerHTML = `<div class="msg-bubble typing"><span></span><span></span><span></span></div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div.id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// Show unread dot after 3s if not opened
setTimeout(() => {
  if (!chatOpen) document.getElementById("chatUnread").style.display = "flex";
}, 3000);
