const tg = window.Telegram.WebApp;
tg.expand();

let userId = null;

if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
    userId = tg.initDataUnsafe.user.id;
} else {
    document.getElementById("status").innerText = "Telegram session error";
    document.getElementById("action").disabled = true;
}

async function checkStatus() {
    if (!userId) return;

    const res = await fetch("/api/status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId })
    });

    const data = await res.json();

    if (data.premium) {
        document.getElementById("status").innerText = "Premium Active";
        document.getElementById("action").innerText = "Activated";
        document.getElementById("action").disabled = true;
    } else {
        document.getElementById("status").innerText = "Free Plan";
    }
}

async function activate() {
    if (!userId) return;

    await fetch("/api/activate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId })
    });

    checkStatus();
}

checkStatus();
