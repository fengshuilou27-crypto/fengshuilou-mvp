#!/bin/bash
set -e

# 風水樓 MVP 一鍵更新腳本 (v2.5.1)
# 用於已部署服務器的快速更新

echo "========================================"
echo "  風水樓 MVP 快速更新腳本"
echo "  版本: v2.5.1"
echo "========================================"

# 進入項目目錄
cd /app/fengshuilou-mvp 2>/dev/null || cd ~/fengshuilou-mvp 2>/dev/null || cd ./fengshuilou-mvp 2>/dev/null || {
    echo "❌ 找不到項目目錄。請確認當前目錄包含 docker-compose.yml"
    exit 1
}

echo "📂 工作目錄: $(pwd)"

# 拉取最新代碼
echo "📥 拉取最新代碼..."
git pull origin main

# 清理舊容器和鏡像（可選）
echo "🧹 清理舊容器..."
docker-compose down

# 重新構建並啟動
echo "🐳 重新構建 Docker 鏡像..."
docker-compose build --no-cache

echo "🚀 啟動服務..."
docker-compose up -d

# 等待服務啟動
sleep 8

# 健康檢查
echo "🏥 健康檢查..."
if curl -s http://localhost:8000/api/health | grep -q "healthy\|ok"; then
    echo "✅ 後端 API 運行正常"
else
    echo "⚠️  後端 API 可能未啟動，檢查日誌..."
    docker-compose logs --tail=20 fengshuilou
fi

# 檢查版本
echo ""
echo "📋 檢查線上版本..."
VERSION=$(curl -s https://fengshuilou.com/ | grep -oP 'v2\.[0-9.]+' | head -1)
echo "   線上版本: $VERSION"

echo ""
echo "========================================"
echo "  ✅ 更新完成！"
echo "========================================"
echo ""
echo "訪問地址："
echo "  https://fengshuilou.com"
echo ""
echo "管理命令："
echo "  查看日誌：docker-compose logs -f"
echo "  重啟：    docker-compose restart"
echo "  停止：    docker-compose down"
echo ""
