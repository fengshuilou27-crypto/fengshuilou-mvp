import Link from 'next/link';
import { Compass, Mail, Shield } from 'lucide-react';

const legalLinks = [
  { href: '/disclaimer/', label: '免責聲明' },
  { href: '/privacy/', label: '私隱政策' },
  { href: '/terms/', label: '服務條款' },
];

const featureLinks = [
  { href: '/module1/', label: '自測現有住所' },
  { href: '/module2/', label: '搜尋樓盤' },
  { href: '/module3/', label: '樓盤匹配' },
  { href: '/fxti/', label: 'FXTI 測試' },
];

export function Footer() {
  return (
    <footer className="bg-brand-500 text-brand-200">
      {/* Main Footer */}
      <div className="container-brand py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-gold flex items-center justify-center">
                <Compass className="w-5 h-5 text-brand-900" />
              </div>
              <div>
                <h3 className="text-white font-display font-bold text-lg">風水樓</h3>
                <p className="text-brand-300 text-xs">AI 智能風水樓盤匹配</p>
              </div>
            </div>
            <p className="text-brand-300 text-sm leading-relaxed max-w-xs">
              結合人工智能與傳統風水學，為您找到最匹配的樓盤。八字命理、玄空飛星、八宅風水，一鍵分析。
            </p>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-white font-semibold mb-4">功能</h4>
            <ul className="space-y-2">
              {featureLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-brand-300 hover:text-gold-400 text-sm transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal & Contact */}
          <div>
            <h4 className="text-white font-semibold mb-4">法律與聯繫</h4>
            <ul className="space-y-2 mb-6">
              {legalLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-brand-300 hover:text-gold-400 text-sm transition-colors flex items-center gap-2"
                  >
                    <Shield className="w-3 h-3" />
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
            <div className="flex items-center gap-2 text-brand-300 text-sm">
              <Mail className="w-4 h-4" />
              <span>support@fengshuilou.com</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-brand-400/30">
        <div className="container-brand py-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-brand-300 text-xs">
            © 2026 風水樓. 保留所有權利。
          </p>
          <p className="text-brand-400 text-xs text-center">
            本系統分析結果僅供參考，不構成專業風水意見。
          </p>
        </div>
      </div>
    </footer>
  );
}
