import os
import json
from datetime import datetime

# 파일 위치
IN_DIR = "toss/merged"
OUT_DIR = "toss/vectorized"
os.makedirs(OUT_DIR, exist_ok=True)

CATEGORY_MAP = {
    'business-registration': ('business_planning', '창업 전 체크리스트', 'e-commerce'),
    'building-a-website':    ('business_planning', '쇼핑몰 제작 팁', 'e-commerce'),
    'operational-tips':      ('productivity', '운영팁', 'e-commerce'),
    'hr':                    ('management', '세금, 인사, 노무', 'e-commerce'),
    'marketing':             ('marketing', '마케팅', 'e-commerce'),
    'report':                ('case', '리포트', 'e-commerce'),
}
SOURCE = "enterprise"
LAST_UPDATED = datetime.now().strftime("%Y-%m-%d")  # 필요시 개별 날짜 지정

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_chunks(chunks, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

def chunk_text(text, max_length=600):
    # 문단 기준 또는 600자 단위 분할
    paras = [p.strip() for p in text.split('\n') if p.strip()]
    chunks = []
    temp = ""
    for p in paras:
        if len(temp) + len(p) > max_length and temp:
            chunks.append(temp.strip())
            temp = p
        else:
            temp += ("\n" if temp else "") + p
    if temp:
        chunks.append(temp.strip())
    return chunks

def docid_from_url(url):
    if not url:
        return "unknown"
    url = url.rstrip('/')
    return url.split('/')[-1]

def convert_file(in_path, out_path, category, topic, persona):
    data = load_json(in_path)
    chunks_list = []
    for doc in data:
        url = doc.get("url", "")
        doc_id = docid_from_url(url)
        content = doc.get("content", "")
        content_chunks = chunk_text(content)
        for idx, chunk in enumerate(content_chunks):
            chunk_meta = {
                "doc_id": doc_id,
                "chunk_id": idx,
                "persona": persona,
                "category": category,
                "topic": topic,
                "source": SOURCE,
                "last_updated": LAST_UPDATED,
                "content": chunk
            }
            chunks_list.append(chunk_meta)
    save_chunks(chunks_list, out_path)

# 자동 변환 실행
for file in os.listdir(IN_DIR):
    if not file.endswith('_merged.json'):
        continue
    name = file.replace('_merged.json', '')
    if name not in CATEGORY_MAP:
        print(f"경고: 카테고리 매핑 안됨: {file}")
        continue
    category, topic, persona = CATEGORY_MAP[name]
    in_file = os.path.join(IN_DIR, file)
    out_file = os.path.join(OUT_DIR, f"{name}_vector.json")
    convert_file(in_file, out_file, category, topic, persona)
    print(f"✔ {file} → {out_file}")
