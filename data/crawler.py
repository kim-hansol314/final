import requests
from bs4 import BeautifulSoup
import time
import json
import os

BASE_URL = "https://www.tosspayments.com"
CATEGORY_BASE_LIST = [
    "https://www.tosspayments.com/blog/business-registration",
    "https://www.tosspayments.com/blog/building-a-website",
    "https://www.tosspayments.com/blog/operational-tips",
    "https://www.tosspayments.com/blog/hr",
    "https://www.tosspayments.com/blog/marketing",
    "https://www.tosspayments.com/blog/report",
]
N_PAGES = 8 

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def get_soup(url):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def extract_article_links(soup):
    links = []
    for a in soup.select("a[href^='/blog/articles/']"):
        url = BASE_URL + a["href"].split("?")[0]
        links.append(url)
    return list(set(links))

def extract_blog_content(soup):
    article = soup.select_one("main article")
    if not article:
        article = soup.select_one("main")
    if not article:
        return {"title": "", "content": ""}
    # 다양한 패턴으로 title 탐색
    title_tag = (
        article.select_one("h1")
        or article.select_one("h1[class^=css-]")
        or article.select_one("[class*=title]")
        or soup.select_one("main h1")
        or soup.select_one("h1")
    )
    title = title_tag.get_text(strip=True) if title_tag else ""
    paragraphs = article.select(".css-1ohnli2, p")
    content_text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
    return {
        "title": title,
        "content": content_text
    }

def slug_from_url(url):
    return url.rstrip("/").split("/")[-1]

def save_json(data, url, folder):
    base_folder = os.path.join("toss", folder)
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
            data = extract_blog_content(article_soup)
            save_json(data, link, folder)
            visited.add(link)
            time.sleep(0.5)
        except Exception as e:
            print(f"  !! 아티클 오류 {link}: {e}")

if __name__ == "__main__":
    for category_base in CATEGORY_BASE_LIST:
        crawl_category(category_base)
