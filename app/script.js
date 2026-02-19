(function () {
  const tg = window.Telegram?.WebApp;
  if (tg) {
    try { tg.expand(); } catch (e) {}
    try { tg.ready(); } catch (e) {}
  }

  const $ = (id) => document.getElementById(id);

  const uidEl = $("uid");
  const planEl = $("plan");
  const statusEl = $("status");
  const expEl = $("expires");
  const toastEl = $("toast");
  const hintEl = $("hint");

  const btnActivate = $("btnActivate");
  const btnRefresh = $("btnRefresh");

  const adminKey = $("adminKey");
  const adminUserId = $("adminUserId");
  const btnAdminPro = $("btnAdminPro");
  const btnAdminFree = $("btnAdminFree");

  function toast(msg) {
    toastEl.textContent = msg || "";
  }

  function getUID() {
    // 1) Telegram user id
    const tgId = tg?.initDataUnsafe?.user?.id;
    if (tgId) return String(tgId);

    // 2) Browser demo mode: ?uid=123
    const u = new URL(window.location.href);
    const q = u.searchParams.get("uid");
    if (q) return String(q);

    return null;
  }

  async function api(path, payload) {
    // Always POST (your backend endpoints are POST)
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload || {}),
    });

    let data;
    try { data = await res.json(); }
    catch { data = { error: "bad_json" }; }

    if (!res.ok) {
      const msg = data?.detail || data?.error || ("HTTP " + res.status);
      throw new Error(msg);
    }
    return data;
  }

  function fmtExpires(x) {
    if (!x) return "—";
    // Accept ISO string
    try {
      const d = new Date(x);
      if (!isNaN(d.getTime())) {
        return d.toISOString().replace(".000Z", "Z");
      }
    } catch (e) {}
    return String(x);
  }

  async function refresh() {
    const uid = getUID();
    if (!uid) {
      uidEl.textContent = "—";
      planEl.textContent = "—";
      expEl.textContent = "—";
      statusEl.textContent = "Open from Telegram (or add ?uid=123)";
      hintEl.style.display = "block";
      btnActivate.disabled = true;
      toast("No Telegram user id detected.");
      return;
    }

    hintEl.style.display = "none";
    uidEl.textContent = uid;
    statusEl.textContent = "Loading…";
    toast("");

    try {
      const data = await api("/api/status", { user_id: uid });
      planEl.textContent = data.plan || (data.premium ? "PRO" : "FREE");
      expEl.textContent = fmtExpires(data.expires);
      statusEl.textContent = data.premium ? "Premium active ✅" : "Free plan";
      btnActivate.disabled = !!data.premium;
    } catch (e) {
      statusEl.textContent = "API error";
      toast("Status failed: " + e.message);
      btnActivate.disabled = true;
    }
  }

  async function activate() {
    const uid = getUID();
    if (!uid) return toast("Open from Telegram or use ?uid=123");

    btnActivate.disabled = true;
    toast("Activating…");

    try {
      const data = await api("/api/activate", { user_id: uid });
      toast(data?.success ? "Activated ✅" : "Done");
      await refresh();
    } catch (e) {
      toast("Activate failed: " + e.message);
      btnActivate.disabled = false;
    }
  }

  async function adminSet(mode) {
    const key = adminKey.value.trim();
    const uid = adminUserId.value.trim();
    if (!key || !uid) return toast("Admin: enter key + user id");

    toast("Admin request…");
    try {
      const data = await api("/api/admin/set", {
        key,
        user_id: uid,
        mode, // "pro" | "free"
      });
      toast(data?.ok ? "Admin updated ✅" : "Admin done");
      await refresh();
    } catch (e) {
      toast("Admin failed: " + e.message);
    }
  }

  // Click handlers (ensure buttons are actually clickable)
  btnRefresh.addEventListener("click", refresh);
  btnActivate.addEventListener("click", activate);
  btnAdminPro.addEventListener("click", () => adminSet("pro"));
  btnAdminFree.addEventListener("click", () => adminSet("free"));

  // Stars background
  const canvas = document.getElementById("stars");
  const ctx = canvas.getContext("2d");
  let W = 0, H = 0, stars = [];

  function resize() {
    W = canvas.width = window.innerWidth * devicePixelRatio;
    H = canvas.height = window.innerHeight * devicePixelRatio;
    stars = Array.from({ length: 110 }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      r: (Math.random() * 1.6 + 0.4) * devicePixelRatio,
      a: Math.random() * 0.8 + 0.2,
      s: (Math.random() * 0.25 + 0.05) * devicePixelRatio,
    }));
  }

  function tick() {
    ctx.clearRect(0, 0, W, H);
    for (const st of stars) {
      st.y += st.s;
      if (st.y > H) st.y = 0;
      ctx.globalAlpha = st.a;
      ctx.beginPath();
      ctx.arc(st.x, st.y, st.r, 0, Math.PI * 2);
      ctx.fillStyle = "#ffffff";
      ctx.fill();
    }
    requestAnimationFrame(tick);
  }

  window.addEventListener("resize", resize);
  resize();
  tick();

  // Start
  refresh();
})();
