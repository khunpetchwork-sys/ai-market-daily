const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt=d=>new Date(d).toLocaleDateString("th-TH",{weekday:"long",year:"numeric",month:"long",day:"numeric"});
document.getElementById("today").textContent=fmt(new Date());

fetch("data/news.json?ts="+Date.now()).then(r=>{if(!r.ok)throw Error();return r.json()}).then(render).catch(()=>{
document.getElementById("summary").innerHTML='<div class="summary-card"><div class="summary-icon">🤖</div><h3>ระบบพร้อมแล้ว</h3><p>เมื่อ Auto News ทำงาน ข่าวจริงจะถูกใส่เข้ามาที่นี่</p></div>';
document.getElementById("news").innerHTML='<div class="loading">ยังไม่มีข่าว — รัน GitHub Action ก่อน</div>';renderMarkets([]);});

function render(d){
const n=d.news||[];document.getElementById("newsCount").textContent=n.length+" ข่าว";
document.getElementById("summary").innerHTML=(d.quick_summary||[]).map((x,i)=>`<article class="summary-card"><div class="summary-icon">${i?"📈":"🤖"}</div><h3>${esc(x.title)}</h3><p>${esc(x.text)}</p></article>`).join("");
document.getElementById("news").innerHTML=n.map(x=>`<article class="news-card"><div class="meta"><span class="tag">${esc(x.category)}</span><span>${esc(x.source)} · ${esc(x.time)}</span></div><h3>${esc(x.title)}</h3><p>${esc(x.summary)}</p><div class="why"><strong>💡 ทำไมต้องสนใจ</strong><span>${esc(x.why)}</span></div>${x.url?`<a class="source" href="${esc(x.url)}" target="_blank" rel="noopener">อ่านต้นฉบับ →</a>`:""}</article>`).join("")||'<div class="loading">วันนี้ยังไม่มีข่าวที่ผ่านการคัดเลือก</div>';
renderMarkets(d.markets||[]);const w=d.weekly||{};document.getElementById("weekly").innerHTML=`<h3>${esc(w.title||"สรุปประจำสัปดาห์")}</h3><p>${esc(w.summary||"ระบบจะสร้าง Weekly Brief อัตโนมัติ")}</p><ul>${(w.points||[]).map(x=>`<li>${esc(x)}</li>`).join("")}</ul>`;
}
function renderMarkets(ms){
const names=[["S&P 500","SCBS&P500","ติดตามภาพรวมตลาดสหรัฐฯ"],["MSCI World","SCBWORLD","กระจายความเสี่ยงหลายประเทศ"],["China Tech","SCBCTECH","ติดตาม AI และเทคโนโลยีจีน"],["Gold","SCBGOLD","ติดตามดอลลาร์และดอกเบี้ย"]];
const m=Object.fromEntries(ms.map(x=>[x.name,x]));document.getElementById("markets").innerHTML=names.map(x=>{const a=m[x[0]]||{};return `<article class="market-card"><div class="fund">${x[0]}</div><h3>${x[1]}</h3><div class="state">${esc(a.state||"รออัปเดต")}</div><p>${esc(a.summary||x[2])}</p><div class="note"><b>มุมมอง:</b> ${esc(a.note||x[2])}</div></article>`}).join("");
}
