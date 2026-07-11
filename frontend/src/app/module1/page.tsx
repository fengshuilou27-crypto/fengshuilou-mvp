import type { Metadata } from 'next';
import { Construction } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
  title: '自測現有住所 | 風水樓',
  description: '輸入您的出生信息與物業資料，AI 分析現有住所的風水匹配度。',
};

export default function Module1Page() {
  return (
    <div className="bg-paper min-h-screen py-20">
      <div className="container-brand max-w-2xl text-center">
        <Construction className="w-16 h-16 text-gold-500 mx-auto mb-6" />
        <h1 className="heading-display text-3xl mb-4">自測現有住所</h1>
        <p className="text-gray-600 mb-8">
          輸入您的出生信息與物業資料，AI 將分析現有住所的風水匹配度，包括玄空飛星、八宅吉凶、零正神等。
        </p>
        <div className="card-brand p-8 text-left">
          <h3 className="font-display font-semibold text-lg mb-4">功能即將上線</h3>
          <p className="text-gray-600 text-sm mb-4">
            此頁面正在重構中，將遷移至 React + Next.js 架構。目前您仍可使用舊版：
          </p>
          <a
            href="https://fengshuilou.com/module1"
            className="btn-primary inline-flex"
            target="_blank"
            rel="noopener noreferrer"
          >
            使用舊版系統
          </a>
        </div>
      </div>
    </div>
  );
}
