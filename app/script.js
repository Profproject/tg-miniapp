const tg = window.Telegram?.WebApp;
if (tg) { try { tg.expand(); tg.ready(); } catch(e) {} }

const $ = (id) => document.getElementById(id);

let audioCtx;
function clickSound(){
  try{
    audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    const o = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o.type = "triangle";
    o.frequency.value = 520;
    g.gain.value = 0.028;
    o.connect(g); g.connect(audioCtx.destination);
    o.start();
    setTimeout(()=>o.stop(), 40);
  }catch(e){}
}
function haptic(type="light"){ try{ tg?.HapticFeedback?.impactOccurred(type); }catch(e){} }
function tap(){ haptic("light"); clickSound(); }

function getUserId(){
  if (tg?.initDataUnsafe?.user?.id) return tg.initDataUnsafe.user.id;
  let id = localStorage.getItem("demo_user_id");
  if (!id){
    id = String(100000000 + Math.floor(Math.random()*900000000));
    localStorage.setItem("demo_user_id", id);
  }
  return Number(id);
}

let state = { user_id: getUserId(), plan: "FREE", expires_at: null };

function log(msg){
  const box = $("log");
  if (!box) return;
  const d = document.createElement("div");
  d.textContent = msg;
  box.prepend(d);
  setTimeout(()=>d.remove(), 8000);
}

function fmt(x){
  if (!x) return "—";
  try { return new Date(x).toISOString().replace(".000Z","Z"); } catch { return String(x); }
}
function allowed(need){
  const p = (state.plan||"FREE").toUpperCase();
  if (need === "PRO") return p === "PRO" || p === "VIP";
  if (need === "VIP") return p === "VIP";
  return true;
}

async function api(path, body=null, method="POST", extraHeaders=null){
  const opt = { method, headers: {} };
  if (extraHeaders) Object.assign(opt.headers, extraHeaders);
  if (body !== null){
    opt.headers["Content-Type"] = "application/json";
    opt.body = JSON.stringify(body);
  }
  const res = await fetch(path, opt);
  const data = await res.json().catch(()=> ({}));
  if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`);
  return data;
}

function render(){
  $("uid").textContent = String(state.user_id);
  $("plan").textContent = state.plan;
  $("exp").textContent = fmt(state.expires_at);
  $("status").textContent = state.plan === "FREE" ? "Free plan" : `${state.plan} active ✅`;
}

async function refresh(){
  const data = await api("/api/status", { user_id: state.user_id });
  state.plan = data.plan;
  state.expires_at = data.expires_at;
  render();
}

async function metrics(){
  const m = await api("/api/metrics", null, "GET");
  $("mTotal").textContent = m.total_users;
  $("mPro").textContent = m.pro_users;
  $("mVip").textContent = m.vip_users;
}

async function createInvoice(plan){
  return await api("/api/pay/create", { user_id: state.user_id, plan });
}

async function checkInvoice(invoice_id){
  return await api(`/api/pay/check?invoice_id=${encodeURIComponent(invoice_id)}`, null, "GET");
}

async function pay(plan){
  tap();
  $("status").textContent = "Creating invoice…";

  const inv = await createInvoice(plan);
  if (!inv.pay_url) throw new Error("No pay_url returned");

  $("status").textContent = "Opening payment…";
  if (tg?.openLink) tg.openLink(inv.pay_url);
  else window.open(inv.pay_url, "_blank");

  // polling fallback: check every 2s up to 2 minutes
  const started = Date.now();
  while (Date.now() - started < 120000){
    await new Promise(r => setTimeout(r, 2000));
    try{
      const chk = await checkInvoice(inv.invoice_id);
      if (chk.status === "paid"){
        state.plan = chk.user.plan;
        state.expires_at = chk.user.expires_at;
        render();
        await metrics();
        $("status").textContent = `${state.plan} active ✅`;
        return;
      }
      if (chk.status === "expired"){
        $("status").textContent = "Invoice expired";
        return;
      }
      $("status").textContent = `Waiting payment… (${chk.status})`;
    }catch(e){
      $("status").textContent = "Checking…";
    }
  }
  $("status").textContent = "Waiting payment… (timeout)";
}

// refresh after returning to app
document.addEventListener("visibilitychange", ()=>{
  if (!document.hidden) refresh().then(metrics).catch(()=>{});
});

// Tabs
document.querySelectorAll(".tab").forEach(btn=>{
  btn.addEventListener("click", ()=>{
    tap();
    document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));
    btn.classList.add("active");
    const v = btn.dataset.view;
    document.querySelectorAll(".view").forEach(s=>s.classList.remove("active"));
    $(`view-${v}`).classList.add("active");
  });
});

// Buttons
$("btnRefresh").addEventListener("click", async ()=>{ tap(); await refresh(); await metrics(); });

$("btnPayPro").addEventListener("click", async ()=>{
  try { await pay("PRO"); } catch(e){ $("status").textContent = "Payment error"; }
});
$("btnPayPro2").addEventListener("click", async ()=>{
  try { await pay("PRO"); } catch(e){ $("status").textContent = "Payment error"; }
});
$("btnPayVip").addEventListener("click", async ()=>{
  try { await pay("VIP"); } catch(e){ $("status").textContent = "Payment error"; }
});
$("btnPayVip2").addEventListener("click", async ()=>{
  try { await pay("VIP"); } catch(e){ $("status").textContent = "Payment error"; }
});

$("btnUseFree").addEventListener("click", async ()=>{
  tap();
  // FREE is default; just refresh + show
  await refresh().catch(()=>{});
  $("status").textContent = "Free plan";
});
$("btnFree").addEventListener("click", async ()=>{
  tap();
  await refresh().catch(()=>{});
  $("status").textContent = "Free plan";
});

$("btnOpenDocs").addEventListener("click", ()=>{
  tap();
  const url = location.origin + "/docs";
  if (tg?.openLink) tg.openLink(url);
  else window.open(url, "_blank");
});

// Locked features modal
const modal = $("modal");
const mt = $("mt");
const mx = $("mx");
const mClose = $("mClose");
const mUpgrade = $("mUpgrade");

function openModal(title, text){
  mt.textContent = title;
  mx.textContent = text;
  modal.classList.add("show");
}
function closeModal(){ modal.classList.remove("show"); }

mClose.addEventListener("click", ()=>{ tap(); closeModal(); });
modal.addEventListener("click", (e)=>{ if (e.target === modal) closeModal(); });
mUpgrade.addEventListener("click", async ()=>{
  tap();
  closeModal();
  try { await pay("PRO"); } catch(e){ $("status").textContent = "Payment error"; }
});

document.querySelectorAll(".feat").forEach(btn=>{
  btn.addEventListener("click", ()=>{
    tap();
    const need = btn.dataset.need;
    if (allowed(need)) openModal("Unlocked ✅", "This feature is available on your plan.");
    else openModal("Locked 🔒", `Requires ${need}. Upgrade to unlock.`);
  });
});

// Admin (header-based)
async function adminSet(plan){
  tap();
  const adminKey = $("adminKey").value.trim();
  const user_id = Number($("adminUser").value.trim());
  const daysRaw = $("adminDays").value.trim();

  if (!adminKey) return log("Admin key required");
  if (!user_id) return log("User id required");

  const payload = { user_id, plan };
  if (daysRaw) payload.days = Number(daysRaw);

  try{
    const r = await api(
      "/api/admin/set_plan",
      payload,
      "POST",
      { "x-admin-key": adminKey }
    );
    log(`OK: ${r.user_id} -> ${r.plan} exp=${fmt(r.expires_at)}`);
    await metrics();
    if (user_id === state.user_id){
      state.plan = r.plan; state.expires_at = r.expires_at; render();
    }
  }catch(e){
    log("Admin error: " + e.message);
  }
}

$("aFree").addEventListener("click", ()=>adminSet("FREE"));
$("aPro").addEventListener("click", ()=>adminSet("PRO"));
$("aVip").addEventListener("click", ()=>adminSet("VIP"));

// 3D tilt
function tilt(node){
  let rect=null, max=10;
  node.addEventListener("mousemove",(e)=>{
    rect = rect || node.getBoundingClientRect();
    const x=(e.clientX-rect.left)/rect.width;
    const y=(e.clientY-rect.top)/rect.height;
    const rx=(max/2 - y*max).toFixed(2);
    const ry=(x*max - max/2).toFixed(2);
    node.style.transform=`perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg)`;
  });
  node.addEventListener("mouseleave",()=>{
    rect=null;
    node.style.transform="perspective(900px) rotateX(0deg) rotateY(0deg)";
  });
}
document.querySelectorAll(".tilt").forEach(tilt);

// Canvas particles
const canvas = document.getElementById("fx");
const ctx = canvas.getContext("2d");
let W,H,dots;

function resize(){
  W = canvas.width = innerWidth * devicePixelRatio;
  H = canvas.height = innerHeight * devicePixelRatio;
  canvas.style.width = innerWidth+"px";
  canvas.style.height = innerHeight+"px";
  dots = Array.from({length:140}, ()=>({
    x:Math.random()*W, y:Math.random()*H,
    r:(Math.random()*1.8+0.2)*devicePixelRatio,
    vx:(Math.random()*0.35+0.05)*devicePixelRatio,
    vy:(Math.random()*0.22+0.02)*devicePixelRatio,
    a:Math.random()*0.55+0.12
  }));
}
addEventListener("resize", resize);
resize();

function tick(){
  ctx.clearRect(0,0,W,H);
  for (const d of dots){
    d.x += d.vx; d.y += d.vy;
    if (d.x > W+20) d.x = -20;
    if (d.y > H+20) d.y = -20;

    const g = ctx.createRadialGradient(d.x, d.y, 0, d.x, d.y, d.r*10);
    g.addColorStop(0, `rgba(168,85,247,${d.a})`);
    g.addColorStop(0.5, `rgba(163,255,18,${d.a*0.35})`);
    g.addColorStop(1, `rgba(0,0,0,0)`);

    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(d.x,d.y,d.r*10,0,Math.PI*2);
    ctx.fill();
  }
  requestAnimationFrame(tick);
}
tick();

// init
$("uid").textContent = String(state.user_id);
render();
refresh().then(metrics).catch(()=>{});
