import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '服務條款 | 風水樓',
  description: '風水樓服務條款 — 使用規則、訂閱條款、知識產權與責任限制。',
};

export default function TermsPage() {
  return (
    <div className="bg-paper min-h-screen py-12">
      <div className="container-brand max-w-3xl">
        <div className="bg-white rounded-2xl shadow-card p-8 md:p-12">
          <h1 className="heading-display text-3xl mb-2">服務條款</h1>
          <p className="text-gray-400 text-sm mb-8">Terms of Service</p>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-8 text-sm text-amber-800">
            <strong>請仔細閱讀：</strong> 使用本網站及服務即表示您同意以下條款。如您不同意任何條款，請勿使用本服務。
          </div>

          <div className="space-y-8">
            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">1. 服務概述</h2>
              <p className="text-gray-700 leading-relaxed">
                「風水樓」是由 FengShuiLou Technology Limited 運營的人工智能風水分析工具平台。本服務基於傳統風水理論提供樓盤風水分析功能，僅為信息工具，不構成任何專業意見。詳情請參閱 <a href="/disclaimer/" className="text-brand-600 underline">免責聲明</a>。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">2. 帳戶與註冊</h2>
              <p className="text-gray-700 leading-relaxed">
                註冊時您同意提供準確信息、年滿 18 歲、對帳戶活動負責。我們保留在違反條款時暫停或終止帳戶的權利。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">3. 訂閱與付款</h2>
              <ul className="list-disc list-inside text-gray-700 text-sm space-y-1">
                <li>免費層：基本功能，有限使用次數</li>
                <li>Basic：每月 HK$38，無限制分析 + 進階功能</li>
                <li>Pro：每月 HK$98，完整功能 + 風水師諮詢</li>
              </ul>
              <p className="text-gray-700 text-sm mt-2">
                首次訂閱後 7 天內可申請全額退款。續費後 48 小時內可申請按比例退款。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">4. 知識產權</h2>
              <p className="text-gray-700 leading-relaxed">
                本服務的所有內容受版權、商標等知識產權法律保護。傳統風水知識屬於公共領域，我們的知識產權僅涵蓋算法的具體實現方式。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">5. 責任限制</h2>
              <p className="text-gray-700 leading-relaxed">
                本服務按「現狀」提供。我們的總賠償責任不超過您最近 12 個月內支付的服務費用總額。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">6. 爭議解決</h2>
              <p className="text-gray-700 leading-relaxed">
                本條款受香港法律管轄。任何爭議應首先通過友好協商解決，協商不成提交香港國際仲裁中心（HKIAC）仲裁。
              </p>
            </section>
          </div>

          <div className="mt-12 pt-8 border-t border-gray-200 text-center text-gray-400 text-sm">
            <p>最後更新日期：2026年7月2日</p>
          </div>
        </div>
      </div>
    </div>
  );
}
