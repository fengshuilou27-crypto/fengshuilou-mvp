'use client';

import { motion } from 'framer-motion';

const stats = [
  { value: '24', label: '山向分析', suffix: '種' },
  { value: '9', label: '九宮飛星', suffix: '運' },
  { value: '6', label: '維度評估', suffix: '項' },
  { value: '100', label: '匹配精度', suffix: '%' },
];

export function Stats() {
  return (
    <section className="py-16 bg-brand-500">
      <div className="container-brand">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-display font-bold text-white mb-1">
                {stat.value}
                <span className="text-gold-400 text-2xl">{stat.suffix}</span>
              </div>
              <div className="text-brand-300 text-sm">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
