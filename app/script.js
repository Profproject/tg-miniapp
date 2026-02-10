const tg = window.Telegram.WebApp;
tg.expand();

const userId = tg.initDataUnsafe.user.id;

async function checkStatus() {
  const res = await fetch("/api/status", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({user_id: userId})
  });
  const data = await res.json();

  if (data.premium) {
    document.getElementById("status").innerText = "✅ Premium active";
    document.getElementById("action").innerText = "Access Granted";
    document.getElementById("action").disabled = true;
  } else {
    document.getElementById("status").innerText = "🔒 Free access";
  }
}

async function activate() {
  await fetch("/api/activate", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({user_id: userId})
  });
  checkStatus();
}

checkStatus();
