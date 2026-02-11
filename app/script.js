const tg = window.Telegram.WebApp;
tg.expand();

const userId = tg.initDataUnsafe.user?.id || Math.floor(Math.random()*100000);

async function loadStatus(){
  const res = await fetch("/api/status",{
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body:JSON.stringify({ user_id:userId })
  });

  const data = await res.json();

  document.getElementById("plan").innerText =
    data.active ? "🔥 Plan: PRO" : "🆓 Free Plan";

  document.getElementById("expires").innerText =
    data.active ? "Expires: "+data.expires_at : "";
}

async function activate(){
  await fetch("/api/activate",{
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body:JSON.stringify({ user_id:userId, plan:"pro" })
  });

  loadStatus();
}

loadStatus();
