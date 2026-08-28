# AI & Market Daily — Auto News

ระบบเว็บข่าว AI + ตลาดที่อัปเดตอัตโนมัติด้วย GitHub Actions

## ติดตั้ง
1. อัปโหลดไฟล์ทั้งหมดในชุดนี้เข้า repo `ai-market-daily`
2. GitHub → Settings → Secrets and variables → Actions
3. สร้าง Secret ชื่อ `GEMINI_API_KEY`
4. ไป Actions → `Update AI & Market News` → Run workflow เพื่อทดสอบ

ทุกวัน GitHub Actions จะดึง RSS → ส่งให้ Gemini คัดและสรุป → เขียน `data/news.json` → commit กลับเข้า repo

หมายเหตุ: ตลาดในเวอร์ชันนี้เป็นสรุปข่าวเชิงบริบท ยังไม่มีราคากองทุน/ดัชนีแบบเรียลไทม์
