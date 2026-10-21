"""Author: Anveshaa Kesharwaani

Build dashboard/index.html: a standalone, interactive dashboard.

- No server, no internet, no extra libraries. Double-click the file to open it.
- It reads bi_data/students_scored.csv, embeds the rows, and draws the charts
  in the browser with plain JavaScript.
- Filters (branch, CGPA band, company type) update every card and chart.

This is a working browser dashboard. It is not a Power BI or Tableau file.
"""
import json
from datetime import date
from pathlib import Path

import pandas as pd

BI_DIR = Path("bi_data")
OUT_DIR = Path("dashboard")

COLUMNS = [
    "branch", "cgpa_band", "placed", "company_type", "sector", "package_lpa",
    "ai_probability", "ai_band", "coding_score", "aptitude_score",
    "communication_score", "data_tools_score",
]

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Campus Placement Intelligence 2026 | Anveshaa Kesharwaani</title>
<style>
  :root { --bg:#f5f7fb; --card:#ffffff; --ink:#1a202c; --muted:#64748b; --line:#e2e8f0;
          --a:#4f46e5; --b:#0ea5e9; --c:#10b981; --d:#f59e0b; --bad:#ef4444; }
  :root[data-theme="dark"] { --bg:#0b1020; --card:#131a30; --ink:#e6eaf5; --muted:#93a0bd; --line:#232c49; }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--ink); }
  header { padding:24px 28px 8px; display:flex; flex-wrap:wrap; gap:12px; justify-content:space-between; align-items:flex-end; }
  h1 { margin:0; font-size:24px; letter-spacing:-.3px; }
  .by { color:var(--muted); font-size:13px; margin-top:2px; }
  .badge { font-size:12px; background:var(--a); color:#fff; padding:3px 9px; border-radius:99px; margin-left:8px; vertical-align:middle; }
  .controls { display:flex; flex-wrap:wrap; gap:10px; padding:8px 28px 4px; align-items:center; }
  select, button { background:var(--card); color:var(--ink); border:1px solid var(--line); border-radius:8px; padding:7px 10px; font-size:14px; }
  button { cursor:pointer; }
  .note { margin:6px 28px 0; font-size:12px; color:var(--muted); }
  .grid { display:grid; gap:14px; padding:14px 28px 28px; grid-template-columns:repeat(12,1fr); }
  .card { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px 18px; }
  .kpi { grid-column:span 3; }
  .kpi .v { font-size:30px; font-weight:700; letter-spacing:-.5px; }
  .kpi .l { color:var(--muted); font-size:13px; }
  .w6 { grid-column:span 6; } .w4 { grid-column:span 4; } .w12 { grid-column:span 12; }
  h2 { margin:0 0 12px; font-size:15px; }
  .row { display:grid; grid-template-columns:130px 1fr 70px; gap:10px; align-items:center; margin:7px 0; font-size:13px; }
  .row .name { color:var(--muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .track { background:var(--line); border-radius:6px; height:14px; overflow:hidden; position:relative; }
  .fill { height:100%; border-radius:6px; transition:width .35s ease; }
  .val { text-align:right; font-variant-numeric:tabular-nums; }
  .pair .track { height:8px; margin:2px 0; }
  .legend { font-size:12px; color:var(--muted); margin-bottom:6px; display:flex; gap:14px; }
  .dot { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:5px; }
  footer { text-align:center; color:var(--muted); font-size:12px; padding:0 0 26px; }
  .empty { color:var(--muted); font-size:13px; padding:8px 0; }
  @media (max-width:900px){ .kpi{grid-column:span 6} .w6,.w4{grid-column:span 12} .row{grid-template-columns:100px 1fr 60px} }
</style>
</head>
<body>
<header>
  <div>
    <h1>Campus Placement Intelligence <span class="badge">2026</span></h1>
    <div class="by">Built by Anveshaa Kesharwaani &middot; generated __GENERATED__ &middot; synthetic data</div>
  </div>
  <button id="theme" type="button">Toggle dark / light</button>
</header>

<div class="controls">
  <label>Branch <select id="f-branch"></select></label>
  <label>CGPA band <select id="f-band"></select></label>
  <label>Company type <select id="f-type"></select></label>
  <button id="reset" type="button">Reset filters</button>
</div>
<div class="note">All numbers are from fictional data made by a rule in src/generate_data.py. They show how the method works and say nothing about any real college. Company type filters apply to placed students only.</div>

<div class="grid">
  <div class="card kpi"><div class="v" id="k-students">-</div><div class="l">Students</div></div>
  <div class="card kpi"><div class="v" id="k-rate">-</div><div class="l">Placement rate</div></div>
  <div class="card kpi"><div class="v" id="k-pkg">-</div><div class="l">Average package (LPA)</div></div>
  <div class="card kpi"><div class="v" id="k-nontech">-</div><div class="l">Offers from non-tech companies</div></div>

  <div class="card w6"><h2>Placement rate by branch</h2><div id="c-branch"></div></div>
  <div class="card w6"><h2>Placement rate by CGPA band</h2><div id="c-band"></div></div>
  <div class="card w6"><h2>Offers by sector (average package on the right)</h2><div id="c-sector"></div></div>
  <div class="card w6"><h2>Does the AI score sort students? Actual placement by AI band</h2><div id="c-ai"></div></div>
  <div class="card w12"><h2>Skill gap: placed vs not placed (average score)</h2>
    <div class="legend"><span><i class="dot" style="background:var(--c)"></i>Placed</span><span><i class="dot" style="background:var(--bad)"></i>Not placed</span></div>
    <div id="c-skill"></div></div>
</div>
<footer>&copy; 2026 Anveshaa Kesharwaani &middot; MIT License &middot; Campus Placement Intelligence</footer>

<script>
const DATA = __DATA__;
const ALL = "All";
const $ = id => document.getElementById(id);
const uniq = k => [...new Set(DATA.map(d => d[k]).filter(v => v !== null))].sort();
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const pct = (n, d) => d ? 100 * n / d : null;
const fmt = (v, s = "") => v === null || v === undefined || Number.isNaN(v) ? "n/a" : v.toFixed(1) + s;

function fill(sel, label, values) {
  sel.innerHTML = "";
  [ALL, ...values].forEach(v => { const o = document.createElement("option"); o.value = v; o.textContent = v === ALL ? "All " + label : v; sel.appendChild(o); });
}
fill($("f-branch"), "branches", uniq("branch"));
fill($("f-band"), "bands", uniq("cgpa_band"));
fill($("f-type"), "types", uniq("company_type"));

function filtered() {
  const b = $("f-branch").value, g = $("f-band").value, t = $("f-type").value;
  return DATA.filter(d => (b === ALL || d.branch === b) && (g === ALL || d.cgpa_band === g) &&
                         (t === ALL || d.company_type === t));
}

function bars(el, items, color, max) {
  const box = $(el); box.innerHTML = "";
  if (!items.length) { box.innerHTML = '<div class="empty">No students match these filters.</div>'; return; }
  items.forEach(it => {
    const row = document.createElement("div"); row.className = "row";
    const n = document.createElement("div"); n.className = "name"; n.textContent = it.name; n.title = it.name;
    const tr = document.createElement("div"); tr.className = "track";
    const f = document.createElement("div"); f.className = "fill"; f.style.background = color;
    f.style.width = Math.max(0, Math.min(100, 100 * (it.value || 0) / max)) + "%";
    tr.appendChild(f);
    const v = document.createElement("div"); v.className = "val"; v.textContent = it.label;
    row.append(n, tr, v); box.appendChild(row);
  });
}

function groupRate(rows, key) {
  const m = new Map();
  rows.forEach(r => { const k = r[key]; if (k === null) return; const o = m.get(k) || { n: 0, p: 0 }; o.n++; o.p += r.placed; m.set(k, o); });
  return [...m.entries()].sort((a, b) => a[0] < b[0] ? -1 : 1).map(([k, o]) => ({ name: k, value: pct(o.p, o.n), label: fmt(pct(o.p, o.n), "%") + " (" + o.n + ")" }));
}

function render() {
  const rows = filtered();
  const placed = rows.filter(r => r.placed === 1);
  const pk = placed.map(r => r.package_lpa).filter(v => v !== null);
  const nonTech = placed.filter(r => r.company_type === "Non-tech").length;
  $("k-students").textContent = rows.length.toLocaleString();
  $("k-rate").textContent = fmt(pct(placed.length, rows.length), "%");
  $("k-pkg").textContent = fmt(mean(pk));
  $("k-nontech").textContent = fmt(pct(nonTech, placed.length), "%");

  bars("c-branch", groupRate(rows, "branch"), "var(--a)", 100);
  bars("c-band", groupRate(rows, "cgpa_band"), "var(--b)", 100);

  const sec = new Map();
  placed.forEach(r => { const o = sec.get(r.sector) || { n: 0, s: 0 }; o.n++; o.s += r.package_lpa; sec.set(r.sector, o); });
  const secItems = [...sec.entries()].sort((a, b) => b[1].n - a[1].n).map(([k, o]) => ({ name: k, value: o.n, label: o.n + " | " + (o.s / o.n).toFixed(1) }));
  bars("c-sector", secItems, "var(--c)", Math.max(1, ...secItems.map(i => i.value)));

  const order = { "Needs work": 1, "Moderate": 2, "Strong": 3 };
  bars("c-ai", groupRate(rows, "ai_band").sort((a, b) => order[a.name] - order[b.name]), "var(--d)", 100);

  const skills = [["coding_score", "Coding"], ["aptitude_score", "Aptitude"], ["communication_score", "Communication"], ["data_tools_score", "Data tools"]];
  const box = $("c-skill"); box.innerHTML = "";
  skills.forEach(([k, name]) => {
    const p = mean(rows.filter(r => r.placed === 1).map(r => r[k])), n = mean(rows.filter(r => r.placed === 0).map(r => r[k]));
    const row = document.createElement("div"); row.className = "row pair";
    const lab = document.createElement("div"); lab.className = "name"; lab.textContent = name;
    const mid = document.createElement("div");
    [[p, "var(--c)"], [n, "var(--bad)"]].forEach(([v, c]) => {
      const t = document.createElement("div"); t.className = "track";
      const f = document.createElement("div"); f.className = "fill"; f.style.background = c; f.style.width = (v || 0) + "%"; t.appendChild(f); mid.appendChild(t);
    });
    const val = document.createElement("div"); val.className = "val"; val.textContent = fmt(p) + " / " + fmt(n);
    row.append(lab, mid, val); box.appendChild(row);
  });
}

["f-branch", "f-band", "f-type"].forEach(id => $(id).addEventListener("change", render));
$("reset").addEventListener("click", () => { ["f-branch", "f-band", "f-type"].forEach(id => $(id).value = ALL); render(); });
$("theme").addEventListener("click", () => {
  const r = document.documentElement; r.dataset.theme = r.dataset.theme === "dark" ? "light" : "dark";
});
if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) document.documentElement.dataset.theme = "dark";
render();
</script>
</body>
</html>
"""


def build_dashboard(bi_dir=BI_DIR, out_dir=OUT_DIR) -> Path:
    df = pd.read_csv(Path(bi_dir) / "students_scored.csv")[COLUMNS]
    # Keep it small: round numbers, then let pandas write NaN as JSON null.
    df["package_lpa"] = df["package_lpa"].round(2)
    for col in ("coding_score", "aptitude_score", "communication_score", "data_tools_score"):
        df[col] = df[col].round(1)
    data = json.dumps(json.loads(df.to_json(orient="records")), separators=(",", ":"))
    html = TEMPLATE.replace("__DATA__", data).replace("__GENERATED__", date.today().isoformat())
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "index.html"
    path.write_text(html, encoding="utf-8")
    return path


if __name__ == "__main__":
    print(build_dashboard())
