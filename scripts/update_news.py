import os,json,re,html,time
from datetime import datetime,timezone
from urllib.request import Request,urlopen
import urllib.error
import xml.etree.ElementTree as ET

FEEDS=[
("OpenAI","https://openai.com/news/rss.xml"),
("Google AI","https://blog.google/technology/ai/rss/"),
("MIT Technology Review","https://www.technologyreview.com/feed/"),
("VentureBeat AI","https://venturebeat.com/category/ai/feed/")
]

def clean(s):
 s=re.sub(r"<[^>]+>"," ",html.unescape(s or ""))
 return re.sub(r"\s+"," ",s).strip()

def get(e,names):
 for n in names:
  x=e.find(n)
  if x is not None and x.text:
   return clean(x.text)
 return ""

items=[]

for source,url in FEEDS:
 try:
  raw=urlopen(
   Request(url,headers={"User-Agent":"AI-Market-Daily/1.0"}),
   timeout=20
  ).read()

  root=ET.fromstring(raw)

  for it in root.findall(".//item")[:8]:
   title=get(it,["title"])

   if title:
    items.append({
     "source":source,
     "title":title,
     "url":get(it,["link"]),
     "description":get(it,["description","summary"])[:1200],
     "published":get(it,["pubDate","published","updated"])
    })

 except Exception as e:
  print("RSS error",source,e)

if not items:
 raise SystemExit("No RSS items found")

api=os.environ.get("GEMINI_API_KEY")

if not api:
 raise SystemExit("Missing GEMINI_API_KEY")

prompt='''คุณเป็นบรรณาธิการข่าว AI และนักวิเคราะห์การลงทุน

หน้าที่ของคุณคืออ่านข่าว RSS ทั้งหมดด้านล่าง แล้วเลือกข่าว AI ที่สำคัญที่สุดไม่เกิน 8 ข่าว

เป้าหมายของเว็บ:
เว็บนี้ไม่ได้มีไว้ให้ผู้อ่านไปอ่านต้นฉบับ แต่ต้องการ "สรุปข่าวให้เข้าใจง่าย"
ดังนั้นเนื้อหาที่สร้างขึ้นต้องอ่านแล้วเข้าใจว่าเกิดอะไรขึ้น โดยไม่จำเป็นต้องเปิดต้นฉบับ

สำหรับข่าวแต่ละข่าว ให้สร้างสรุป 2 ระดับ:

1. short_summary
ใช้แสดงบนหน้าแรก
- 2-3 ประโยค
- สั้น กระชับ
- บอกว่าเกิดอะไรขึ้น
- บอกประเด็นสำคัญ
- อ่านจบแล้วต้องเข้าใจข่าวคร่าว ๆ
- ห้ามเขียนกว้าง ๆ หรือสั้นจนไม่รู้ว่าเกิดอะไรขึ้น

2. full_summary
ใช้ในหน้ารายละเอียดข่าว
- ประมาณ 400-700 คำ หรือตามความซับซ้อนของข่าว
- เขียนเป็นภาษาไทยที่อ่านง่าย
- อธิบายเรื่องราวให้คนที่ไม่ติดตามข่าว AI เข้าใจ
- อธิบายว่าเกิดอะไรขึ้น
- ใครเกี่ยวข้อง
- สิ่งที่เปลี่ยนแปลงหรือประกาศคืออะไร
- ทำไมเรื่องนี้สำคัญ
- ผลกระทบที่อาจเกิดขึ้น
- หากมีรายละเอียดสำคัญจากข่าว RSS ให้รวมไว้
- ห้ามเติมข้อเท็จจริงที่ไม่มีอยู่ในข้อมูล RSS
- ไม่ต้องแปลข่าวแบบคำต่อคำ
- ให้เรียบเรียงใหม่เหมือนบทความสรุปข่าวของเว็บเราเอง
- แบ่งเป็นย่อหน้าสั้น ๆ เพื่อให้อ่านง่าย

3. why_it_matters
อธิบายสั้น ๆ ว่าข่าวนี้สำคัญอย่างไร ประมาณ 2-4 ประโยค

4. impact
อธิบายผลกระทบหรือแนวโน้มที่อาจเกิดขึ้นจากข่าวนี้ โดยแยก:
- AI industry
- Business
- Investment

ห้ามสร้างตัวเลข ราคา หรือผลตอบแทนที่ไม่มีอยู่ในข่าว

5. markets
วิเคราะห์จากข่าวทั้งหมดว่าแนวโน้มมีผลต่อสินทรัพย์ที่ติดตามอย่างไร

สินทรัพย์:

S&P 500
ใช้ชื่อระบบว่า SCBS&P500
เน้นบริษัทสหรัฐฯ บริษัทเทคโนโลยีขนาดใหญ่ การลงทุน AI และความเชื่อมั่นตลาด

MSCI World
ใช้ชื่อระบบว่า SCBWORLD
เน้นบริษัททั่วโลก เศรษฐกิจโลก และบริษัทเทคโนโลยีทั่วโลก

China Tech
ใช้ชื่อระบบว่า SCBCTECH
เน้นบริษัทเทคโนโลยีจีน การแข่งขัน AI และความสามารถในการแข่งขันด้านเทคโนโลยี

Gold
ใช้ชื่อระบบว่า SCBGOLD
วิเคราะห์ผลกระทบทางอ้อม เช่น ความเสี่ยงตลาด เศรษฐกิจ เงินเฟ้อ ความไม่แน่นอน และความต้องการสินทรัพย์ปลอดภัย

state ต้องเป็นเพียง:
"บวก"
"ลบ"
"เป็นกลาง"

summary:
อธิบายแนวโน้ม 1-2 ประโยค

note:
อธิบายเหตุผลและความเสี่ยง 1-2 ประโยค

ห้ามใช้ N/A
ห้ามสร้างราคาปัจจุบัน
ห้ามสร้างตัวเลขผลตอบแทน
ห้ามบอกว่าราคาจะขึ้นหรือลงเป็นจำนวนเท่าไร

หากข่าวไม่เพียงพอ ให้ใช้ "เป็นกลาง" และอธิบายว่าข้อมูลยังไม่เพียงพอ

6. weekly
สรุปภาพรวมของข่าวทั้งหมด
- แนวโน้ม AI ในช่วงนี้
- ประเด็นที่ควรจับตา
- ความเสี่ยงสำคัญ

ต้องตอบ JSON เท่านั้น
ห้ามใช้ Markdown
ห้ามใส่ข้อความนอก JSON

ใช้โครงสร้างนี้:

{
 "quick_summary":[
  {
   "title":"",
   "text":""
  }
 ],
 "news":[
  {
   "title":"",
   "short_summary":"",
   "full_summary":"",
   "why_it_matters":"",
   "impact":{
    "AI industry":"",
    "Business":"",
    "Investment":""
   },
   "category":"",
   "source":"",
   "url":"",
   "time":""
  }
 ],
 "markets":[
  {
   "name":"S&P 500",
   "state":"",
   "summary":"",
   "note":""
  },
  {
   "name":"MSCI World",
   "state":"",
   "summary":"",
   "note":""
  },
  {
   "name":"China Tech",
   "state":"",
   "summary":"",
   "note":""
  },
  {
   "name":"Gold",
   "state":"",
   "summary":"",
   "note":""
  }
 ],
 "weekly":{
  "title":"",
  "summary":"",
  "points":[
   "",
   "",
   ""
  ]
 }
}

ข่าว RSS:
'''+json.dumps(items,ensure_ascii=False)

endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"

payload=json.dumps({
 "contents":[
  {
   "parts":[
    {
     "text":prompt
    }
   ]
  }
 ],
 "generationConfig":{
  "temperature":0.2,
  "response_mime_type":"application/json"
 }
},ensure_ascii=False).encode("utf-8")


# ==========================================
# Gemini API + AUTO RETRY
# ==========================================

MAX_RETRIES=4

# เวลารอก่อนลองใหม่
RETRY_DELAYS=[10,30,60]

for attempt in range(1,MAX_RETRIES+1):

 print(f"Gemini request attempt {attempt}/{MAX_RETRIES}")

 try:

  req=Request(
   endpoint,
   data=payload,
   headers={
    "Content-Type":"application/json",
    "x-goog-api-key":api
   }
  )

  raw=urlopen(req,timeout=90).read()

  # สำเร็จ
  print("Gemini API success")
  break

 except urllib.error.HTTPError as e:

  detail=e.read().decode("utf-8",errors="replace")

  # 503 = Gemini มีโหลดสูงชั่วคราว
  # 429 = rate limit / resource exhausted ชั่วคราว
  if e.code in (503,429) and attempt<MAX_RETRIES:

   delay=RETRY_DELAYS[attempt-1]

   print(
    f"Gemini API HTTP {e.code}. "
    f"Retrying in {delay} seconds..."
   )

   time.sleep(delay)

   continue

  # API key ผิด / permission / endpoint ผิด
  # ไม่ควร retry เพราะ retry ก็ไม่ช่วย
  raise SystemExit(
   f"Gemini API HTTP {e.code}: {detail}"
  )

 except Exception as e:

  # Network error เช่น connection หลุด
  if attempt<MAX_RETRIES:

   delay=RETRY_DELAYS[attempt-1]

   print(
    f"Network error: {e}. "
    f"Retrying in {delay} seconds..."
   )

   time.sleep(delay)

   continue

  raise SystemExit(
   f"Gemini request failed after {MAX_RETRIES} attempts: {e}"
  )


# ==========================================
# อ่านผล Gemini
# ==========================================

response=json.loads(raw)

text=response["candidates"][0]["content"]["parts"][0]["text"]

out=json.loads(text)

out["updated_at"]=datetime.now(timezone.utc).isoformat()
out["source_count"]=len(items)

with open("data/news.json","w",encoding="utf-8") as f:
 json.dump(out,f,ensure_ascii=False,indent=2)

print(
 "Updated",
 len(out.get("news",[])),
 "news"
)
```
