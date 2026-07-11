# Stripe 支付集成方案

## 1. 訂閱計劃設計

| 計劃 | 價格 | 功能 |
|------|------|------|
| **免費層** | HK$0 | 每月 3 次基礎分析 |
| **Basic** | HK$38/月 | 無限制分析 + 進階功能 |
| **Pro** | HK$98/月 | 完整功能 + 風水師諮詢 |

---

## 2. Stripe 賬戶設置

### 2.1 註冊 Stripe 賬戶
1. 訪問 https://dashboard.stripe.com/register
2. 使用公司郵箱註冊（support@fengshuilou.com）
3. 完成身份驗證（需要香港公司註冊證明）
4. 設置收款銀行賬戶（香港本地銀行）

### 2.2 創建產品和價格

在 Stripe Dashboard → Products 中創建：

```
產品名稱：風水樓 Basic
描述：無限制風水分析 + 進階功能
價格：HK$38/月（ recurring, monthly ）
```

```
產品名稱：風水樓 Pro
描述：完整功能 + 風水師諮詢
價格：HK$98/月（ recurring, monthly ）
```

記錄 Price ID（如 `price_1ABC123...`），後端需要用到。

---

## 3. 後端集成（FastAPI + Python）

### 3.1 安裝依賴

```bash
pip install stripe
```

### 3.2 環境變量

在 Render Dashboard 設置：
```
STRIPE_SECRET_KEY=sk_live_...      # 生產密鑰
STRIPE_PUBLISHABLE_KEY=pk_live_...  # 前端密鑰
STRIPE_WEBHOOK_SECRET=whsec_...    # Webhook 密鑰
STRIPE_PRICE_BASIC=price_1ABC...   # Basic 價格 ID
STRIPE_PRICE_PRO=price_1DEF...     # Pro 價格 ID
```

### 3.3 創建 Checkout Session API

```python
# routers/payments.py
import stripe
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
import os

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

router = APIRouter(prefix="/api/payments", tags=["payments"])

class CreateCheckoutRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str

@router.post("/create-checkout-session")
def create_checkout_session(request: CreateCheckoutRequest):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": request.price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            # 可選：收集用戶信息
            customer_email=None,  # 如果用戶已登入，傳入其郵箱
        )
        return {"session_id": session.id, "url": session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, WEBHOOK_SECRET)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 處理訂閱事件
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # 更新數據庫：用戶訂閱狀態
        # 記錄：customer_id, subscription_id, price_id, status
        handle_subscription_created(session)

    elif event["type"] == "invoice.paid":
        # 續費成功
        invoice = event["data"]["object"]
        handle_subscription_renewed(invoice)

    elif event["type"] == "invoice.payment_failed":
        # 續費失敗
        invoice = event["data"]["object"]
        handle_subscription_failed(invoice)

    elif event["type"] == "customer.subscription.deleted":
        # 訂閱取消
        subscription = event["data"]["object"]
        handle_subscription_cancelled(subscription)

    return {"status": "success"}
```

### 3.4 用戶訂閱管理 API

```python
@router.get("/subscription-status")
def get_subscription_status(user_id: str):
    """查詢用戶當前訂閱狀態"""
    # 從數據庫查詢
    pass

@router.post("/cancel-subscription")
def cancel_subscription(subscription_id: str):
    """取消訂閱（月末生效）"""
    try:
        stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        return {"status": "cancelled_at_period_end"}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create-portal-session")
def create_portal_session(customer_id: str):
    """創建 Stripe 客戶門戶（管理支付方式、查看發票）"""
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url="https://fengshuilou.com/account",
        )
        return {"url": session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## 4. 前端集成（React + Next.js）

### 4.1 安裝 Stripe.js

```bash
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### 4.2 訂閱頁面組件

```tsx
// app/pricing/page.tsx
'use client';

import { loadStripe } from '@stripe/stripe-js';
import { useState } from 'react';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

const plans = [
  {
    name: 'Basic',
    price: 'HK$38',
    period: '/月',
    price_id: process.env.NEXT_PUBLIC_STRIPE_PRICE_BASIC,
    features: ['無限制風水分析', '進階報告', '歷史記錄保存'],
  },
  {
    name: 'Pro',
    price: 'HK$98',
    period: '/月',
    price_id: process.env.NEXT_PUBLIC_STRIPE_PRICE_PRO,
    features: ['Basic 全部功能', '風水師 1 對 1 諮詢', '優先客戶支持', '專屬風水建議'],
    popular: true,
  },
];

export default function PricingPage() {
  const [loading, setLoading] = useState<string | null>(null);

  const handleSubscribe = async (priceId: string) => {
    setLoading(priceId);
    try {
      const response = await fetch('/api/payments/create-checkout-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          price_id: priceId,
          success_url: `${window.location.origin}/payment/success`,
          cancel_url: `${window.location.origin}/payment/cancel`,
        }),
      });
      const { url } = await response.json();
      window.location.href = url; // 重定向到 Stripe Checkout
    } catch (error) {
      alert('支付初始化失敗，請重試');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-paper py-20">
      <div className="container-brand max-w-4xl">
        <div className="text-center mb-16">
          <h1 className="heading-display text-4xl mb-4">選擇您的計劃</h1>
          <p className="text-gray-600">隨時取消，無隱藏費用</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`card-brand p-8 ${plan.popular ? 'ring-2 ring-gold-400' : ''}`}
            >
              {plan.popular && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gold-500 text-white text-xs font-bold px-4 py-1 rounded-full">
                  最受歡迎
                </span>
              )}
              <h3 className="font-display font-bold text-2xl text-brand-800">{plan.name}</h3>
              <div className="mt-4 mb-6">
                <span className="text-4xl font-bold text-brand-900">{plan.price}</span>
                <span className="text-gray-500">{plan.period}</span>
              </div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-gray-700">
                    <span className="text-green-500">✓</span> {f}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => handleSubscribe(plan.price_id!)}
                disabled={loading === plan.price_id}
                className="btn-gold w-full"
              >
                {loading === plan.price_id ? '處理中...' : '立即訂閱'}
              </button>
            </div>
          ))}
        </div>

        <p className="text-center text-gray-400 text-sm mt-12">
          所有訂閱均通過 Stripe 安全處理。我們不儲存您的信用卡信息。
        </p>
      </div>
    </div>
  );
}
```

### 4.3 成功/取消頁面

```tsx
// app/payment/success/page.tsx
export default function PaymentSuccess() {
  return (
    <div className="min-h-screen bg-paper flex items-center justify-center">
      <div className="text-center">
        <div className="text-6xl mb-4">🎉</div>
        <h1 className="heading-display text-3xl mb-4">訂閱成功！</h1>
        <p className="text-gray-600 mb-8">感謝您選擇風水樓。您現在可以享用所有進階功能。</p>
        <a href="/module1/" className="btn-primary">開始分析</a>
      </div>
    </div>
  );
}
```

---

## 5. 數據庫 Schema（訂閱表）

```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    stripe_price_id VARCHAR(255),
    plan_name VARCHAR(50), -- 'basic' | 'pro'
    status VARCHAR(50), -- 'active' | 'cancelled' | 'past_due'
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 6. Webhook 配置

### 6.1 本地開發（使用 Stripe CLI）

```bash
# 安裝 Stripe CLI
brew install stripe/stripe-cli/stripe

# 登入
stripe login

# 轉發 webhook 到本地
stripe listen --forward-to localhost:8000/api/payments/webhook
```

### 6.2 生產環境

在 Stripe Dashboard → Webhooks → Add endpoint：
```
Endpoint URL: https://fengshuilou.com/api/payments/webhook
Events to listen:
  - checkout.session.completed
  - invoice.paid
  - invoice.payment_failed
  - customer.subscription.deleted
```

---

## 7. 香港本地支付方式

Stripe 在香港支持：
- **信用卡**（Visa, Mastercard, Amex）
- **FPS 轉數快**（需 Stripe 額外申請）
- **AlipayHK**（需 Stripe 額外申請）

對於 FPS/AlipayHK，需要在 Stripe Dashboard 申請啟用，並在 `payment_method_types` 中加入。

---

## 8. 實施步驟

1. **註冊 Stripe 賬戶**（1-2 天）
2. **創建產品和價格**（10 分鐘）
3. **設置環境變量**（5 分鐘）
4. **實現後端 API**（2-3 小時）
5. **實現前端訂閱頁**（2-3 小時）
6. **配置 Webhook**（30 分鐘）
7. **測試訂閱流程**（1 小時）
8. **部署上線**（30 分鐘）

**總估計：1-2 天工作量**

---

## 9. 注意事項

- Stripe 在香港的手續費約為 **3.4% + HK$2.35/筆**
- 訂閱首次扣款後 7 天內可申請全額退款（需通過 Stripe API 或 Dashboard 手動處理）
- 務必保存 `stripe_customer_id` 和 `stripe_subscription_id`，用於後續管理
- Webhook 必須驗證簽名，防止偽造請求
- 生產環境使用 `pk_live_` 和 `sk_live_`，測試用 `pk_test_` 和 `sk_test_`
