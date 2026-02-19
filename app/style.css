:root{
  --bg1:#120a2a;
  --bg2:#2b0a6a;
  --bg3:#5a2cff;
  --card: rgba(20,10,45,.58);
  --stroke: rgba(255,255,255,.10);
  --text: rgba(255,255,255,.92);
  --muted: rgba(255,255,255,.68);
  --shadow: 0 30px 80px rgba(0,0,0,.45);
  --blur: blur(22px);
  --r: 22px;
}

*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0;
  color:var(--text);
  background: radial-gradient(1200px 900px at 50% 10%, #6a39ff 0%, #2b0a6a 45%, #120a2a 100%);
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
  overflow-x:hidden;
}

.bg{position:fixed; inset:0; pointer-events:none; overflow:hidden}
#stars{position:absolute; inset:0; width:100%; height:100%; opacity:.7}
.glow{
  position:absolute; width:520px; height:520px; border-radius:50%;
  filter: blur(80px);
  opacity:.55;
}
.g1{left:-120px; top:-120px; background:#9b5cff}
.g2{right:-160px; top:25%; background:#3c78ff}
.g3{left:20%; bottom:-200px; background:#ff4bd8; opacity:.35}

.shell{
  width:min(1100px, 94vw);
  margin: 28px auto 40px;
  padding-bottom: 30px;
}

.topbar{
  display:flex; align-items:center; justify-content:space-between;
  margin-bottom: 14px;
}

.brand{display:flex; gap:12px; align-items:center}
.logo{
  width:44px; height:44px; border-radius:14px;
  display:grid; place-items:center;
  background: linear-gradient(135deg, rgba(255,255,255,.22), rgba(255,255,255,.06));
  border:1px solid var(--stroke);
  box-shadow: 0 20px 50px rgba(0,0,0,.25);
}
.name{font-weight:800; letter-spacing:.2px; font-size:16px}
.tag{font-size:12px; color:var(--muted)}

.chip{
  border:1px solid var(--stroke);
  background: rgba(255,255,255,.08);
  color: var(--text);
  padding:8px 12px;
  border-radius:999px;
  box-shadow: 0 10px 30px rgba(0,0,0,.22);
  backdrop-filter: var(--blur);
}

.card{
  background: var(--card);
  border: 1px solid var(--stroke);
  border-radius: var(--r);
  box-shadow: var(--shadow);
  backdrop-filter: var(--blur);
}

.hero{
  display:grid;
  grid-template-columns: 1.2fr .8fr;
  gap: 18px;
  padding: 18px;
  position:relative;
  overflow:hidden;
}
.hero:before{
  content:"";
  position:absolute; inset:-1px;
  background: radial-gradient(700px 250px at 20% 10%, rgba(255,255,255,.14), transparent 60%),
              radial-gradient(600px 260px at 75% 35%, rgba(120,120,255,.18), transparent 60%);
  pointer-events:none;
}

.heroLeft{padding: 10px 10px 12px 10px}
.heroLeft h1{margin:0 0 8px 0; font-size:28px; letter-spacing:.2px}
.muted{color:var(--muted)}
.fine{margin-top:10px; font-size:12px}

.kpis{
  margin-top:14px;
  display:grid;
  grid-template-columns: repeat(3, 1fr);
  gap:10px;
}
.kpi{
  padding:12px;
  border-radius:16px;
  border:1px solid var(--stroke);
  background: rgba(255,255,255,.05);
}
.kpiLabel{font-size:12px; color:var(--muted)}
.kpiValue{margin-top:6px; font-weight:800}
.mono{font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; font-size:12px}

.actions{display:flex; gap:10px; margin-top:14px; flex-wrap:wrap}

.btn{
  position:relative;
  border:1px solid var(--stroke);
  background: rgba(255,255,255,.07);
  color:var(--text);
  padding: 12px 14px;
  border-radius: 16px;
  cursor:pointer;
  transition: transform .12s ease, box-shadow .2s ease, background .2s ease;
  box-shadow: 0 16px 40px rgba(0,0,0,.25);
}
.btn:hover{transform: translateY(-1px)}
.btn:active{transform: translateY(1px) scale(.99)}

.btn.primary{
  border-color: rgba(155,92,255,.55);
  background: linear-gradient(135deg, rgba(155,92,255,.55), rgba(60,120,255,.35));
  overflow:hidden;
}
.btnGlow{
  position:absolute; inset:-60px;
  background: radial-gradient(circle at 30% 40%, rgba(255,255,255,.30), transparent 55%);
  transform: translateX(-10%);
  filter: blur(10px);
  opacity:.55;
  animation: sweep 4.2s ease-in-out infinite;
  pointer-events:none;
}
@keyframes sweep{
  0%{transform: translateX(-30%)}
  50%{transform: translateX(20%)}
  100%{transform: translateX(-30%)}
}

.btn.small{padding:10px 12px; border-radius:14px; font-size:13px}
.btn.ghost{background: transparent}

.heroRight{display:flex; flex-direction:column; gap:12px; padding:10px}

.stack{display:flex; flex-direction:column; gap:10px}
.stackItem{
  display:flex; gap:10px; align-items:flex-start;
  padding:12px;
  border-radius:16px;
  border:1px solid var(--stroke);
  background: rgba(255,255,255,.05);
}
.dot{width:10px; height:10px; border-radius:50%; margin-top:4px; background:rgba(255,255,255,.25)}
.dot.ok{background: rgba(120,255,190,.75); box-shadow:0 0 0 6px rgba(120,255,190,.12)}
.stackTitle{font-weight:800}
.stackDesc{font-size:12px; color:var(--muted); margin-top:2px}

.adminGate{
  padding:12px;
  border-radius:16px;
  border:1px solid var(--stroke);
  background: rgba(255,255,255,.05);
}
.adminTitle{font-weight:800; margin-bottom:8px}
.adminRow{display:flex; gap:10px}
.input{
  width:100%;
  padding:12px 12px;
  border-radius:14px;
  border:1px solid var(--stroke);
  background: rgba(0,0,0,.22);
  color: var(--text);
  outline:none;
}
.input::placeholder{color: rgba(255,255,255,.45)}
.adminHint{font-size:12px; margin-top:8px}

.panel{margin-top:16px; padding:14px}
.panelTop{
  display:flex; align-items:flex-end; justify-content:space-between; gap:10px; flex-wrap:wrap;
}
.panelTitle{font-weight:900; font-size:16px}
.panelActions{display:flex; gap:10px; align-items:center; flex-wrap:wrap}

.table{margin-top:12px; border:1px solid var(--stroke); border-radius:16px; overflow:hidden}
.thead,.row{
  display:grid;
  grid-template-columns: 1.2fr .8fr .6fr 1.6fr 1fr;
  gap:10px;
  align-items:center;
  padding:12px;
}
.thead{
  background: rgba(255,255,255,.06);
  font-size:12px; color: var(--muted);
}
.tbody{display:flex; flex-direction:column}
.row{border-top:1px solid rgba(255,255,255,.08); background: rgba(0,0,0,.10)}
.badge{
  display:inline-flex; align-items:center; gap:6px;
  padding:6px 10px;
  border-radius:999px;
  border:1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.06);
  font-size:12px;
}
.badge.ok{border-color: rgba(120,255,190,.35)}
.badge.warn{border-color: rgba(255,200,120,.35)}
.row .mono{font-size:11px}

.foot{margin-top:16px; text-align:center; font-size:12px}

.toast{
  position: fixed;
  left: 50%;
  bottom: 18px;
  transform: translateX(-50%);
  background: rgba(0,0,0,.55);
  border: 1px solid rgba(255,255,255,.16);
  color: rgba(255,255,255,.92);
  padding: 10px 12px;
  border-radius: 14px;
  box-shadow: 0 20px 60px rgba(0,0,0,.45);
  backdrop-filter: blur(18px);
  max-width: 92vw;
}

@media (max-width: 900px){
  .hero{grid-template-columns: 1fr}
  .kpis{grid-template-columns: 1fr}
  .thead,.row{grid-template-columns: 1.2fr .8fr .6fr 1.2fr 1fr}
}
