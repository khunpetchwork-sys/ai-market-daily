```text
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


items = []

for source, url in FEEDS:
    try:
        request = Request(
            url,
            headers={
                "User-Agent": "AI-Market-Daily/1.0"
            }
        )

        raw = urlopen(
            request,
            timeout=20
        ).read()

        root = ET.fromstring(raw)

        for item in root.findall(".//item")[:8]:

            title = get(
                item,
                ["title"]
            )

            if title:

                items.append({
                    "source": source,
                    "title": title,
                    "url": get(
                        item,
                        ["link"]
                    ),
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

        print(
            "RSS error:",
            source,
            e
        )


if not items:
    raise SystemExit(
        "No RSS items found"
    )


api = os.environ.get(
    "GEMINI_API_KEY"
)

if not api:
    raise SystemExit(
        "Missing GEMINI_API_KEY"
    )


prompt = '''คุณเป็นบรรณาธิการข่าว AI และนักวิเคราะห์การลงทุน

อ่านข่าว RSS ทั้งหมดด้านล่าง แล้วเลือกข่าว AI ที่สำคัญที่สุดไม่เกิน 8 ข่าว

เป้าหมายของเว็บคือสรุปข่าวให้คนทั่วไปเข้าใจง่าย
ผู้อ่านไม่จำเป็นต้องเปิดต้นฉบับ

สำหรับข่าวแต่ละข่าว:

short_summary:
สรุป 2-3 ประโยคสำหรับหน้าแรก
ต้องบอกว่าเกิดอะไรขึ้นและประเด็นสำคัญ

full_summary:
สรุปประมาณ 400-700 คำ หรือตามความซับซ้อน
อธิบายว่าเกิดอะไรขึ้น ใครเกี่ยวข้อง
อะไรเปลี่ยนแปลง ทำไมสำคัญ และผลกระทบ
เขียนภาษาไทยอ่านง่าย
แบ่งเป็นย่อหน้าสั้น ๆ
ห้ามแปลแบบคำต่อคำ
ห้ามเติมข้อเท็จจริงที่ไม่มีใน RSS

why_it_matters:
2-4 ประโยค อธิบายว่าทำไมข่าวนี้สำคัญ

impact:
แยกเป็น
AI industry
Business
Investment

ห้ามสร้างตัวเลข ราคา หรือผลตอบแทนที่ไม่มีในข่าว

markets:

S&P 500
ใช้ชื่อระบบ SCBS&P500
วิเคราะห์บริษัทสหรัฐฯ เทคโนโลยีขนาดใหญ่ การลงทุน AI และความเชื่อมั่นตลาด

MSCI World
ใช้ชื่อระบบ SCBWORLD
วิเคราะห์บริษัททั่วโลก เศรษฐกิจโลก และเทคโนโลยีทั่วโลก

China Tech
ใช้ชื่อระบบ SCBCTECH
วิเคราะห์บริษัทเทคโนโลยีจีน การแข่งขัน AI และความสามารถในการแข่งขัน

Gold
ใช้ชื่อระบบ SCBGOLD
วิเคราะห์ความเสี่ยงตลาด เศรษฐกิจ เงินเฟ้อ ความไม่แน่นอน และสินทรัพย์ปลอดภัย

state ต้องเป็นเพียง:
บวก
ลบ
เป็นกลาง

ห้ามใช้ N/A
ห้ามสร้างราคาปัจจุบัน
ห้ามสร้างตัวเลขผลตอบแทน
ห้ามบอกว่าราคาจะขึ้นหรือลงเป็นจำนวนเท่าไร

หากข้อมูลไม่เพียงพอ ให้ใช้ เป็นกลาง

weekly:
สรุปแนวโน้ม AI
ประเด็นที่ควรจับตา
ความเสี่ยงสำคัญ

ตอบ JSON เท่านั้น
ห้ามใช้ Markdown
ห้ามมีข้อความนอก JSON

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
''' + json.dumps(
    items,
    ensure_ascii=False
)


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


MAX_RETRIES = 4

RETRY_DELAYS = [
    10,
    30,
    60
]


raw = None


for attempt in range(
    1,
    MAX_RETRIES + 1
):

    print(
        f"Gemini request attempt "
        f"{attempt}/{MAX_RETRIES}"
    )

    try:

        request = Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type":
                    "application/json",
                "x-goog-api-key":
                    api
            }
        )

        raw = urlopen(
            request,
            timeout=90
        ).read()

        print(
            "Gemini API success"
        )

        break


    except urllib.error.HTTPError as e:

        detail = e.read().decode(
            "utf-8",
            errors="replace"
        )

        if e.code in (
            429,
            503
        ):

            if attempt < MAX_RETRIES:

                delay = RETRY_DELAYS[
                    attempt - 1
                ]

                print(
                    f"Gemini API HTTP "
                    f"{e.code}. "
                    f"Retrying in "
                    f"{delay} seconds..."
                )

                time.sleep(
                    delay
                )

                continue

        raise SystemExit(
            f"Gemini API HTTP "
            f"{e.code}: {detail}"
        )


    except Exception as e:

        if attempt < MAX_RETRIES:

            delay = RETRY_DELAYS[
                attempt - 1
            ]

            print(
                f"Network error: "
                f"{e}. "
                f"Retrying in "
                f"{delay} seconds..."
            )

            time.sleep(
                delay
            )

            continue

        raise SystemExit(
            "Gemini request failed "
            f"after {MAX_RETRIES} "
            f"attempts: {e}"
        )


if raw is None:

    raise SystemExit(
        "Gemini API failed after "
        "all retries"
    )


try:

    response = json.loads(
        raw
    )

    text = (
        response[
            "candidates"
        ][0][
            "content"
        ][
            "parts"
        ][0][
            "text"
        ]
    )

    out = json.loads(
        text
    )


except Exception as e:

    print(
        "Gemini response:",
        raw.decode(
            "utf-8",
            errors="replace"
        )
    )

    raise SystemExit(
        f"Invalid Gemini JSON "
        f"response: {e}"
    )


out["updated_at"] = (
    datetime.now(
        timezone.utc
    ).isoformat()
)

out["source_count"] = len(
    items
)


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
    len(
        out.get(
            "news",
            []
        )
    ),
    "news"
)

print(
    "RSS sources:",
    len(items)
)
```
