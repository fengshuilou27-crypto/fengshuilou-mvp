'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { X } from 'lucide-react';
import Link from 'next/link';

interface DisclaimerContextType {
  accepted: boolean;
  accept: () => void;
}

const DisclaimerContext = createContext<DisclaimerContextType | undefined>(undefined);

export function useDisclaimer() {
  const context = useContext(DisclaimerContext);
  if (!context) throw new Error('useDisclaimer must be used within DisclaimerProvider');
  return context;
}

export function DisclaimerProvider({ children }: { children: ReactNode }) {
  const [accepted, setAccepted] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('fengshuiDisclaimerAccepted');
    setAccepted(stored === 'true');
    setMounted(true);
  }, []);

  const accept = () => {
    localStorage.setItem('fengshuiDisclaimerAccepted', 'true');
    setAccepted(true);
  };

  if (!mounted) return <>{children}</>;

  return (
    <DisclaimerContext.Provider value={{ accepted, accept }}>
      {children}
      {!accepted && <DisclaimerModal onAccept={accept} />}
    </DisclaimerContext.Provider>
  );
}

function DisclaimerModal({ onAccept }: { onAccept: () => void }) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="heading-section text-xl mb-0">⚠️ 重要聲明</h2>
          </div>
          
          <div className="space-y-4 text-sm text-gray-700 leading-relaxed">
            <p>
              <strong className="text-brand-700">本服務性質：</strong>
              「風水樓」是一個基於人工智能的風水分析工具，旨在將傳統風水理論數碼化，為用戶提供便捷的樓盤風水參考信息。
            </p>
            <p>
              <strong className="text-brand-700">非專業意見：</strong>
              本系統的分析結果不構成任何專業風水意見、投資建議或法律意見。我們強烈建議您在作出任何重大置業決定前，諮詢持牌風水師或相關專業人士。
            </p>
            <p>
              <strong className="text-brand-700">分析準確性：</strong>
              人工智能分析可能存在誤差。風水學為經驗學問，不同流派的判斷標準各異。本系統採用的算法和數據僅供參考。
            </p>
            <p>
              <strong className="text-brand-700">使用風險：</strong>
              使用本服務即表示您了解並接受上述限制。對於因使用本服務而導致的任何損失，我們不承擔法律責任。
            </p>
          </div>

          <div className="mt-6 flex flex-col sm:flex-row gap-3">
            <button
              onClick={onAccept}
              className="btn-primary flex-1"
            >
              我已了解並同意
            </button>
            <Link
              href="/disclaimer/"
              className="btn-secondary flex-1 text-center"
            >
              查看完整聲明
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
