'use client';

import Link from 'next/link';
import { ArrowRight, Compass } from 'lucide-react';
import { motion } from 'framer-motion';

export function CTA() {
  return (
    <section className="py-20 bg-paper">
      <div className="container-brand">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="card-brand bg-gradient-brand text-white p-10 md:p-16 text-center relative overflow-hidden"
        >
          {/* Decorative */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-gold-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />
          
          <div className="relative z-10">
            <h2 className="font-display font-bold text-2xl md:text-3xl mb-4">
              準備好找到您的理想居所了嗎？
            </h2>
            <p className="text-brand-200 mb-8 max-w-xl mx-auto">
              無論是評估現有住所，還是尋找新樓盤，我們的 AI 風水分析都能為您提供專業參考。
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/module1/" className="btn-gold text-lg px-8 py-4">
                <Compass className="w-5 h-5" />
                立即開始分析
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
