const API_BASE = "http://localhost:8000/api";
let sessionId = localStorage.getItem("session_id") || crypto.randomUUID();
localStorage.setItem("session_id", sessionId);
const messagesDiv = document.getElementById("chat-messages");
const userInput = document.getElementById("user-input");
function addMessage(text, sender) {
    const div = document.createElement("div");
    div.className = `message ${sender}`;
    div.innerHTML = `<div class="content">${text.replace(/\n/g, "<br>")}</div>`;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
async function sendMessage() {
    const msg = userInput.value.trim();
    if (!msg) return;
    addMessage(msg, "user");
    userInput.value = "";
    const typing = document.createElement("div");
    typing.className = "message assistant";
    typing.innerHTML = `<div class="content">Typing<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></div>`;
    messagesDiv.appendChild(typing);
    try {
        const res = await fetch(`${API_BASE}/chat/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg, session_id: sessionId })
        });
        const data = await res.json();
        messagesDiv.removeChild(typing);
        addMessage(data.response, "assistant");
    } catch(e) {
        messagesDiv.removeChild(typing);
        addMessage("Error: " + e.message, "assistant");
    }
}
document.getElementById("send-btn").onclick = sendMessage;
userInput.addEventListener("keypress", (e) => { if(e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
async function loadStats() {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    const stats = await res.json();
    document.getElementById("stats").innerHTML = `
        <div class="stat">📊 Total SKUs: ${stats.total_skus}</div>
        <div class="stat">⚠️ Low Stock: ${stats.low_stock_count}</div>
        <div class="stat">💰 Value: $${stats.total_inventory_value.toLocaleString()}</div>
    `;
    const alertRes = await fetch(`${API_BASE}/dashboard/alerts`);
    const alerts = await alertRes.json();
    const alertsDiv = document.getElementById("alerts");
    if(alerts.length === 0) alertsDiv.innerHTML = "<p>No alerts</p>";
    else alertsDiv.innerHTML = alerts.map(a => `<div class="alert">🔴 ${a.product_name}: ${a.current_stock} left (reorder at ${a.reorder_level})</div>`).join("");
}
loadStats();
setInterval(loadStats, 30000);
document.querySelectorAll(".suggestion").forEach(btn => {
    btn.onclick = () => { userInput.value = btn.innerText; sendMessage(); };
});
