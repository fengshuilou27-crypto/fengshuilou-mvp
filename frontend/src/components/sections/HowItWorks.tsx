'use client';

import { User, Home, BarChart3, FileCheck } from 'lucide-react';
import { motion } from 'framer-motion';

const steps = [
  {
    number: '01',
    icon: User,
    title: '輸入您的信息',
    description: '填寫您的出生日期、時間、性別與職業。系統將自動計算您的八字命理與五行屬性。',
  },
  {
    number: '02',
    icon: Home,
    title: '描述您的目標',
    description: '選擇您的置業目標：財運、健康、事業、桃花或家庭和諧。可設置多個優先級目標。',
  },
  {
    number: '03',
    icon: BarChart3,
    title: 'AI 智能分析',
    description: '系統結合玄空飛星、八宅風水、八字匹配與 GIS 地理分析，計算綜合風水得分。',
  },
  {
    number: '04',
    icon: FileCheck,
    title: '獲取詳細報告',
    description: '查看六維度雷達圖、分項得分、化解建議與 AI 分析說明，助您作出明智決定。',
  },
];

export function HowItWorks() {
  return (
    <section className="py-20 bg-white">
      <div className="container-brand">
        <div className="text-center mb-16">
          <h2 className="heading-section">如何使用</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            四個簡單步驟，即可獲得專業級的風水樓盤分析
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5, delay: index * 0.15 }}
              className="relative"
            >
              <div className="text-center">
                <div className="w-16 h-16 rounded-2xl bg-brand-500 flex items-center justify-center mx-auto mb-4 shadow-lg">
                  <step.icon className="w-8 h-8 text-white" />
                </div>
                <div className="text-gold-500 font-display font-bold text-sm mb-2">
                  步驟 {step.number}
                </div>
                <h3 className="font-display font-semibold text-lg text-brand-800 mb-2">
                  {step.title}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {step.description}
                </p>
              </div>
              
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-8 left-[60%] w-[80%] h-px bg-gradient-to-r from-brand-200 to-transparent" />
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
