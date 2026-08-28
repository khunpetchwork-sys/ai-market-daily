import os,json,re,html,urllib.parse
from datetime import datetime,timezone
from urllib.request import Request,urlopen
import xml.etree.ElementTree as ET

FEEDS=[
("OpenAI","https://openai.com/news/rss.xml"),
("Google AI","https://blog.google/technology/ai/rss/"),
("MIT Technology Review","https://www.technologyreview.com/feed/"),
("VentureBeat AI","https://venturebeat.com/category/ai/feed/")
]
def clean(s):
 s=re.sub(r"<[^>]+>"," ",html.unescape(s or ""));return re.sub(r"\s+"," ",s).strip()
def get(e,names):
 for n in names:
  x=e.find(n)
  if x is not None and x.text:return clean(x.text)
 return ""
items=[]
for source,url in FEEDS:
 try:
  raw=urlopen(Request(url,headers={"User-Agent":"AI-Market-Daily/1.0"}),timeout=20).read()
  root=ET.fromstring(raw)
  for it in root.findall(".//item")[:8]:
   title=get(it,["title"])
   if title:items.append({"source":source,"title":title,"url":get(it,["link"]),"description":get(it,["description","summary"])[:800],"published":get(it,["pubDate","published","updated"])})
 except Exception as e:print("RSS error",source,e)
if not items:raise SystemExit("No RSS items found")
api=os.environ.get("GEMINI_API_KEY")
if not api:raise SystemExit("Missing GEMINI_API_KEY")
prompt='''คุณเป็นบรรณาธิการเว็บข่าว AI ภาษาไทย จากข่าว RSS ให้เลือกข่าว AI สำคัญที่สุดไม่เกิน 8 ข่าว
สรุปให้คนทั่วไปเข้าใจง่าย ห้ามแต่งข้อมูล
ตอบ JSON เท่านั้น:
{"quick_summary":[{"title":"","text":""}],"news":[{"title":"","summary":"","why":"","category":"","source":"","url":"","time":""}],"markets":[{"name":"S&P 500","state":"","summary":"","note":""},{"name":"MSCI World","state":"","summary":"","note":""},{"name":"China Tech","state":"","summary":"","note":""},{"name":"Gold","state":"","summary":"","note":""}],"weekly":{"title":"","summary":"","points":["","",""]}}
ข่าว:
'''+json.dumps(items,ensure_ascii=False)
endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key="+urllib.parse.quote(api)
payload=json.dumps({"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.2,"responseMimeType":"application/json"}}).encode()
raw=urlopen(Request(endpoint,data=payload,headers={"Content-Type":"application/json"}),timeout=90).read()
out=json.loads(json.loads(raw)["candidates"][0]["content"]["parts"][0]["text"])
out["updated_at"]=datetime.now(timezone.utc).isoformat();out["source_count"]=len(items)
with open("data/news.json","w",encoding="utf-8") as f:json.dump(out,f,ensure_ascii=False,indent=2)
print("Updated",len(out.get("news",[])),"news")
