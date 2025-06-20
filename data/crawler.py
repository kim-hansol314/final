import requests
from bs4 import BeautifulSoup
import time
import json
import os

BASE_URL = "https://www.tosspayments.com"
CATEGORY_BASE = "https://www.tosspayments.com/blog/report"
FOLDER = CATEGORY_BASE.split("/")[-1]
N_PAGES = 8  # 실제 페이지 수로 맞춰주세요

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
    title = article.select_one("h1")
    paragraphs = article.select(".css-1ohnli2, p")
    content_text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
    return {
        "title": title.get_text(strip=True) if title else "",
        "content": content_text
    }

def slug_from_url(url):
    return url.rstrip("/").split("/")[-1]

def save_json(data, url, folder=FOLDER):
    os.makedirs(folder, exist_ok=True)
    slug = slug_from_url(url)
    filepath = os.path.join(folder, f"{slug}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"url": url, **data}, f, ensure_ascii=False, indent=2)
    print(f"저장 완료: {filepath}")

def crawl_all_article_pages():
    all_links = set()
    for i in range(1, N_PAGES + 1):
        url = f"{CATEGORY_BASE}?page={i}"
        print(f"[{i}페이지] URL: {url}")
        try:
            soup = get_soup(url)
            links = extract_article_links(soup)
            print(f"  - 아티클 {len(links)}개 발견")
            all_links.update(links)
            time.sleep(0.5)
        except Exception as e:
            print(f"  !! 목록 페이지 오류 {url}: {e}")
    print(f"\n총 아티클 수집: {len(all_links)}개")

    visited = set()
    for link in sorted(all_links):
        if link in visited:
            continue
        try:
            article_soup = get_soup(link)
            data = extract_blog_content(article_soup)
            save_json(data, link)
            visited.add(link)
            time.sleep(0.5)
        except Exception as e:
            print(f"  !! 아티클 오류 {link}: {e}")

if __name__ == "__main__":
    crawl_all_article_pages()
