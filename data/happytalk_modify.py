import json
from datetime import datetime

# 파일 경로
IN_FILE = "happytalk_cs.json"
OUT_FILE = "happytalk_cs_vector.json"

CATEGORY = "customer_management"
TOPIC = "고객상담 매뉴얼"
PERSONA = "common"
SOURCE = "enterprise"
LAST_UPDATED = datetime.now().strftime("%Y-%m-%d")

def docid_from_url(url):
    url = url.rstrip('/')
    return url.split('/')[-1]

with open(IN_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

doc_id = docid_from_url(data["url"])
content_ordered = data.get("content_ordered", [])

chunks = []
for idx, block in enumerate(content_ordered):
    if block.get("type") == "text":
        chunk = {
            "doc_id": doc_id,
            "chunk_id": idx,
            "persona": PERSONA,
            "category": CATEGORY,
            "topic": TOPIC,
            "source": SOURCE,
            "last_updated": LAST_UPDATED,
            "content": block["data"]
        }
        chunks.append(chunk)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"변환 완료: {OUT_FILE} ({len(chunks)}개 chunk)")
