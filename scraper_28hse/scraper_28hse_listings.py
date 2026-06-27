#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
28HSE 在售楼盘爬虫 v2 — 精确解析版
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import csv
import time
import re
from bs4 import BeautifulSoup
from pathlib import Path

BASE_URL = "https://www.28hse.com/buy"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8",
}
REQUEST_DELAY = 0.5
OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_CSV = OUTPUT_DIR / "listings_28hse.csv"


def parse_listing_item(item):
    """精确解析单个楼盘条目"""
    try:
        result = {
            "title": "", "estate": "", "district": "", "facing": "",
            "price_raw": "", "build_area": "", "usable_area": "",
            "rooms": "", "unit_info": "", "year_built": "",
            "agent": "", "property_type": "", "developer": "",
            "tags": "", "time_posted": "",
        }

        # 1. 标题: .header
        header = item.select_one('.header')
        if header:
            result["title"] = header.get_text(strip=True)

        # 2. 发布时间: .description .right.floated .ui.label
        time_label = item.select_one('.description .right.floated .ui.label')
        if time_label:
            result["time_posted"] = time_label.get_text(strip=True).replace(" 刊登", "").strip()

        # 3. 地区+屋苑: .district_area
        # HTML结构: <a>地区</a> <a>屋苑</a> | <span>单位</span>
        district_area = item.select_one('.district_area')
        if district_area:
            all_links = district_area.select('a')
            if len(all_links) >= 2:
                result["district"] = all_links[0].get_text(strip=True)  # 第1个<a>是地区
                result["estate"] = all_links[1].get_text(strip=True)    # 第2个<a>是屋苑
            elif len(all_links) == 1:
                result["district"] = all_links[0].get_text(strip=True)
                result["estate"] = ""
            # 单位信息: .unit_desc
            unit_desc = district_area.select_one('.unit_desc')
            if unit_desc:
                result["unit_info"] = unit_desc.get_text(strip=True)

        # 4. 面积: .areaUnitPrice
        area_div = item.select_one('.areaUnitPrice')
        if area_div:
            text = area_div.get_text(strip=True)
            # 实用面积: 506 呎 @18,182 元 (span分离后可能带空格)
            usable_match = re.search(r'實用面積:\s*([\d,]+)\s*呎', text)
            if usable_match:
                result["usable_area"] = usable_match.group(1).replace(",", "")
            build_match = re.search(r'建築面積:\s*([\d,]+)\s*呎', text)
            if build_match:
                result["build_area"] = build_match.group(1).replace(",", "")

        # 5. 代理公司: .companyName
        company = item.select_one('.companyName')
        if company:
            result["agent"] = company.get_text(strip=True)

        # 6. 价格 + 房数 + 浴室 + 朝向 + 物业类型 + 标签: .extra
        extra = item.select_one('.extra')
        if extra:
            # 价格: .ui.right.floated.red.large.label
            price_label = extra.select_one('.ui.right.floated.red.large.label')
            if price_label:
                text = price_label.get_text(strip=True)
                price_match = re.search(r'\$\s*([\d,]+)\s*萬元', text)
                if price_match:
                    result["price_raw"] = price_match.group(1).replace(",", "")
                elif "價格面議" in text:
                    result["price_raw"] = "面議"

            # 标签: .tagLabels .ui.label
            tag_labels = extra.select('.tagLabels .ui.label')
            tags = []
            for label in tag_labels:
                text = label.get_text(strip=True)
                if not text:
                    continue
                # 房数 (如 "2 房")
                room_match = re.match(r'(\d+)\s*房$', text)
                if room_match:
                    result["rooms"] = f"{room_match.group(1)}房"
                    continue
                # 浴室 (如 "1 浴室")
                bath_match = re.match(r'(\d+)\s*浴室$', text)
                if bath_match:
                    if result["rooms"]:
                        result["rooms"] += f"{bath_match.group(1)}浴"
                    else:
                        result["rooms"] = f"{bath_match.group(1)}浴"
                    continue
                # 开放式
                if text == "開放式間隔":
                    result["rooms"] = "開放式"
                    continue
                # 5+ 房
                if re.match(r'\d+\+\s*房', text):
                    result["rooms"] = text
                    continue
                # 朝向
                facing_match = re.match(r'向(東|南|西|北|東南|東北|西南|西北)$', text)
                if facing_match:
                    result["facing"] = text
                    continue
                # 物业类型
                property_types = ["私人屋苑", "居屋", "公屋", "唐樓", "洋樓", "單幢式大廈", "村屋", "獨立屋"]
                if text in property_types:
                    result["property_type"] = text
                    continue
                # 开发商
                developers = [
                    "新鴻基", "長實", "恒基", "信和", "新世界", "會德豐", "南豐",
                    "華懋", "太古", "恒隆", "嘉里建設", "和記黃埔", "中國海外",
                    "香港房協", "嘉華", "永泰", "九龍建業", "宏安", "香港興業",
                    "億京", "泛海", "添宙", "宇晴", "晉誠", "萬方", "新港",
                    "富榮", "喜置", "凱樂", "世紀21"
                ]
                if text in developers:
                    result["developer"] = text
                    continue
                # 其他标签
                tags.append(text)

            result["tags"] = ",".join(tags)

        return result

    except Exception as e:
        print(f"  Parse error: {e}")
        return None


def fetch_page(page_num):
    url = f"{BASE_URL}?page={page_num}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  Request failed page={page_num}: {e}")
        return None


def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('.item.property_item')
    print(f"  Found {len(items)} property items")

    listings = []
    for item in items:
        listing = parse_listing_item(item)
        if listing and listing.get("estate") and listing.get("price_raw"):
            listings.append(listing)

    return listings


def scrape_all_pages(max_pages=None, start_page=1):
    all_listings = []
    page = start_page

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 尝试从断点继续（不清空已有数据）
    if OUTPUT_CSV.exists():
        with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
            existing = list(csv.DictReader(f))
            if existing:
                print(f"Found {len(existing)} existing records, appending mode")
                all_listings = existing

    while True:
        if max_pages and page > max_pages:
            print(f"Max page limit {max_pages} reached, stopping")
            break

        print(f"Fetching page {page}...")
        html = fetch_page(page)

        if not html:
            print(f"Page {page} fetch failed, retrying...")
            time.sleep(5)
            html = fetch_page(page)
            if not html:
                print(f"Page {page} retry failed, stopping")
                break

        listings = parse_page(html)

        if not listings:
            print(f"Page {page} no data, might be at end")
            break

        all_listings.extend(listings)
        print(f"  Added {len(listings)}, total {len(all_listings)}")

        # 每10页保存
        if page % 10 == 0:
            save_to_csv(all_listings)
            print(f"  Saved to {OUTPUT_CSV}")

        time.sleep(REQUEST_DELAY)
        page += 1

    save_to_csv(all_listings)
    print(f"\nDone! Total {len(all_listings)} records")
    print(f"Saved to: {OUTPUT_CSV}")
    return all_listings


def save_to_csv(listings):
    if not listings:
        return

    fieldnames = [
        "title", "estate", "district", "facing", "price_raw",
        "build_area", "usable_area", "rooms", "unit_info",
        "year_built", "agent", "property_type", "developer", "tags", "time_posted"
    ]

    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for listing in listings:
            row = {k: listing.get(k, "") for k in fieldnames}
            writer.writerow(row)


if __name__ == "__main__":
    max_pages = None
    start_page = 1
    if len(sys.argv) > 1:
        max_pages = int(sys.argv[1])
    if len(sys.argv) > 2:
        start_page = int(sys.argv[2])

    scrape_all_pages(max_pages=max_pages, start_page=start_page)
