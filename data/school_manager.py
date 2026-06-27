#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流派配置管理器
支持JSON驅動的風水流派切換
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

# 配置文件路徑
CONFIG_PATH = Path(__file__).parent / "school_configs.json"

class SchoolConfigManager:
    """風水流派配置管理器"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or CONFIG_PATH
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加載配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """默認配置（通用版）"""
        return {
            "version": "1.0",
            "schools": {
                "default": {
                    "name": "通用版",
                    "description": "標準六維評分",
                    "dimensions": {
                        "flying_star": {"weight": 30, "max_raw_score": 40, "label": "飛星"},
                        "bazi": {"weight": 20, "max_raw_score": 20, "label": "八字"},
                        "bagua": {"weight": 15, "max_raw_score": 10, "label": "八宅"},
                        "zero_main_god": {"weight": 10, "max_raw_score": 10, "label": "零正神"},
                        "waishantou": {"weight": 10, "max_raw_score": 10, "label": "外巒頭"},
                        "location": {"weight": 10, "max_raw_score": 10, "label": "區位"},
                        "goal": {"weight": 15, "max_raw_score": 15, "label": "目標"}
                    }
                }
            }
        }
    
    def get_school(self, school_id: str = "default") -> Dict[str, Any]:
        """獲取指定流派配置"""
        return self.config.get("schools", {}).get(school_id, self.config["schools"]["default"])
    
    def list_schools(self) -> Dict[str, str]:
        """列出所有可用流派"""
        return {
            k: v["name"] 
            for k, v in self.config.get("schools", {}).items()
        }
    
    def get_dimensions(self, school_id: str = "default") -> Dict[str, Any]:
        """獲取指定流派的維度配置"""
        school = self.get_school(school_id)
        return school.get("dimensions", {})
    
    def get_weights(self, school_id: str = "default") -> Dict[str, float]:
        """獲取指定流派的權重分配"""
        dims = self.get_dimensions(school_id)
        return {k: v["weight"] for k, v in dims.items()}
    
    def calculate_score(self, school_id: str, raw_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        根據流派配置計算總分
        
        Args:
            school_id: 流派ID
            raw_scores: 各維度原始分數
        
        Returns:
            {
                "total_score": 總分(0-100),
                "breakdown": 各維度正規化分數,
                "radar_data": 雷達圖數據
            }
        """
        dims = self.get_dimensions(school_id)
        
        breakdown = {}
        total = 0
        max_total = 0
        
        for dim_id, dim_config in dims.items():
            weight = dim_config["weight"]
            max_raw = dim_config.get("max_raw_score", 100)
            raw = raw_scores.get(dim_id, 0)
            
            # 正規化到該維度的權重
            if max_raw > 0:
                normalized = (raw / max_raw) * weight
            else:
                normalized = raw  # 直接應用（如煞氣扣分）
            
            breakdown[dim_config["label"]] = round(normalized, 1)
            total += normalized
            max_total += weight
        
        # 標準化到100分制
        if max_total > 0:
            total_score = (total / max_total) * 100
        else:
            total_score = 0
        
        total_score = max(0, min(100, round(total_score, 1)))
        
        # 雷達圖數據
        radar_data = {
            "dimensions": list(breakdown.keys()),
            "scores": [
                round(min(100, max(0, (breakdown[k] / dims[v]["weight"]) * 100)), 1)
                for k, v in zip(breakdown.keys(), dims.keys())
            ],
            "max_values": [100] * len(breakdown)
        }
        
        return {
            "total_score": total_score,
            "breakdown": breakdown,
            "radar_data": radar_data,
            "school_id": school_id,
            "school_name": self.get_school(school_id)["name"]
        }
    
    def reload(self):
        """重新加載配置文件"""
        self.config = self._load_config()


# 全局實例
_school_manager = None

def get_school_manager() -> SchoolConfigManager:
    """獲取全局流派管理器實例"""
    global _school_manager
    if _school_manager is None:
        _school_manager = SchoolConfigManager()
    return _school_manager
