import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '私隱政策 | 風水樓',
  description: '風水樓私隱政策 — 了解我們如何收集、使用和保護您的個人數據。',
};

export default function PrivacyPage() {
  return (
    <div className="bg-paper min-h-screen py-12">
      <div className="container-brand max-w-3xl">
        <div className="bg-white rounded-2xl shadow-card p-8 md:p-12">
          <h1 className="heading-display text-3xl mb-2">私隱政策</h1>
          <p className="text-gray-400 text-sm mb-2">Privacy Policy</p>
          <p className="text-green-700 text-sm bg-green-50 rounded-lg p-3 mb-8">
            最後更新日期：2026年7月2日
          </p>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8 text-sm text-blue-800">
            <strong>簡要說明：</strong> 我們非常重視您的私隱。本系統收集的個人數據僅用於風水分析，不會出售予第三方。我們採用業界標準的加密措施保護您的數據。您可以選擇匿名使用，或隨時要求刪除您的數據。
          </div>

          <div className="space-y-8">
            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">1. 我們是誰</h2>
              <p className="text-gray-700 leading-relaxed">
                「風水樓」是一個基於人工智能的風水樓盤分析平台，由 FengShuiLou Technology Limited（註冊地：香港）運營。我們致力於將傳統風水學與現代科技結合，為用戶提供便捷的樓盤風水分析工具。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">2. 我們收集什麼數據</h2>
              <div className="overflow-x-auto mt-4">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-200 p-2 text-left">數據類型</th>
                      <th className="border border-gray-200 p-2 text-left">具體內容</th>
                      <th className="border border-gray-200 p-2 text-left">用途</th>
                      <th className="border border-gray-200 p-2 text-left">是否必填</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-gray-200 p-2">個人基本資料</td>
                      <td className="border border-gray-200 p-2">出生日期</td>
                      <td className="border border-gray-200 p-2">八字命理分析</td>
                      <td className="border border-gray-200 p-2">必填</td>
                    </tr>
                    <tr className="bg-gray-50">
                      <td className="border border-gray-200 p-2">出生時間</td>
                      <td className="border border-gray-200 p-2">時、分</td>
                      <td className="border border-gray-200 p-2">精確四柱排盤</td>
                      <td className="border border-gray-200 p-2">可選</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-200 p-2">性別</td>
                      <td className="border border-gray-200 p-2">男/女</td>
                      <td className="border border-gray-200 p-2">八字陰陽分析</td>
                      <td className="border border-gray-200 p-2">必填</td>
                    </tr>
                    <tr className="bg-gray-50">
                      <td className="border border-gray-200 p-2">職業</td>
                      <td className="border border-gray-200 p-2">職業類型</td>
                      <td className="border border-gray-200 p-2">五行屬性匹配</td>
                      <td className="border border-gray-200 p-2">可選</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-200 p-2">同住人信息</td>
                      <td className="border border-gray-200 p-2">出生日期、性別</td>
                      <td className="border border-gray-200 p-2">雙人模式分析</td>
                      <td className="border border-gray-200 p-2">可選</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">3. 數據存儲與安全</h2>
              <p className="text-gray-700 leading-relaxed mb-2">
                您的數據存儲於 Neon Serverless Postgres（新加坡數據中心），符合新加坡及香港的數據保護法規。
              </p>
              <ul className="list-disc list-inside text-gray-700 text-sm space-y-1">
                <li>傳輸加密：所有數據通過 HTTPS（TLS 1.3）傳輸</li>
                <li>存儲加密：數據庫使用 AES-256 加密</li>
                <li>匿名分析：分析結果保存 30 天後自動刪除</li>
                <li>註冊用戶數據：保存至帳戶註銷或用戶要求刪除</li>
              </ul>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">4. 您的權利</h2>
              <p className="text-gray-700 leading-relaxed">
                根據香港《個人資料（私隱）條例》，您享有查閱、更正、刪除、限制處理、數據可攜和反對的權利。行使權利請發送電郵至 privacy@fengshuilou.com，我們將在 30 天內回覆。
              </p>
            </section>

            <section>
              <h2 className="font-display font-semibold text-xl text-brand-800 mb-3 border-b-2 border-gold-400 pb-2">5. 聯繫我們</h2>
              <p className="text-gray-700 leading-relaxed">
                資料保護主任：privacy@fengshuilou.com
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
