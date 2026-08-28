const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt=d=>new Date(d).toLocaleDateString("th-TH",{weekday:"long",year:"numeric",month:"long",day:"numeric"});

document.getElementById("today").textContent=fmt(new Date());

fetch("data/news.json?ts="+Date.now())
.then(r=>{
 if(!r.ok) throw Error();
 return r.json();
})
.then(render)
.catch(()=>{
 document.getElementById("summary").innerHTML='<div class="summary-card"><div class="summary-icon">🤖</div><h3>ระบบพร้อมแล้ว</h3><p>เมื่อ Auto News ทำงาน ข่าวจริงจะถูกใส่เข้ามาที่นี่</p></div>';
 document.getElementById("news").innerHTML='<div class="loading">ยังไม่มีข่าว — รัน GitHub Action ก่อน</div>';
 renderMarkets([]);
});

function render(d){

 const n=d.news||[];

 document.getElementById("newsCount").textContent=n.length+" ข่าว";

 // สรุปวันนี้
 document.getElementById("summary").innerHTML=
 (d.quick_summary||[]).map((x,i)=>`
  <article class="summary-card">
   <div class="summary-icon">${i?"📈":"🤖"}</div>
   <h3>${esc(x.title)}</h3>
   <p>${esc(x.text)}</p>
  </article>
 `).join("");

 // ข่าว
 document.getElementById("news").innerHTML=
 n.map((x,i)=>`
  <article class="news-card" data-index="${i}" role="button" tabindex="0">

   <div class="meta">
    <span class="tag">${esc(x.category)}</span>
    <span>${esc(x.source)}${x.time?` · ${esc(x.time)}`:""}</span>
   </div>

   <h3>${esc(x.title)}</h3>

   <p>${esc(x.short_summary||x.summary||"")}</p>

   <div class="why">
    <strong>💡 ทำไมต้องสนใจ</strong>
    <span>${esc(x.why_it_matters||x.why||"")}</span>
   </div>

   <div class="read-more">
    อ่านสรุปฉบับเต็ม →
   </div>

  </article>
 `).join("")
 || '<div class="loading">วันนี้ยังไม่มีข่าวที่ผ่านการคัดเลือก</div>';

 // คลิกข่าว
 document.querySelectorAll(".news-card[data-index]").forEach(card=>{

  const open=()=>{
   showArticle(n[Number(card.dataset.index)]);
  };

  card.addEventListener("click",open);

  card.addEventListener("keydown",e=>{
   if(e.key==="Enter"||e.key===" "){
    e.preventDefault();
    open();
   }
  });

 });

 renderMarkets(d.markets||[]);

 // Weekly
 const w=d.weekly||{};

 document.getElementById("weekly").innerHTML=`
  <h3>${esc(w.title||"สรุปประจำสัปดาห์")}</h3>
  <p>${esc(w.summary||"ระบบจะสร้าง Weekly Brief อัตโนมัติ")}</p>
  <ul>
   ${(w.points||[]).map(x=>`<li>${esc(x)}</li>`).join("")}
  </ul>
 `;
}


// =========================
// หน้าสรุปข่าวฉบับเต็ม
// =========================

function showArticle(x){

 if(!x)return;

 const impact=x.impact||{};

 const article=document.createElement("section");

 article.id="articleView";
 article.className="article-view";

 article.innerHTML=`

  <div class="article-inner">

   <button class="back-button" type="button">
    ← กลับไปข่าวทั้งหมด
   </button>

   <div class="meta">
    <span class="tag">${esc(x.category)}</span>
    <span>${esc(x.source)}${x.time?` · ${esc(x.time)}`:""}</span>
   </div>

   <h1>${esc(x.title)}</h1>

   <div class="article-lead">
    ${esc(x.short_summary||"")}
   </div>


   <div class="article-section">

    <h2>สรุปข่าว</h2>

    ${paragraphs(
     x.full_summary||
     x.summary||
     ""
    )}

   </div>


   <div class="article-section">

    <h2>ทำไมเรื่องนี้สำคัญ?</h2>

    ${paragraphs(
     x.why_it_matters||
     x.why||
     ""
    )}

   </div>


   <div class="article-section">

    <h2>ผลกระทบที่ควรจับตา</h2>

    <div class="impact-grid">

     <div>
      <b>🤖 AI</b>
      <p>${esc(
       impact["AI industry"]||
       impact.ai||
       "ยังไม่มีข้อมูลเพิ่มเติม"
      )}</p>
     </div>

     <div>
      <b>💼 ธุรกิจ</b>
      <p>${esc(
       impact.Business||
       impact.business||
       "ยังไม่มีข้อมูลเพิ่มเติม"
      )}</p>
     </div>

     <div>
      <b>📈 การลงทุน</b>
      <p>${esc(
       impact.Investment||
       impact.investment||
       "ยังไม่มีข้อมูลเพิ่มเติม"
      )}</p>
     </div>

    </div>

   </div>


   ${
    x.url
    ?
    `
    <div class="article-source">

     <span>
      สรุปโดย AI & Market Daily
      จากข้อมูลข่าวต้นฉบับ
     </span>

     <a
      class="source"
      href="${esc(x.url)}"
      target="_blank"
      rel="noopener noreferrer"
     >
      อ่านแหล่งข่าวต้นฉบับ →
     </a>

    </div>
    `
    :
    ""
   }

  </div>
 `;


 document.body.appendChild(article);

 document.body.classList.add("article-open");

 article
 .querySelector(".back-button")
 .addEventListener("click",closeArticle);

 window.scrollTo({
  top:0,
  behavior:"instant"
 });
}


// ปิดหน้าข่าว
function closeArticle(){

 const article=document.getElementById("articleView");

 if(article){
  article.remove();
 }

 document.body.classList.remove("article-open");

}


// แยกย่อหน้า
function paragraphs(text){

 return String(text||"")
 .split(/\n\s*\n|\n/)
 .map(s=>s.trim())
 .filter(Boolean)
 .map(s=>`<p>${esc(s)}</p>`)
 .join("");

}


// =========================
// ตลาดที่ติดตาม
// =========================

function renderMarkets(ms){

 const names=[
  ["S&P 500","SCBS&P500","ติดตามภาพรวมตลาดสหรัฐฯ"],
  ["MSCI World","SCBWORLD","กระจายความเสี่ยงหลายประเทศ"],
  ["China Tech","SCBCTECH","ติดตาม AI และเทคโนโลยีจีน"],
  ["Gold","SCBGOLD","ติดตามปัจจัยเศรษฐกิจและสินทรัพย์ปลอดภัย"]
 ];

 const m=Object.fromEntries(
  ms.map(x=>[x.name,x])
 );

 document.getElementById("markets").innerHTML=

 names.map(x=>{

  const a=m[x[0]]||{};

  return `
   <article class="market-card">

    <div class="fund">
     ${x[0]}
    </div>

    <h3>
     ${x[1]}
    </h3>

    <div class="state">
     ${esc(a.state||"รออัปเดต")}
    </div>

    <p>
     ${esc(a.summary||x[2])}
    </p>

    <div class="note">
     <b>มุมมอง:</b>
     ${esc(a.note||x[2])}
    </div>

   </article>
  `;

 }).join("");

}
