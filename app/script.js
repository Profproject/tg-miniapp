const tg = window.Telegram.WebApp;
tg.expand();

const userId = tg.initDataUnsafe?.user?.id;

async function checkStatus() {
    const res = await fetch("/api/status", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({user_id: userId})
    });

    const data = await res.json();

    const statusText = document.getElementById("status");
    const dot = document.getElementById("status-dot");
    const btn = document.getElementById("action-btn");

    if (data.premium) {
        statusText.innerText = "Premium Active";
        dot.style.background = "#00ff88";
        dot.style.boxShadow = "0 0 12px #00ff88";
        btn.innerText = "Access Granted";
        btn.disabled = true;
    } else {
        statusText.innerText = "No Active Subscription";
        dot.style.background = "orange";
        dot.style.boxShadow = "0 0 12px orange";
        btn.innerText = "Activate Premium";
        btn.disabled = false;
    }
}

async function activate() {
    await fetch("/api/activate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({user_id: userId})
    });

    checkStatus();
}

checkStatus();
