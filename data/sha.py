# 煞氣查表數據

SHA_TABLE = {
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
    "二五交加": {
        "severity": "重度",
        "penalty": -15,
        "remedy": "六銅錢或金屬風水物化泄",
        "cost": "低",
        "desc": "二黑病符+五黃大煞同宮"
    },
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
