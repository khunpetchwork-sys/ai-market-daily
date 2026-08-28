import os,json,re,html
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
     "description":get(it,["description","summary"])[:800],
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

หน้าที่ของคุณคืออ่านข่าว RSS ทั้งหมดด้านล่าง แล้ว:
1. เลือกข่าว AI ที่สำคัญที่สุดไม่เกิน 8 ข่าว
2. สรุปข่าวเป็นภาษาไทยแบบกระชับ เข้าใจง่าย
3. วิเคราะห์ว่า "ข่าวและแนวโน้ม" เหล่านี้ส่งผลอย่างไรต่อสินทรัพย์ที่ติดตาม 4 ตัว
4. ห้ามแต่งข้อเท็จจริง ตัวเลข ราคา หรือข้อมูลที่ไม่มีอยู่ในข่าว

สำคัญ:
ส่วน markets ไม่ต้องแสดงราคาปัจจุบัน และไม่ต้องบอกว่ามีหรือไม่มีข้อมูลดัชนี
เราต้องการ "การวิเคราะห์แนวโน้มจากข่าว" เท่านั้น

สินทรัพย์ที่ต้องวิเคราะห์:

1. S&P 500
ใช้ชื่อในระบบว่า SCBS&P500
วิเคราะห์ผลต่อหุ้นสหรัฐฯ โดยเฉพาะบริษัทเทคโนโลยีขนาดใหญ่ การลงทุน AI ผลประกอบการ และความเชื่อมั่นของตลาด

2. MSCI World
ใช้ชื่อในระบบว่า SCBWORLD
วิเคราะห์ผลต่อหุ้นทั่วโลก เศรษฐกิจโลก บริษัทเทคโนโลยี และการกระจายการลงทุน

3. China Tech
ใช้ชื่อในระบบว่า SCBCTECH
วิเคราะห์ผลต่อหุ้นเทคโนโลยีจีน การแข่งขันด้าน AI บริษัทจีน การพัฒนาเทคโนโลยี และความสามารถในการแข่งขันกับสหรัฐฯ

4. Gold
ใช้ชื่อในระบบว่า SCBGOLD
วิเคราะห์ผลกระทบทางอ้อมจากข่าว เช่น ความเสี่ยงของตลาด เศรษฐกิจ เงินเฟ้อ ความไม่แน่นอน และความต้องการสินทรัพย์ปลอดภัย

สำหรับแต่ละสินทรัพย์:

state:
ต้องเลือกเพียงหนึ่งค่า:
"บวก"
"ลบ"
"เป็นกลาง"

summary:
อธิบายแนวโน้มจากข่าวที่มี 1-2 ประโยค

note:
อธิบายเหตุผลสำคัญและความเสี่ยง 1-2 ประโยค

ห้ามใช้:
"N/A"
"ไม่มีข้อมูลดัชนี"
"ไม่มีข้อมูลราคา"

หากข่าวไม่ได้เกี่ยวข้องกับสินทรัพย์นั้นโดยตรง ให้ใช้ "เป็นกลาง" และอธิบายว่าเป็นผลกระทบทางอ้อมหรือข่าวยังไม่มีปัจจัยเพียงพอที่จะชี้ทิศทาง

อย่าคาดเดาราคาหรือผลตอบแทนในอนาคต
อย่าบอกว่าราคาจะขึ้นหรือลงเป็นจำนวนเท่าไร
ให้วิเคราะห์เฉพาะ "แนวโน้ม" และ "ปัจจัยที่อาจส่งผล"

สำหรับข่าวแต่ละข่าว:
title = ชื่อข่าว
summary = สรุปว่าเกิดอะไรขึ้น
why = ทำไมข่าวนี้สำคัญ
category = หมวดข่าว
source = แหล่งข่าว
url = URL ต้นฉบับ
time = เวลาของข่าวถ้ามี

quick_summary:
เลือกประเด็นสำคัญที่สุด 2-3 เรื่องจากข่าวทั้งหมด

weekly:
สรุปภาพรวมแนวโน้มจากข่าวทั้งหมด
ไม่ต้องสร้างตัวเลขผลตอบแทน
points ให้ใส่ปัจจัยสำคัญ 3 ข้อ

ตอบ JSON เท่านั้น ห้ามใส่ Markdown และต้องใช้โครงสร้างนี้:

{"quick_summary":[{"title":"","text":""}],"news":[{"title":"","summary":"","why":"","category":"","source":"","url":"","time":""}],"markets":[{"name":"S&P 500","state":"","summary":"","note":""},{"name":"MSCI World","state":"","summary":"","note":""},{"name":"China Tech","state":"","summary":"","note":""},{"name":"Gold","state":"","summary":"","note":""}],"weekly":{"title":"","summary":"","points":["","",""]}}

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

except urllib.error.HTTPError as e:
 detail=e.read().decode("utf-8",errors="replace")
 raise SystemExit(f"Gemini API HTTP {e.code}: {detail}")

response=json.loads(raw)

text=response["candidates"][0]["content"]["parts"][0]["text"]

out=json.loads(text)

out["updated_at"]=datetime.now(timezone.utc).isoformat()
out["source_count"]=len(items)

with open("data/news.json","w",encoding="utf-8") as f:
 json.dump(out,f,ensure_ascii=False,indent=2)

print("Updated",len(out.get("news",[])),"news")
