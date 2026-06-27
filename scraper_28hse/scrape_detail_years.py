#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
28HSE 详情页年份补全爬虫 — B方案抽样
处理高频无年份屋苑，爬详情页获取入伙年份
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import csv, requests, re, time, json
from bs4 import BeautifulSoup
from urllib.parse import quote
from collections import Counter
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8",
}
REQUEST_DELAY = 0.5

DATA_DIR = Path(__file__).parent / "data"
LISTINGS_CSV = DATA_DIR / "listings_28hse.csv"
OUTPUT_JSON = DATA_DIR / "estate_years_detail.json"
OUTPUT_LOG = DATA_DIR / "estate_years_detail.log"


def fetch_detail_year(estate_name: str) -> int | None:
    """
    搜索屋苑名，获取第一个在售listing的详情页，提取入伙年份
    """
    try:
        # Step 1: 搜索屋苑
        search_url = f"https://www.28hse.com/buy?searchText={quote(estate_name)}"
        resp = requests.get(search_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        items = soup.select(".item.property_item")
        if not items:
            return None

        # Step 2: 获取第一个listing的详情页URL
        first_item = items[0]
        header = first_item.select_one(".header")
        if not header:
            return None
        a = header.find("a")
        if not a or not a.get("href"):
            return None

        detail_path = a["href"]
        detail_url = detail_path if detail_path.startswith("http") else f"https://www.28hse.com{detail_path}"

        # Step 3: 爬详情页提取年份
        dresp = requests.get(detail_url, headers=HEADERS, timeout=30)
        dresp.raise_for_status()
        dsoup = BeautifulSoup(dresp.text, "html.parser")

        for td in dsoup.find_all("td"):
            txt = td.get_text(strip=True)
            if txt in ["入伙日期", "入伙年份", "落成年份"]:
                parent_tr = td.find_parent("tr")
                if parent_tr:
                    all_tds = parent_tr.find_all("td")
                    for i, t in enumerate(all_tds):
                        if t.get_text(strip=True) == txt and i + 1 < len(all_tds):
                            val = all_tds[i + 1].get_text(strip=True)
                            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", val)
                            if year_match:
                                return int(year_match.group(1))
        return None

    except Exception as e:
        return None


def main():
    """主函数：抽样处理高频无年份屋苑"""
    # 加载listings
    with open(LISTINGS_CSV, "r", encoding="utf-8") as f:
        listings = list(csv.DictReader(f))

    # 筛选无year_built的listing
    no_year = [x for x in listings if not x.get("year_built") or not str(x.get("year_built")).strip()]
    estates_freq = Counter(x["estate"] for x in no_year)
    
    # 取top 100高频屋苑（覆盖最多listings）
    top_estates = [e for e, _ in estates_freq.most_common(100)]
    
    print(f"Total listings without year: {len(no_year)}")
    print(f"Unique estates without year: {len(estates_freq)}")
    print(f"Sampling top {len(top_estates)} estates (covering {sum(estates_freq[e] for e in top_estates)} listings)")

    # 尝试加载已有结果（断点续爬）
    estate_years = {}
    if OUTPUT_JSON.exists():
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            estate_years = json.load(f)
        print(f"Loaded {len(estate_years)} existing results")

    log_lines = []
    processed = 0

    for estate in top_estates:
        if estate in estate_years:
            continue  # 已处理过

        year = fetch_detail_year(estate)
        if year:
            estate_years[estate] = year
            log_lines.append(f"{estate}: {year}")
            print(f"  {estate}: {year}")
        else:
            log_lines.append(f"{estate}: NOT_FOUND")
            print(f"  {estate}: NOT_FOUND")

        processed += 1
        time.sleep(REQUEST_DELAY)

    # 保存结果
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(estate_years, f, ensure_ascii=False, indent=2)

    with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print(f"\nDone. Found {len(estate_years)} / {len(top_estates)} years")
    print(f"Saved to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
