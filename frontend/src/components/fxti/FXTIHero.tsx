'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, Users } from 'lucide-react';
import { ALL_PROFILE_IDS, FXTI_PROFILES } from '@/lib/fxti-data';
import { ProfileCard } from '@/components/fxti/ProfileCard';

export function FXTIHero() {
  return (
    <section className="relative bg-gradient-hero overflow-hidden">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-gold-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-brand-400/10 rounded-full blur-3xl" />
      </div>

      <div className="container-brand relative z-10 py-20 lg:py-28">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gold-500/10 border border-gold-500/20 text-gold-400 text-sm font-medium mb-8"
          >
            <Sparkles className="w-4 h-4" />
            FXTI 五行性格測試
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="heading-display text-4xl md:text-5xl text-white mb-6"
          >
            探索您的<span className="text-gold-400">五行性格</span>原型
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-brand-200 text-lg leading-relaxed mb-10 max-w-2xl mx-auto"
          >
            通過 10 題專業問卷，結合您的出生時辰，分析您的五行性格特質。
            了解您的優勢、成長方向，以及最適合的居住環境。
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link href="/fxti/test/" className="btn-gold text-lg px-8 py-4">
              <Sparkles className="w-5 h-5" />
              開始測試
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href="#profiles" className="btn-primary text-lg px-8 py-4">
              <Users className="w-5 h-5" />
              瀏覽 15 種原型
            </Link>
          </motion.div>
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 80" fill="none" className="w-full">
          <path d="M0 80V40C240 80 480 0 720 0C960 0 1200 80 1440 40V80H0Z" fill="#f5f0e8" />
        </svg>
      </div>
    </section>
  );
}

export function ProfileGrid() {
  return (
    <section id="profiles" className="py-20 bg-paper">
      <div className="container-brand">
        <div className="text-center mb-16">
          <h2 className="heading-section">15 種五行性格原型</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            每個人都有獨特的五行組合。了解這些原型，幫助您認識自己，找到最適合的居住環境。
          </p>
        </div>

        {/* 純格 */}
        <div className="mb-16">
          <h3 className="font-display font-semibold text-xl text-brand-800 mb-2 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-gold-400" />
            純格原型（5 種）
          </h3>
          <p className="text-gray-500 text-sm mb-6">單一五行主導，性格特質鮮明</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {['A1', 'A2', 'A3', 'A4', 'A5'].map((id, index) => (
              <motion.div
                key={id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <ProfileCard profileId={id} />
              </motion.div>
            ))}
          </div>
        </div>

        {/* 複合格 */}
        <div>
          <h3 className="font-display font-semibold text-xl text-brand-800 mb-2 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-brand-400" />
            複合格原型（10 種）
          </h3>
          <p className="text-gray-500 text-sm mb-6">兩種五行交互，性格更為立體多元</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10'].map((id, index) => (
              <motion.div
                key={id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.08 }}
              >
                <ProfileCard profileId={id} />
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
