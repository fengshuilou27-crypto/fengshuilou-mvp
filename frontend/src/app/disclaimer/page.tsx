import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '免責聲明 | 風水樓',
  description: '風水樓服務免責聲明 — 使用條款、服務性質、準確性說明與責任限制。',
};

export default function DisclaimerPage() {
  return (
    <div className="bg-paper min-h-screen py-12">
      <div className="container-brand max-w-3xl">
        <div className="bg-white rounded-2xl shadow-card p-8 md:p-12">
          <h1 className="heading-display text-3xl mb-2">免責聲明</h1>
          <p className="text-gray-400 text-sm mb-8">Disclaimer</p>
          
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-8 text-sm text-amber-800">
            <strong>重要提示：</strong> 使用本網站及服務前，請仔細閱讀本免責聲明。使用服務即表示您同意以下條款。
          </div>

          <div className="space-y-8">
            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">1. 服務性質</h2>
              <p className="text-gray-700 leading-relaxed">
                「風水樓」是一個基於人工智能的風水分析工具平台，旨在將傳統風水理論數碼化，為用戶提供便捷的樓盤風水參考信息。本服務僅為信息工具，不構成任何專業意見、投資建議或法律意見。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">2. 非專業意見聲明</h2>
              <p className="text-gray-700 leading-relaxed">
                本系統的分析結果不構成任何專業風水意見。我們強烈建議您在作出任何重大置業決定前，諮詢持牌風水師或相關專業人士。傳統風水學為經驗學問，涉及實地勘察、環境觀察等無法通過軟件完全替代的因素。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">3. 分析準確性</h2>
              <p className="text-gray-700 leading-relaxed">
                人工智能分析可能存在誤差。風水學為經驗學問，不同流派的判斷標準各異。本系統採用的算法和數據僅供參考，不應作為唯一決策依據。實際風水效果受多種因素影響，包括但不限於：建築細節、周邊環境變化、個人運勢波動等。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">4. 數據使用</h2>
              <p className="text-gray-700 leading-relaxed">
                我們重視您的私隱。您提供的個人信息（如出生日期）僅用於風水分析，不會用於其他目的或出售給第三方。詳情請參閱 <a href="/privacy/" className="text-brand-600 underline">私隱政策</a>。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">5. 責任限制</h2>
              <p className="text-gray-700 leading-relaxed">
                在法律允許的最大範圍內，我們不對因使用本服務而導致的任何直接或間接損失承擔責任，包括但不限於：置業決策失誤、投資損失、心理預期落差等。我們的總賠償責任不超過您最近 12 個月內支付的服務費用總額。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">6. 第三方服務</h2>
              <p className="text-gray-700 leading-relaxed">
                本服務可能使用第三方數據（如 Google Maps）。我們不對第三方服務的準確性或可用性負責。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">7. 知識產權</h2>
              <p className="text-gray-700 leading-relaxed">
                本系統的所有內容，包括軟件、算法、界面設計、品牌標識等，均受知識產權法律保護。玄空飛星、八字命理等傳統風水理論屬於公共領域知識。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">8. 變更通知</h2>
              <p className="text-gray-700 leading-relaxed">
                我們保留隨時修改本免責聲明的權利。重大變更將通過網站公告。繼續使用服務即表示接受更新後的條款。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">9. 聯繫我們</h2>
              <p className="text-gray-700 leading-relaxed">
                如有任何問題，請聯繫 support@fengshuilou.com。
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
