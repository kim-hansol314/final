import requests
from bs4 import BeautifulSoup, Tag
import os
import re
from PIL import Image, ImageOps
import pytesseract
from io import BytesIO
import json

pytesseract.pytesseract.tesseract_cmd = r"D:\tesseract-ocr\tesseract.exe"

URL = "https://jiles.or.kr/communication/management/callingmanual.htm"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
SAVE_DIR = "jiles_ocr"

def clean_filename(s):
    return re.sub(r'[^A-Za-z0-9가-힣_.-]', '_', s)

def get_soup(url):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def preprocess_image(img):
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    return img

def ocr_image_from_url(img_url, slug=None):
    try:
        resp = requests.get(img_url, headers=HEADERS, timeout=10)
        if resp.status_code != 200 or not resp.headers.get("Content-Type", "").startswith("image"):
            print(f"OCR 실패(이미지가 아님): {img_url}")
            return ""
        img = Image.open(BytesIO(resp.content))
        img = preprocess_image(img)
        if slug:
            os.makedirs(os.path.join(SAVE_DIR, "debug_img"), exist_ok=True)
            img_path = os.path.join(SAVE_DIR, "debug_img", f"{clean_filename(slug)}.png")
            img.save(img_path)
        text = pytesseract.image_to_string(img, lang="kor+eng")
        return text.strip()
    except Exception as e:
        print(f"OCR 실패: {img_url}, {e}")
        return ""

def extract_content_order(soup):
    content_list = []
    main = soup.body
    seen_texts = set()
    for elem in main.descendants:
        if isinstance(elem, Tag):
            # 이미지
            if elem.name == 'img':
                src = elem.get("src", "")
                if src and not src.startswith("data:"):
                    if src.startswith("//"):
                        img_url = "https:" + src
                    elif src.startswith("/"):
                        img_url = "https://jiles.or.kr" + src
                    elif src.startswith("http"):
                        img_url = src
                    else:
                        img_url = "https://jiles.or.kr/" + src
                    ocr_text = ocr_image_from_url(img_url, slug=img_url.split("/")[-1])
                    content_list.append({"type": "image", "img_url": img_url, "ocr_text": ocr_text})
            # leaf 텍스트 블록
            elif elem.name in ['p', 'span', 'li', 'div', 'h1', 'h2', 'h3', 'h4']:
                if not any(isinstance(child, Tag) for child in elem.children):
                    text = elem.get_text(strip=True)
                    if text and text not in seen_texts:
                        content_list.append({"type": "text", "data": text})
                        seen_texts.add(text)
    return content_list

def main():
    os.makedirs(SAVE_DIR, exist_ok=True)
    soup = get_soup(URL)
    title = soup.title.get_text(strip=True) if soup.title else ""
    content_ordered = extract_content_order(soup)

    result = {
        "url": URL,
        "title": title,
        "content_ordered": content_ordered
    }

    with open(os.path.join(SAVE_DIR, "callingmanual_ocr.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("크롤링 및 OCR 완료!")

if __name__ == "__main__":
    main()
