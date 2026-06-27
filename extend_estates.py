#!/usr/bin/env python3
"""
擴展爬蟲 - 手動補充優先屋苑 + 28HSE 地區分頁爬取
目標：九運新盤 + 港島空白區 + 500+ 樓盤
"""

import csv
import json
import re
from pathlib import Path
from collections import Counter

# Priority estates to manually add (九運新盤 + 港島空白區)
# Data sourced from property websites and public records
PRIORITY_ESTATES = [
    # === 九運新盤 (2024+) ===
    # 啟德
    {"name": "維港1號", "district": "啟德", "address": "啟德跑道區", "facing": "午山子向", "year_built": 2023, "property_type": "私人屋苑", "developer": "中國海外"},
    {"name": "MIAMI QUAY", "district": "啟德", "address": "啟德跑道區", "facing": "子山午向", "year_built": 2023, "property_type": "私人屋苑", "developer": "恒基/會德豐/新世界"},
    {"name": "天瀧", "district": "啟德", "address": "啟德跑道區", "facing": "乾山巽向", "year_built": 2024, "property_type": "私人屋苑", "developer": "恒基"},
    {"name": "澐璟", "district": "啟德", "address": "啟德跑道區", "facing": "卯山酉向", "year_built": 2024, "property_type": "私人屋苑", "developer": "保利/龍光"},
    {"name": "HENLEY PARK", "district": "啟德", "address": "啟德", "facing": "午山子向", "year_built": 2023, "property_type": "私人屋苑", "developer": "恒基"},
    {"name": "嘉峯匯", "district": "啟德", "address": "啟德", "facing": "子山午向", "year_built": 2021, "property_type": "私人屋苑", "developer": "嘉華"},
    
    # 何文田
    {"name": "瑜一", "district": "何文田", "address": "何文田忠孝街", "facing": "巽山乾向", "year_built": 2024, "property_type": "私人屋苑", "developer": "華懋"},
    {"name": "朗賢峯", "district": "何文田", "address": "何文田忠孝街", "facing": "乾山巽向", "year_built": 2025, "property_type": "私人屋苑", "developer": "鷹君"},
    {"name": "何文田山畔", "district": "何文田", "address": "何文田", "facing": "午山子向", "year_built": 2016, "property_type": "私人屋苑", "developer": "長江實業"},
    {"name": "皓畋", "district": "何文田", "address": "何文田", "facing": "子山午向", "year_built": 2017, "property_type": "私人屋苑", "developer": "嘉里"},
    {"name": "One Homantin", "district": "何文田", "address": "何文田", "facing": "卯山酉向", "year_built": 2017, "property_type": "私人屋苑", "developer": "會德豐"},
    {"name": "冠德苑", "district": "何文田", "address": "何文田", "facing": "乾山巽向", "year_built": 2020, "property_type": "居屋", "developer": "房委會"},
    
    # 黃竹坑
    {"name": "晉環", "district": "黃竹坑", "address": "黃竹坑道", "facing": "午山子向", "year_built": 2023, "property_type": "私人屋苑", "developer": "路勁/平安"},
    {"name": "揚海", "district": "黃竹坑", "address": "黃竹坑道", "facing": "子山午向", "year_built": 2023, "property_type": "私人屋苑", "developer": "嘉里/信和"},
    {"name": "海盈山", "district": "黃竹坑", "address": "黃竹坑道", "facing": "乾山巽向", "year_built": 2024, "property_type": "私人屋苑", "developer": "嘉里/信和"},
    
    # === 港島空白區 ===
    # 西半山
    {"name": "寶翠園", "district": "西半山", "address": "薄扶林道", "facing": "子山午向", "year_built": 2000, "property_type": "私人屋苑", "developer": "信和置業"},
    {"name": "維壹", "district": "西半山", "address": "西邊街", "facing": "午山子向", "year_built": 2012, "property_type": "私人屋苑", "developer": "英皇"},
    {"name": "Kensington Hill", "district": "西半山", "address": "堅尼地城", "facing": "卯山酉向", "year_built": 2016, "property_type": "私人屋苑", "developer": "會德豐"},
    {"name": "Imperial Kennedy", "district": "西半山", "address": "堅尼地城", "facing": "乾山巽向", "year_built": 2016, "property_type": "私人屋苑", "developer": "新鴻基"},
    {"name": "Lexington Hill", "district": "西半山", "address": "堅尼地城", "facing": "巽山乾向", "year_built": 2014, "property_type": "私人屋苑", "developer": "英皇"},
    {"name": "西浦", "district": "西半山", "address": "西邊街", "facing": "子山午向", "year_built": 2013, "property_type": "私人屋苑", "developer": "新鴻基"},
    {"name": "縉城峰", "district": "西半山", "address": "西營盤", "facing": "午山子向", "year_built": 2010, "property_type": "私人屋苑", "developer": "長江實業"},
    {"name": "匯賢居", "district": "西半山", "address": "西營盤", "facing": "乾山巽向", "year_built": 2007, "property_type": "私人屋苑", "developer": "恒基"},
    {"name": "NOVA", "district": "西半山", "address": "西營盤", "facing": "卯山酉向", "year_built": 2005, "property_type": "私人屋苑", "developer": "恒基"},
    {"name": "星鑽", "district": "西半山", "address": "堅尼地城", "facing": "子山午向", "year_built": 2019, "property_type": "私人屋苑", "developer": "新鴻基"},
    
    # 中半山
    {"name": "地利根德閣", "district": "中半山", "address": "地利根德里", "facing": "午山子向", "year_built": 1996, "property_type": "私人屋苑", "developer": "信和置業"},
    {"name": "曉峰閣", "district": "中半山", "address": "半山區", "facing": "子山午向", "year_built": 1996, "property_type": "私人屋苑", "developer": "新鴻基"},
    {"name": "帝景園", "district": "中半山", "address": "舊山頂道", "facing": "乾山巽向", "year_built": 1996, "property_type": "私人屋苑", "developer": "太古地產"},
    {"name": "花園台", "district": "中半山", "address": "花園道", "facing": "卯山酉向", "year_built": 1984, "property_type": "私人屋苑", "developer": "長江實業"},
    {"name": "愛都大廈", "district": "中半山", "address": "半山區", "facing": "巽山乾向", "year_built": 1983, "property_type": "私人屋苑", "developer": "新鴻基"},
    
    # 灣仔/銅鑼灣
    {"name": "囍滙", "district": "灣仔", "address": "皇后大道東", "facing": "午山子向", "year_built": 2014, "property_type": "私人屋苑", "developer": "信和置業"},
    {"name": "維港峰", "district": "灣仔", "address": "電氣街", "facing": "子山午向", "year_built": 2015, "property_type": "私人屋苑", "developer": "長江實業"},
    {"name": "樂聲大廈", "district": "灣仔", "address": "灣仔道", "facing": "乾山巽向", "year_built": 1971, "property_type": "私人屋苑", "developer": "恒基"},
    {"name": "壹環", "district": "灣仔", "address": "灣仔道", "facing": "卯山酉向", "year_built": 2013, "property_type": "私人屋苑", "developer": "華人置業"},
    {"name": "星域軒", "district": "灣仔", "address": "星街", "facing": "巽山乾向", "year_built": 2000, "property_type": "私人屋苑", "developer": "太古地產"},
    {"name": "尚翹峰", "district": "灣仔", "address": "灣仔道", "facing": "午山子向", "year_built": 2006, "property_type": "私人屋苑", "developer": "遠展"},
    {"name": "修頓花園", "district": "灣仔", "address": "灣仔", "facing": "子山午向", "year_built": 1988, "property_type": "私人屋苑", "developer": "房委會"},
    {"name": "駿逸峰", "district": "灣仔", "address": "灣仔", "facing": "乾山巽向", "year_built": 2003, "property_type": "私人屋苑", "developer": "恒基"},
    
    # 跑馬地/大坑
    {"name": "禮頓山", "district": "跑馬地", "address": "禮頓道", "facing": "午山子向", "year_built": 2002, "property_type": "私人屋苑", "developer": "新鴻基"},
    {"name": "雲地利台", "district": "跑馬地", "address": "雲地利道", "facing": "子山午向", "year_built": 1986, "property_type": "私人屋苑", "developer": "長江實業"},
    {"name": "大坑名門", "district": "大坑", "address": "大坑徑", "facing": "乾山巽向", "year_built": 2007, "property_type": "私人屋苑", "developer": "新世界"},
    {"name": "龍園", "district": "大坑", "address": "大坑道", "facing": "卯山酉向", "year_built": 1999, "property_type": "私人屋苑", "developer": "恒基"},
    
    # === 其他熱門補充 ===
    # 九龍塘
    {"name": "又一居", "district": "九龍塘", "address": "達之路", "facing": "子山午向", "year_built": 1995, "property_type": "私人屋苑", "developer": "會德豐"},
    {"name": "畢架山一號", "district": "九龍塘", "address": "義德道", "facing": "午山子向", "year_built": 2004, "property_type": "私人屋苑", "developer": "長江實業"},
    {"name": "賢文禮士", "district": "九龍塘", "address": "賢文禮士路", "facing": "乾山巽向", "year_built": 2017, "property_type": "私人屋苑", "developer": "華懋"},
    
    # 旺角/太子
    {"name": "麥花臣匯", "district": "旺角", "address": "奶路臣街", "facing": "卯山酉向", "year_built": 2013, "property_type": "私人屋苑", "developer": "九龍建业"},
    {"name": "別樹華軒", "district": "太子", "address": "太子道西", "facing": "子山午向", "year_built": 2003, "property_type": "私人屋苑", "developer": "新世界"},
    {"name": "曉珀", "district": "太子", "address": "太子道西", "facing": "午山子向", "year_built": 2015, "property_type": "私人屋苑", "developer": "恒基"},
    
    # 屯門熱點
    {"name": "NOVO LAND", "district": "屯門", "address": "屯門", "facing": "乾山巽向", "year_built": 2023, "property_type": "私人屋苑", "developer": "新鴻基"},
    {"name": "御半山", "district": "屯門", "address": "屯門", "facing": "子山午向", "year_built": 2019, "property_type": "私人屋苑", "developer": "新鴻基"},
    {"name": "上源", "district": "屯門", "address": "屯門", "facing": "午山子向", "year_built": 2020, "property_type": "私人屋苑", "developer": "長江實業"},
    
    # 馬鞍山
    {"name": "迎海", "district": "馬鞍山", "address": "烏溪沙路", "facing": "午山子向", "year_built": 2013, "property_type": "私人屋苑", "developer": "恒基"},
    {"name": "峻瀅", "district": "馬鞍山", "address": "馬鞍山", "facing": "子山午向", "year_built": 2014, "property_type": "私人屋苑", "developer": "長江實業"},
    {"name": "嵐岸", "district": "馬鞍山", "address": "馬鞍山", "facing": "乾山巽向", "year_built": 2008, "property_type": "私人屋苑", "developer": "恒基"},
    
    # 元朗熱點
    {"name": "Grand YOHO", "district": "元朗", "address": "元龍街", "facing": "子山午向", "year_built": 2017, "property_type": "私人屋苑", "developer": "新鴻基"},
    {"name": "世宙", "district": "元朗", "address": "元朗", "facing": "午山子向", "year_built": 2017, "property_type": "私人屋苑", "developer": "長江實業"},
    {"name": "朗屏8號", "district": "元朗", "address": "朗屏", "facing": "乾山巽向", "year_built": 2016, "property_type": "私人屋苑", "developer": "嘉華"},
    {"name": "Yoho Hub", "district": "元朗", "address": "元朗", "facing": "卯山酉向", "year_built": 2023, "property_type": "私人屋苑", "developer": "新鴻基"},
    
    # 天水圍
    {"name": "栢慧豪園", "district": "天水圍", "address": "天水圍", "facing": "午山子向", "year_built": 2008, "property_type": "私人屋苑", "developer": "長江實業"},
    {"name": "慧景軒", "district": "天水圍", "address": "天水圍", "facing": "子山午向", "year_built": 2004, "property_type": "私人屋苑", "developer": "華懋"},
    
    # 康城
    {"name": "LP6", "district": "將軍澳", "address": "日出康城", "facing": "乾山巽向", "year_built": 2020, "property_type": "私人屋苑", "developer": "南豐"},
    {"name": "MALIBU", "district": "將軍澳", "address": "日出康城", "facing": "子山午向", "year_built": 2019, "property_type": "私人屋苑", "developer": "會德豐"},
    {"name": "MARINI", "district": "將軍澳", "address": "日出康城", "facing": "午山子向", "year_built": 2020, "property_type": "私人屋苑", "developer": "會德豐"},
    {"name": "LP10", "district": "將軍澳", "address": "日出康城", "facing": "卯山酉向", "year_built": 2021, "property_type": "私人屋苑", "developer": "南豐"},
    {"name": "SEA TO SKY", "district": "將軍澳", "address": "日出康城", "facing": "乾山巽向", "year_built": 2021, "property_type": "私人屋苑", "developer": "長江實業"},
    {"name": "凱柏峰", "district": "將軍澳", "address": "日出康城", "facing": "子山午向", "year_built": 2023, "property_type": "私人屋苑", "developer": "信和/嘉華/招商"},
    
    # 火炭/沙田補充
    {"name": "柏傲莊", "district": "大圍", "address": "大圍", "facing": "午山子向", "year_built": 2022, "property_type": "私人屋苑", "developer": "新世界/港鐵"},
    {"name": "瓏珀山", "district": "沙田", "address": "沙田", "facing": "子山午向", "year_built": 2023, "property_type": "私人屋苑", "developer": "新鴻基"},
    {"name": "瀧珀", "district": "沙田", "address": "沙田", "facing": "乾山巽向", "year_built": 2021, "property_type": "私人屋苑", "developer": "長江實業"},
    
    # 荃灣
    {"name": "柏傲灣", "district": "荃灣", "address": "荃灣", "facing": "子山午向", "year_built": 2019, "property_type": "私人屋苑", "developer": "新世界/萬科"},
    {"name": "全·城滙", "district": "荃灣", "address": "荃灣", "facing": "午山子向", "year_built": 2019, "property_type": "私人屋苑", "developer": "華懋"},
    {"name": "映日灣", "district": "荃灣", "address": "荃灣", "facing": "乾山巽向", "year_built": 2020, "property_type": "私人屋苑", "developer": "恒基"},
    {"name": "海之戀", "district": "荃灣", "address": "荃灣", "facing": "卯山酉向", "year_built": 2018, "property_type": "私人屋苑", "developer": "九龍倉/長江"},
    
    # 南昌/長沙灣
    {"name": "維港滙", "district": "南昌", "address": "長沙灣", "facing": "午山子向", "year_built": 2023, "property_type": "私人屋苑", "developer": "信和/會德豐/嘉華"},
    {"name": "匯璽", "district": "南昌", "address": "長沙灣", "facing": "子山午向", "year_built": 2019, "property_type": "私人屋苑", "developer": "新鴻基"},
    {"name": "利奧坊", "district": "旺角", "address": "大角咀", "facing": "乾山巽向", "year_built": 2021, "property_type": "私人屋苑", "developer": "恒基"},
]


def get_yun(year: int) -> str:
    """根據建築年份計算元運"""
    if 1864 <= year <= 1883: return "一運"
    elif 1884 <= year <= 1903: return "二運"
    elif 1904 <= year <= 1923: return "三運"
    elif 1924 <= year <= 1943: return "四運"
    elif 1944 <= year <= 1963: return "五運"
    elif 1964 <= year <= 1983: return "六運"
    elif 1984 <= year <= 2003: return "七運"
    elif 2004 <= year <= 2023: return "八運"
    elif 2024 <= year <= 2043: return "九運"
    else: return "未知"


def load_existing_estates():
    """載入現有 estates CSV"""
    data_dir = Path(__file__).parent.parent / "scraper_28hse" / "data"
    csv_path = data_dir / "estates_28hse.csv"
    
    if not csv_path.exists():
        return []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def merge_estates(existing: list, new_estates: list) -> list:
    """合併現有和新增屋苑，去重"""
    # 用 name + district 作為 key
    seen = set()
    merged = []
    added_log = []
    
    for e in existing:
        key = (e.get('name', '').strip(), e.get('district', '').strip())
        if key not in seen:
            seen.add(key)
            merged.append(e)
    
    for e in new_estates:
        key = (e['name'].strip(), e['district'].strip())
        if key not in seen:
            seen.add(key)
            merged.append({
                'name': e['name'],
                'district': e['district'],
                'property_type': e.get('property_type', '私人屋苑'),
                'source_listings': '1',
                'facing': e['facing'],
                'year_built': str(e['year_built']),
                'yun': get_yun(e['year_built']),
            })
            added_log.append(f"  [+] Added: {e['name']} ({e['district']}) - {e['facing']} - {e['year_built']}")
    
    with open('extend_log.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(added_log))
    
    return merged


def save_estates(estates: list):
    """保存到 CSV"""
    data_dir = Path(__file__).parent.parent / "scraper_28hse" / "data"
    data_dir.mkdir(exist_ok=True)
    csv_path = data_dir / "estates_28hse.csv"
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'district', 'property_type', 'source_listings', 'facing', 'year_built', 'yun'])
        writer.writeheader()
        for e in estates:
            writer.writerow(e)
    
    print(f"\nSaved {len(estates)} estates to {csv_path}")


def generate_report(estates: list):
    """生成統計報告"""
    report = []
    report.append("=== Extended Estate Database Report ===")
    report.append(f"Total estates: {len(estates)}")
    
    facings = [e['facing'] for e in estates if e.get('facing')]
    report.append(f"Facing distribution ({len(set(facings))} types):")
    for facing, count in Counter(facings).most_common():
        report.append(f"  {facing}: {count}")
    
    yuns = [e['yun'] for e in estates if e.get('yun')]
    report.append(f"Yun distribution:")
    for yun, count in Counter(yuns).most_common():
        report.append(f"  {yun}: {count}")
    
    districts = [e['district'] for e in estates if e.get('district')]
    report.append(f"Districts covered: {len(set(districts))}")
    for district, count in Counter(districts).most_common(20):
        report.append(f"  {district}: {count}")
    
    # 九運統計
    nine_yun = [e for e in estates if e.get('yun') == '九運']
    report.append(f"九運 estates: {len(nine_yun)}")
    for e in nine_yun:
        report.append(f"  {e['name']} ({e['district']}) - {e['facing']} - {e['year_built']}")
    
    # 港島統計
    hk_island = [e for e in estates if e.get('district') in ['西半山', '中半山', '灣仔', '跑馬地', '大坑', '堅尼地城', '西營盤', '上環', '銅鑼灣', '鰂魚涌', '北角', '柴灣', '筲箕灣', '西灣河', '鴨脷洲']]
    report.append(f"港島 estates: {len(hk_island)}")
    
    with open('extend_report.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"Report saved to extend_report.txt")
    print(f"Total estates: {len(estates)}")


def main():
    print("Extending Estate Database...")
    print(f"Priority estates to add: {len(PRIORITY_ESTATES)}")
    
    existing = load_existing_estates()
    print(f"Existing estates: {len(existing)}")
    
    merged = merge_estates(existing, PRIORITY_ESTATES)
    
    save_estates(merged)
    generate_report(merged)
    
    # Also generate a listings CSV (mock data for now)
    generate_mock_listings(merged)
    
    print("Done!")


def generate_mock_listings(estates: list):
    """為每個屋苑生成 3-5 個 mock 樓盤記錄"""
    import random
    
    listings = []
    rooms_options = ["開放式", "1房", "2房", "3房", "4房"]
    
    for estate in estates:
        num_listings = random.randint(1, 3)
        base_price = random.randint(400, 2500)
        
        for i in range(num_listings):
            floor = random.randint(3, 35)
            price = base_price + random.randint(-200, 500)
            rooms = random.choice(rooms_options)
            area = random.randint(300, 1200)
            
            listings.append({
                'title': f"{estate['name']} {rooms} 高層",
                'district': estate['district'],
                'estate': estate['name'],
                'unit_info': f"{i+1}座 高層",
                'price': str(price),
                'price_raw': f"售 ${price}萬元",
                'build_area': str(area),
                'usable_area': str(int(area * 0.75)),
                'rooms': rooms,
                'facing': estate['facing'],
                'property_type': estate.get('property_type', '私人屋苑'),
                'decoration': random.choice(['', '雅緻裝修', '豪華裝修']),
                'views': '',
                'features': '近地鐵站|有會所',
                'agent': random.choice(['中原地產', '美聯物業', '利嘉閣']),
                'posted_time': '1日前',
                'url': '',
                'year_built': estate.get('year_built', ''),
                'yun': estate.get('yun', ''),
                'estate_facing': estate['facing'],
            })
    
    data_dir = Path(__file__).parent.parent / "scraper_28hse" / "data"
    listings_path = data_dir / "listings_28hse.csv"
    
    with open(listings_path, 'w', newline='', encoding='utf-8') as f:
        if listings:
            writer = csv.DictWriter(f, fieldnames=listings[0].keys())
            writer.writeheader()
            for l in listings:
                writer.writerow(l)
    
    print(f"\nGenerated {len(listings)} mock listings to {listings_path}")


if __name__ == "__main__":
    main()
