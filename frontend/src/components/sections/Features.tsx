'use client';

import { Compass, Search, Scale, BookOpen, Shield, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import Link from 'next/link';

const features = [
  {
    icon: Compass,
    title: '自測現有住所',
    description: '輸入您的出生信息與物業資料，AI 分析現有住所的風水匹配度，包括玄空飛星、八宅吉凶、零正神等。',
    href: '/module1/',
    color: 'bg-blue-50 text-blue-600',
  },
  {
    icon: Search,
    title: '搜尋樓盤',
    description: '瀏覽香港各區樓盤，按坐向、價格、地區篩選，並查看每個樓盤的風水評分與詳細分析。',
    href: '/module2/',
    color: 'bg-green-50 text-green-600',
  },
  {
    icon: Scale,
    title: '智能匹配',
    description: '系統根據您的八字命理與置業目標，自動計算最佳匹配樓盤，並提供目標加權分析。',
    href: '/module3/',
    color: 'bg-purple-50 text-purple-600',
  },
  {
    icon: BookOpen,
    title: 'FXTI 性格測試',
    description: '通過 10 題問卷，結合出生時辰，分析您的五行性格特質，了解最適合您的居住環境。',
    href: '/fxti/',
    color: 'bg-amber-50 text-amber-600',
  },
  {
    icon: Shield,
    title: '煞氣評估',
    description: '自動識別天斬煞、反弓煞、剪刀煞等常見煞氣，並提供具體化解建議與參考價格。',
    href: '/module1/',
    color: 'bg-red-50 text-red-600',
  },
  {
    icon: Zap,
    title: '六維度分析',
    description: '從財運、健康、事業、桃花、家庭和諧、貴人六個維度，全面評估樓盤與您的契合度。',
    href: '/module3/',
    color: 'bg-teal-50 text-teal-600',
  },
];

export function Features() {
  return (
    <section className="py-20 bg-paper">
      <div className="container-brand">
        <div className="text-center mb-16">
          <h2 className="heading-section">核心功能</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            結合多種傳統風水理論與現代 AI 技術，為您提供全面的樓盤分析服務
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Link href={feature.href} className="block h-full">
                <div className="card-brand p-6 h-full hover:-translate-y-1 transition-transform duration-300">
                  <div className={`w-12 h-12 rounded-xl ${feature.color} flex items-center justify-center mb-4`}>
                    <feature.icon className="w-6 h-6" />
                  </div>
                  <h3 className="font-display font-semibold text-lg text-brand-800 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
