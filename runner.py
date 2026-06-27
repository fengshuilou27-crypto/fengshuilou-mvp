#!/usr/bin/env python3
"""
整合 Runner - 執行三個回測案例並輸出結果
Usage: python runner.py
"""
import requests
import json
import os
import threading
import time
from datetime import datetime
import uvicorn

# 在内部启动服务器
import app as app_module

BASE_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = "./test_results"

def run_server():
    uvicorn.run(app_module.app, host="127.0.0.1", port=8000, log_level="warning")

server = threading.Thread(target=run_server, daemon=True)
server.start()
time.sleep(2)

# 三個回測案例
TEST_CASES = [
    {
        "name": "太古城",
        "description": "正南/子山午向/九運到山到向",
        "request": {
            "request_meta": {
                "eval_year": 2026,
                "user_gender": "男",
                "birth_date": "1985-08-20",
                "building_year": 1986,
                "building_facing": "子山午向",
                "floor_number": 15,
                "goal": "財富",
                "north_has_water": True,
                "south_has_mountain": False,
                "detected_shas": []
            }
        }
    },
    {
        "name": "沙田第一城",
        "description": "西北/乾山巽向/八運到山到向",
        "request": {
            "request_meta": {
                "eval_year": 2026,
                "user_gender": "女",
                "birth_date": "1990-03-15",
                "building_year": 1984,
                "building_facing": "乾山巽向",
                "floor_number": 8,
                "goal": "家庭和睦",
                "north_has_water": False,
                "south_has_mountain": True,
                "detected_shas": []
            }
        }
    },
    {
        "name": "YOHO Town",
        "description": "東向/卯山酉向/八運雙星會向",
        "request": {
            "request_meta": {
                "eval_year": 2026,
                "user_gender": "男",
                "birth_date": "1992-11-08",
                "building_year": 2004,
                "building_facing": "卯山酉向",
                "floor_number": 22,
                "goal": "財富",
                "north_has_water": True,
                "south_has_mountain": False,
                "detected_shas": []
            }
        }
    }
]


def ensure_server_running():
    """檢查服務是否運行"""
    try:
        resp = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ 服務運行中: v{data.get('version', 'unknown')}, 支持{data.get('supported_facings', '?')}個坐向")
            return True
    except Exception as e:
        print(f"❌ 服務未運行: {e}")
        print("請先運行: python app.py")
        return False


def run_test_case(test_case):
    """執行單個測試案例"""
    print(f"\n{'='*60}")
    print(f"📍 案例: {test_case['name']}")
    print(f"📝 {test_case['description']}")
    print(f"{'='*60}")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/evaluate",
            json=test_case['request'],
            timeout=30
        )
        
        if resp.status_code != 200:
            print(f"❌ HTTP 錯誤: {resp.status_code}")
            print(resp.text)
            return None
        
        result = resp.json()
        
        if result.get('status') != 'success':
            print(f"❌ 評估失敗: {result}")
            return result
        
        match = result['match_result']
        
        # 打印關鍵結果
        print(f"\n📊 總分: {match['final_score']}/100")
        print(f"⭐ 評級: {match['rating']}")
        print(f"🎯 置信度: {match['confidence']*100:.0f}%")
        
        # 分項得分
        print(f"\n📋 分項得分:")
        for key, value in match['score_breakdown'].items():
            print(f"  - {key}: {value}")
        
        # 八字信息
        if 'bazi_data' in match:
            print(f"\n📅 八字四柱:")
            bazi = match['bazi_data']
            print(f"  年柱: {bazi.get('year_pillar', 'N/A')}")
            print(f"  月柱: {bazi.get('month_pillar', 'N/A')}")
            print(f"  日柱: {bazi.get('day_pillar', 'N/A')}")
            print(f"  時柱: {bazi.get('hour_pillar', 'N/A')}")
            print(f"  日主: {bazi.get('day_master', 'N/A')}")
        
        # 雙期飛星
        if match.get('dual_period_flying_star'):
            dp = match['dual_period_flying_star']
            print(f"\n🏛️ 雙期飛星:")
            print(f"  Building Yun: {dp['building_yun']}")
            print(f"  Current Yun: {dp['current_yun']}")
            if dp.get('building_yun_analysis'):
                print(f"  Building Score: {dp['building_yun_analysis']['score']}/40")
            if dp.get('current_yun_analysis'):
                print(f"  Current Score: {dp['current_yun_analysis']['score']}/40")
        
        # 風險標記
        if match['flags']:
            print(f"\n⚠️ 風險標記:")
            for flag, value in match['flags'].items():
                if value:
                    print(f"  - {flag}: {value}")
        
        # 化解建議
        if match.get('recommended_remedies'):
            print(f"\n💡 化解建議:")
            for remedy in match['recommended_remedies']:
                print(f"  - {remedy['item']}: {remedy['purpose']} (成本: {remedy['cost']})")
        
        return result
        
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        return None


def save_results(results):
    """保存結果到文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存完整 JSON
    full_path = os.path.join(OUTPUT_DIR, f"all_results_{timestamp}.json")
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 完整結果已保存: {full_path}")
    
    # 保存每個案例的簡化結果
    for case_name, result in results.items():
        if result and result.get('status') == 'success':
            match = result['match_result']
            summary = {
                "case_name": case_name,
                "final_score": match['final_score'],
                "rating": match['rating'],
                "confidence": match['confidence'],
                "score_breakdown": match['score_breakdown'],
                "radar_chart": match.get('radar_chart'),
                "dual_period": match.get('dual_period_flying_star'),
                "flags": match['flags'],
                "ai_rationale": match['ai_rationale'],
                "recommended_remedies": match.get('recommended_remedies', []),
                "yun_conversion_advice": match.get('yun_conversion_advice')
            }
            
            case_path = os.path.join(OUTPUT_DIR, f"{case_name}_{timestamp}.json")
            with open(case_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"💾 {case_name} 結果已保存: {case_path}")


def main():
    print("🚀 AI風水樓盤匹配系統 - 整合 Runner")
    print(f"{'='*60}")
    
    # 檢查服務
    if not ensure_server_running():
        return 1
    
    # 執行所有案例
    results = {}
    for test_case in TEST_CASES:
        result = run_test_case(test_case)
        results[test_case['name']] = result
    
    # 保存結果
    save_results(results)
    
    # 總結
    print(f"\n{'='*60}")
    print("📊 執行總結")
    print(f"{'='*60}")
    for name, result in results.items():
        if result and result.get('status') == 'success':
            score = result['match_result']['final_score']
            print(f"  ✅ {name}: {score}/100")
        else:
            print(f"  ❌ {name}: 失敗")
    
    print(f"\n{'='*60}")
    print("✅ 所有案例執行完成")
    print(f"📁 結果保存在: {os.path.abspath(OUTPUT_DIR)}")
    print(f"{'='*60}")
    
    return 0


if __name__ == "__main__":
    exit(main())
