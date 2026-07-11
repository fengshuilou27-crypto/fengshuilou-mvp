# 風水樓 v3.0 — Next.js 前端

基於 React + Next.js 14 + TypeScript + Tailwind CSS 的全新前端架構。

## 品牌設計系統

### 色彩
- **主色** `#1a3c2a` — 深翡翠綠（代表風水、自然、穩重）
- **輔色** `#c9a961` — 古金色（代表吉祥、傳統、尊貴）
- **宣紙白** `#f5f0e8` — 背景色（傳統書卷感）
- **墨黑** `#1a1a2e` — 文字色（古典韻味）

### 字體
- **Display**: Noto Serif TC（標題、品牌字）
- **Body**: Noto Sans TC（正文、UI 文字）

### 視覺風格
- 新中式現代風格，結合傳統風水元素與現代 UI 設計
- 圓角卡片、柔和陰影、金色點綴
- 裝飾性分隔線、網格紋理背景

## 技術棧

- **Next.js 14** (App Router, Static Export)
- **React 18** + TypeScript
- **Tailwind CSS** (自定義品牌主題)
- **Framer Motion** (動畫)
- **Lucide React** (圖標)

## 項目結構

```
src/
  app/              # Next.js App Router 頁面
    page.tsx        # 首頁 (Hero + Features + HowItWorks + Stats + CTA)
    layout.tsx      # 根佈局 (Header + Footer + Disclaimer)
    disclaimer/     # 免責聲明頁
    privacy/        # 私隱政策頁
    terms/          # 服務條款頁
    module1/        # 自測住所 (占位)
    module2/        # 搜尋樓盤 (占位)
    module3/        # 樓盤匹配 (占位)
    fxti/           # FXTI 測試 (占位)
  components/
    layout/         # Header, Footer
    sections/       # Hero, Features, HowItWorks, Stats, CTA
    providers/      # DisclaimerProvider
    ui/             # 共享 UI 組件
  lib/
    utils.ts        # 工具函數
```

## 開發命令

```bash
npm install
npm run dev      # 開發模式
npm run build    # 靜態構建 (輸出到 dist/)
```

## 部署

構建輸出 `dist/` 文件夾可部署到任何靜態託管服務：
- Vercel（推薦）
- Netlify
- Cloudflare Pages
- Render Static Site

## 與後端 API 集成

API 調用通過 Next.js rewrites 代理到 `https://fengshuilou.com/api/*`。

實際分析功能（module1/2/3, fxti）需要額外開發表單組件和 API 集成。

## 待開發項目

1. Module 1: 自測住所表單 + 分析結果頁面
2. Module 2: 樓盤列表 + 篩選 + 詳情頁面
3. Module 3: 智能匹配表單 + 匹配結果頁面
4. FXTI: 問卷表單 + 性格分析結果頁面
5. 用戶認證系統（登入/註冊）
6. 支付與訂閱系統（Stripe）
7. 風水師合作平台
