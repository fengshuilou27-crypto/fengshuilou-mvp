# 煞氣查表數據 (v3.2 擴充版)
# 從 6 種擴充至 22 種常見煞氣

SHA_TABLE = {
    # ---- 外部形煞 (10種) ----
    "天斬煞": {
        "severity": "輕度",
        "penalty": -4,
        "remedy": "麒麟一對放窗台",
        "cost": "中",
        "desc": "兩棟大樓中間狹縫，氣流直沖"
    },
    "聲煞": {
        "severity": "中度",
        "penalty": -8,
        "remedy": "隔音窗+室內水景",
        "cost": "中",
        "desc": "噪音干擾，影響心神安寧"
    },
    "路沖": {
        "severity": "重度",
        "penalty": -12,
        "remedy": "山海鎮+植物屏風",
        "cost": "高",
        "desc": "道路直沖大門或窗戶"
    },
    "反弓煞": {
        "severity": "重度",
        "penalty": -12,
        "remedy": "八卦鏡+泰山石敢當",
        "cost": "中",
        "desc": "道路或河流呈反弓形狀直沖住宅"
    },
    "尖角煞": {
        "severity": "中度",
        "penalty": -8,
        "remedy": "銅葫蘆或植物遮擋",
        "cost": "低",
        "desc": "鄰近建築尖角直對住宅"
    },
    "壁刀煞": {
        "severity": "中度",
        "penalty": -8,
        "remedy": "八卦鏡+屏風阻隔",
        "cost": "中",
        "desc": "鄰近建築牆面如刀直切住宅"
    },
    "穿堂煞": {
        "severity": "中度",
        "penalty": -6,
        "remedy": "玄關屏風或門簾阻擋",
        "cost": "低",
        "desc": "大門直對後門或窗戶，氣流直穿"
    },
    "光煞": {
        "severity": "輕度",
        "penalty": -4,
        "remedy": "遮光窗簾或磨砂玻璃",
        "cost": "低",
        "desc": "強光反射或霓虹燈直射"
    },
    
    # ---- 飛星煞氣 (8種) ----
    "二五交加": {
        "severity": "重度",
        "penalty": -15,
        "remedy": "六銅錢或金屬風水物化泄",
        "cost": "低",
        "desc": "二黑病符+五黃大煞同宮"
    },
    "伏吟": {
        "severity": "中度",
        "penalty": -6,
        "remedy": "銅葫蘆或銅風鈴化泄",
        "cost": "低",
        "desc": "山星向星同宮伏吟，氣滯運衰"
    },
    "六七交劍": {
        "severity": "中度",
        "penalty": -8,
        "remedy": "水景或植物緩和金氣",
        "cost": "中",
        "desc": "六白七赤同宮，交劍煞臨"
    },
    "三五鬥牛": {
        "severity": "中度",
        "penalty": -8,
        "remedy": "紅色裝飾或燈光化解",
        "cost": "低",
        "desc": "三碧五黃同宮，鬥爭是非"
    },
    "五黃臨門": {
        "severity": "重度",
        "penalty": -15,
        "remedy": "銅鈴或六帝錢化解",
        "cost": "低",
        "desc": "五黃煞星飛臨大門方位"
    },
    "二黑病符": {
        "severity": "中度",
        "penalty": -8,
        "remedy": "銅葫蘆或安忍水化解",
        "cost": "低",
        "desc": "二黑病符星飛臨卧室或廚房"
    },
    
    # ---- 內部格局煞 (3種) ----
    "橫樑壓頂": {
        "severity": "中度",
        "penalty": -6,
        "remedy": "假天花遮掩或葫蘆化解",
        "cost": "中",
        "desc": "橫樑位於床、沙發或辦公桌正上方"
    },
    "廁所居中": {
        "severity": "中度",
        "penalty": -8,
        "remedy": "保持乾淨+植物+鹽燈",
        "cost": "低",
        "desc": "廁所位於住宅中心（中宮）"
    },
    "門對門": {
        "severity": "輕度",
        "penalty": -4,
        "remedy": "門簾或屏風阻隔",
        "cost": "低",
        "desc": "兩門相對，氣場相沖"
    },
    
    # ---- 環境煞 (2種) ----
    "電磁煞": {
        "severity": "輕度",
        "penalty": -4,
        "remedy": "遠離或屏蔽電磁源",
        "cost": "中",
        "desc": "高壓電塔、變電站或大型電器過近"
    },
    "陰煞": {
        "severity": "中度",
        "penalty": -8,
        "remedy": "增強採光+陽氣植物",
        "cost": "低",
        "desc": "鄰近醫院、墳場、垃圾站等陰氣重地"
    },
    
    # ---- 其他 ----
    "其他": {
        "severity": "輕度",
        "penalty": -2,
        "remedy": "請專業風水師勘察",
        "cost": "待評估",
        "desc": "其他未列明煞氣"
    }
}

SEVERITY_MAP = {
    "輕度": -4,
    "中度": -8,
    "重度": -15
}
