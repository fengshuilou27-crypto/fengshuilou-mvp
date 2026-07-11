import type { Metadata } from 'next';
import { Noto_Sans_TC, Noto_Serif_TC } from 'next/font/google';
import './globals.css';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { DisclaimerProvider } from '@/components/providers/DisclaimerProvider';

const notoSans = Noto_Sans_TC({
  subsets: ['latin'],
  weight: ['300', '400', '500', '700'],
  variable: '--font-noto-sans',
  display: 'swap',
});

const notoSerif = Noto_Serif_TC({
  subsets: ['latin'],
  weight: ['400', '600', '700'],
  variable: '--font-noto-serif',
  display: 'swap',
});

export const metadata: Metadata = {
  title: '風水樓 — AI 智能風水樓盤匹配平台',
  description: '結合人工智能與傳統風水學，為您找到最匹配的樓盤。八字命理、玄空飛星、八宅風水，一鍵分析。',
  keywords: ['風水', '樓盤', '置業', '八字', '玄空飛星', '八宅', '香港', 'AI風水'],
  authors: [{ name: '風水樓' }],
  openGraph: {
    title: '風水樓 — AI 智能風水樓盤匹配',
    description: '結合人工智能與傳統風水學，為您找到最匹配的樓盤',
    type: 'website',
    locale: 'zh_HK',
  },
  icons: {
    icon: '/favicon.svg',
    apple: '/apple-touch-icon.png',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-HK" className={`${notoSans.variable} ${notoSerif.variable}`}>
      <body className="font-body bg-paper text-ink min-h-screen antialiased">
        <DisclaimerProvider>
          <Header />
          <main>{children}</main>
          <Footer />
        </DisclaimerProvider>
      </body>
    </html>
  );
}
