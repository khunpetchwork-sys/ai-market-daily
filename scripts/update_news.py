```python
import os
import json
import re
import html
import time
import urllib.error
from datetime import datetime, timezone
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


FEEDS = [
    ("OpenAI", "https://openai.com/news/rss.xml"),
    ("Google AI", "https://blog.google/technology/ai/rss/"),
    ("MIT Technology Review", "https://www.technologyreview.com/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/")
]


def clean(s):
    s = re.sub(r"<[^>]+>", " ", html.unescape(s or ""))
    return re.sub(r"\s+", " ", s).strip()


def get(element, names):
    for name in names:
        x = element.find(name)
        if x is not None and x.text:
            return clean(x.text)
    return ""


# ============================================================
# 1. ดึงข่าวจาก RSS
# ============================================================

items = []

for source, url in FEEDS:
    try:
        request = Request(
            url,
            headers={
                "User-Agent": "AI-Market-Daily/1.0"
            }
        )

        raw = urlopen(request, timeout=20).read()
        root = ET.fromstring(raw)

        for item in root.findall(".//item")[:8]:

            title = get(item, ["title"])

            if title:
                items.append({
                    "source": source,
                    "title": title,
                    "url": get(item, ["link"]),
                    "description": get(
                        item,
                        ["description", "summary"]
                    )[:1200],
                    "published": get(
                        item,
                        ["pubDate", "published", "updated"]
                    )
                })

    except Exception as e:
        print("RSS error:", source, e)


if not items:
    raise SystemExit("No RSS items found")


# ============================================================
# 2. Gemini API Key
# ============================================================

api = os.environ.get("GEMINI_API_KEY")

if not api:
    raise SystemExit("Missing GEMINI_API_KEY")


# ============================================================
# 3. Prompt สำหรับ Gemini
# ============================================================

prompt = '''คุณเป็นบรรณาธิการข่าว AI และนักวิเคราะห์การลงทุน

หน้าที่ของคุณคืออ่านข่าว RSS ทั้งหมดด้านล่าง แล้วเลือกข่าว AI ที่สำคัญที่สุดไม่เกิน 8 ข่าว

เป้าหมายของเว็บ:

เว็บนี้ไม่ได้มีไว้ให้ผู้อ่านไปอ่านต้นฉบับ
แต่ต้องการสรุปข่าวให้เข้าใจง่าย

ผู้อ่านควรสามารถเข้าใจว่าเกิดอะไรขึ้นจากบทความของเว็บเราเอง
โดยไม่จำเป็นต้องเปิดข่าวต้นฉบับ

สำหรับข่าวแต่ละข่าว ให้สร้างข้อมูลดังนี้:

1. short_summary

ใช้แสดงบนหน้าแรก

- 2-3 ประโยค
- สั้น กระชับ
- บอกว่าเกิดอะไรขึ้น
- บอกประเด็นสำคัญ
- อ่านแล้วต้องเข้าใจข่าวคร่าว ๆ
- ห้ามเขียนกว้าง ๆ
- ห้ามสั้นจนไม่รู้ว่าเกิดอะไรขึ้น

2. full_summary

ใช้ในหน้ารายละเอียดข่าว

- ประมาณ 400-700 คำ หรือตามความซับซ้อนของข่าว
- ภาษาไทยอ่านง่าย
- เขียนเหมือนบทความสรุปข่าวของเว็บเราเอง
- ไม่ต้องแปลคำต่อคำ
- อธิบายว่าเกิดอะไรขึ้น
- ใครเกี่ยวข้อง
- มีการประกาศหรือเปลี่ยนแปลงอะไร
- ทำไมเรื่องนี้สำคัญ
- ผลกระทบที่อาจเกิดขึ้น
- รวมรายละเอียดสำคัญที่มีอยู่ใน RSS
- ห้ามเติมข้อเท็จจริงที่ไม่มีใน RSS
- แบ่งเป็นย่อหน้าสั้น ๆ
- ห้ามใช้ Markdown

3. why_it_matters

อธิบายว่าข่าวนี้สำคัญอย่างไร

ประมาณ 2-4 ประโยค

4. impact

วิเคราะห์ผลกระทบหรือแนวโน้ม โดยแบ่งเป็น:

AI industry
Business
Investment

ห้ามสร้างตัวเลข ราคา หรือผลตอบแทนที่ไม่มีอยู่ในข่าว

5. markets

วิเคราะห์จากข่าวทั้งหมดว่าแนวโน้มส่งผลต่อสินทรัพย์ที่ติดตามอย่างไร

S&P 500
ใช้ชื่อระบบว่า SCBS&P500

เน้น:
- บริษัทสหรัฐฯ
- บริษัทเทคโนโลยีขนาดใหญ่
- การลงทุน AI
- ความเชื่อมั่นตลาด

MSCI World
ใช้ชื่อระบบว่า SCBWORLD

เน้น:
- บริษัททั่วโลก
- เศรษฐกิจโลก
- บริษัทเทคโนโลยีทั่วโลก

China Tech
ใช้ชื่อระบบว่า SCBCTECH

เน้น:
- บริษัทเทคโนโลยีจีน
- การแข่งขัน AI
- ความสามารถในการแข่งขันด้านเทคโนโลยี

Gold
ใช้ชื่อระบบว่า SCBGOLD

วิเคราะห์ผลกระทบทางอ้อม เช่น:
- ความเสี่ยงตลาด
- เศรษฐกิจ
- เงินเฟ้อ
- ความไม่แน่นอน
- ความต้องการสินทรัพย์ปลอดภัย

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

หากข้อมูลข่าวไม่เพียงพอ ให้ใช้ "เป็นกลาง"
และอธิบายว่าข้อมูลยังไม่เพียงพอ

6. weekly

สรุปภาพรวมของข่าวทั้งหมด

ต้องมี:
- แนวโน้ม AI ในช่วงนี้
- ประเด็นที่ควรจับตา
- ความเสี่ยงสำคัญ

ต้องตอบ JSON เท่านั้น

ห้ามใช้ Markdown

ห้ามใส่ข้อความนอก JSON

โครงสร้าง JSON:

{
 "quick_summary": [
  {
   "title": "",
   "text": ""
  }
 ],
 "news": [
  {
   "title": "",
   "short_summary": "",
   "full_summary": "",
   "why_it_matters": "",
   "impact": {
    "AI industry": "",
    "Business": "",
    "Investment": ""
   },
   "category": "",
   "source": "",
   "url": "",
   "time": ""
  }
 ],
 "markets": [
  {
   "name": "S&P 500",
   "state": "",
   "summary": "",
   "note": ""
  },
  {
   "name": "MSCI World",
   "state": "",
   "summary": "",
   "note": ""
  },
  {
   "name": "China Tech",
   "state": "",
   "summary": "",
   "note": ""
  },
  {
   "name": "Gold",
   "state": "",
   "summary": "",
   "note": ""
  }
 ],
 "weekly": {
  "title": "",
  "summary": "",
  "points": [
   "",
   "",
   ""
  ]
 }
}

ข่าว RSS:

''' + json.dumps(items, ensure_ascii=False)


# ============================================================
# 4. Gemini API
# ============================================================

endpoint = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.6-flash:generateContent"
)


payload = json.dumps(
    {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "response_mime_type": "application/json"
        }
    },
    ensure_ascii=False
).encode("utf-8")


# ============================================================
# 5. AUTO RETRY
#
# 503 = Gemini โหลดสูงชั่วคราว
# 429 = จำกัดการใช้งานชั่วคราว
#
# จะลองทั้งหมด 4 ครั้ง
# ============================================================

MAX_RETRIES = 4

RETRY_DELAYS = [
    10,
    30,
    60
]

raw = None

for attempt in range(1, MAX_RETRIES + 1):

    print(
        f"Gemini request attempt "
        f"{attempt}/{MAX_RETRIES}"
    )

    try:

        request = Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api
            }
        )

        raw = urlopen(
            request,
            timeout=90
        ).read()

        print("Gemini API success")

        break

    except urllib.error.HTTPError as e:

        detail = e.read().decode(
            "utf-8",
            errors="replace"
        )

        # Retry เฉพาะปัญหาชั่วคราว
        if e.code in (429, 503):

            if attempt < MAX_RETRIES:

                delay = RETRY_DELAYS[attempt - 1]

                print(
                    f"Gemini API HTTP {e.code}. "
                    f"Retrying in {delay} seconds..."
                )

                time.sleep(delay)

                continue

        # API key ผิด
        # permission ผิด
        # endpoint ผิด
        # หรือ error ที่ไม่ควร retry
        raise SystemExit(
            f"Gemini API HTTP {e.code}: {detail}"
        )

    except Exception as e:

        if attempt < MAX_RETRIES:

            delay = RETRY_DELAYS[attempt - 1]

            print(
                f"Network error: {e}. "
                f"Retrying in {delay} seconds..."
            )

            time.sleep(delay)

            continue

        raise SystemExit(
            "Gemini request failed after "
            f"{MAX_RETRIES} attempts: {e}"
        )


if raw is None:
    raise SystemExit(
        "Gemini API failed after all retries"
    )


# ============================================================
# 6. อ่านผลลัพธ์จาก Gemini
# ============================================================

try:

    response = json.loads(raw)

    text = (
        response["candidates"][0]
        ["content"]["parts"][0]["text"]
    )

    out = json.loads(text)

except Exception as e:

    print("Gemini response:", raw.decode(
        "utf-8",
        errors="replace"
    ))

    raise SystemExit(
        f"Invalid Gemini JSON response: {e}"
    )


# ============================================================
# 7. เพิ่มข้อมูลระบบ
# ============================================================

out["updated_at"] = datetime.now(
    timezone.utc
).isoformat()

out["source_count"] = len(items)


# ============================================================
# 8. บันทึกข่าว
# ============================================================

os.makedirs(
    "data",
    exist_ok=True
)

with open(
    "data/news.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        out,
        f,
        ensure_ascii=False,
        indent=2
    )


print(
    "Updated",
    len(out.get("news", [])),
    "news"
)

print(
    "RSS sources:",
    len(items)
)
```
