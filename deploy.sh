#!/bin/bash
set -e

# 風水樓 MVP 一鍵部署腳本
# 使用方式：
#   1. 將此腳本和全部代碼上傳到服務器
#   2. chmod +x deploy.sh
#   3. ./deploy.sh

echo "========================================"
echo "  風水樓 MVP 部署腳本"
echo "========================================"

# 配置
DOMAIN="fengshuilou.com"
EMAIL="your-email@example.com"  # 用於 Let's Encrypt

# 檢查依賴
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝。請先安裝 Docker 和 Docker Compose。"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安裝。請先安裝。"
    exit 1
fi

# 創建 SSL 目錄
mkdir -p ssl

# 如果使用 Let's Encrypt（需要有域名指向此服務器）
read -p "是否使用 Let's Encrypt 自動獲取 SSL 證書？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📝 安裝 certbot..."
    apt-get update && apt-get install -y certbot
    
    echo "📝 獲取 SSL 證書..."
    certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --agree-tos -m $EMAIL --non-interactive
    
    echo "📝 複製證書到 ssl 目錄..."
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/cert.pem
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/key.pem
    
    # 設置自動續期
    echo "0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /app/ssl/cert.pem && cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /app/ssl/key.pem && docker-compose restart nginx" | crontab -
    echo "✅ 自動續期已設置"
else
    echo "⚠️  請手動將 SSL 證書放入 ssl/ 目錄："
    echo "   ssl/cert.pem - 證書鏈"
    echo "   ssl/key.pem - 私鑰"
    read -p "按 Enter 繼續（已放置證書後）..."
fi

# 構建並啟動
echo "🐳 構建 Docker 鏡像..."
docker-compose build

echo "🚀 啟動服務..."
docker-compose up -d

# 等待服務啟動
sleep 5

# 健康檢查
echo "🏥 健康檢查..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ 後端 API 運行正常"
else
    echo "⚠️ 後端 API 可能未啟動，請檢查日誌：docker-compose logs fengshuilou"
fi

echo ""
echo "========================================"
echo "  ✅ 部署完成！"
echo "========================================"
echo ""
echo "訪問地址："
echo "  https://$DOMAIN"
echo "  https://www.$DOMAIN"
echo ""
echo "管理命令："
echo "  查看日誌：docker-compose logs -f"
echo "  重啟：    docker-compose restart"
echo "  停止：    docker-compose down"
echo "  更新：    docker-compose build && docker-compose up -d"
echo ""
echo "API 測試："
echo "  curl https://$DOMAIN/health"
echo ""
