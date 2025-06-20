import requests
from bs4 import BeautifulSoup, Tag
import time
import json
import os
import re
from PIL import Image, ImageOps
import pytesseract
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r"D:\tesseract-ocr\tesseract.exe"

CATEGORY_BASE_LIST = [
    "https://www.tosspayments.com/blog/business-registration",
    "https://www.tosspayments.com/blog/building-a-website",
    "https://www.tosspayments.com/blog/operational-tips",
    "https://www.tosspayments.com/blog/hr",
    "https://www.tosspayments.com/blog/marketing",
]
N_PAGES = 8  # 필요시 카테고리별 페이지 수 다르게 지정해도 됨

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BASE_URL = "https://www.tosspayments.com"

def get_soup(url):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def preprocess_image(img):
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    return img

def clean_filename(s):
    return re.sub(r'[^A-Za-z0-9가-힣_.-]', '_', s)

def ocr_image_from_url(img_url, slug=None, folder=None):
    try:
        resp = requests.get(img_url, headers=HEADERS, timeout=10)
        img = Image.open(BytesIO(resp.content))
        img = preprocess_image(img)
        if slug and folder:
            safe_slug = clean_filename(slug)
            debug_dir = os.path.join("toss_ocr", folder, "debug_img")
            os.makedirs(debug_dir, exist_ok=True)
            img_path = os.path.join(debug_dir, f"{safe_slug}.png")
            img.save(img_path)
        text = pytesseract.image_to_string(img, lang="kor+eng")
        return text.strip()
    except Exception as e:
        print(f"OCR 실패: {img_url}, {e}")
        return ""

def slug_from_url(url):
    return url.rstrip("/").split("/")[-1]

def extract_article_links(soup):
    links = []
    for a in soup.select("a[href^='/blog/articles/']"):
        url = BASE_URL + a["href"].split("?")[0]
        links.append(url)
    return list(set(links))

def extract_content_order(article, base_url, folder):
    content_list = []
    seen_texts = set()
    if not article:
        return content_list

    for elem in article.descendants:
        if isinstance(elem, Tag):
            if elem.name == 'img':
                src = elem.get("src", "")
                if src and not src.startswith("data:"):
                    if src.startswith("//"):
                        img_url = "https:" + src
                    elif src.startswith("/"):
                        img_url = base_url + src
                    elif src.startswith("http"):
                        img_url = src
                    else:
                        img_url = base_url + "/" + src
                    ocr_text = ocr_image_from_url(img_url, slug=slug_from_url(img_url), folder=folder)
                    content_list.append({"type": "image", "img_url": img_url, "ocr_text": ocr_text})
            elif elem.name in ['p', 'span', 'li', 'h2', 'h3', 'h4']:
                # leaf node: 자식에 태그가 없을 때만
                if not any(isinstance(child, Tag) for child in elem.children):
                    text = elem.get_text(strip=True)
                    if text and text not in seen_texts:
                        content_list.append({"type": "text", "data": text})
                        seen_texts.add(text)
    return content_list

def extract_blog_content(soup, base_url, folder):
    article = soup.select_one("main article")
    if not article:
        article = soup.select_one("main")
    if not article:
        return {"title": "", "content_ordered": []}
    
    # 다양한 패턴으로 title 탐색
    title_tag = (
        article.select_one("h1")
        or article.select_one("h1[class^=css-]")
        or article.select_one("[class*=title]")
        or soup.select_one("main h1")
        or soup.select_one("h1")
    )
    title = title_tag.get_text(strip=True) if title_tag else ""
    
    content_ordered = extract_content_order(article, base_url, folder)
    return {
        "title": title,
        "content_ordered": content_ordered
    }

def save_json(data, url, folder):
    base_folder = os.path.join("toss_ocr", folder)
    os.makedirs(base_folder, exist_ok=True)
    slug = slug_from_url(url)
    filepath = os.path.join(base_folder, f"{slug}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"url": url, **data}, f, ensure_ascii=False, indent=2)
    print(f"저장 완료: {filepath}")

def crawl_category(category_base):
    folder = category_base.split("/")[-1]
    all_links = set()
    for i in range(1, N_PAGES + 1):
        url = f"{category_base}?page={i}"
        print(f"[{folder} {i}페이지] URL: {url}")
        try:
            soup = get_soup(url)
            links = extract_article_links(soup)
            print(f"  - 아티클 {len(links)}개 발견")
            all_links.update(links)
            time.sleep(0.5)
        except Exception as e:
            print(f"  !! 목록 페이지 오류 {url}: {e}")
    print(f"\n[{folder}] 총 아티클 수집: {len(all_links)}개")

    visited = set()
    for link in sorted(all_links):
        if link in visited:
            continue
        try:
            article_soup = get_soup(link)
            data = extract_blog_content(article_soup, BASE_URL, folder)
            save_json(data, link, folder)
            visited.add(link)
            time.sleep(0.5)
        except Exception as e:
            print(f"  !! 아티클 오류 {link}: {e}")

if __name__ == "__main__":
    for category_base in CATEGORY_BASE_LIST:
        crawl_category(category_base)
