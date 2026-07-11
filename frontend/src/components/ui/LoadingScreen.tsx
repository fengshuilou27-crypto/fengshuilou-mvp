'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export function LoadingScreen() {
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // 模擬加載進度
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setIsLoading(false), 500);
          return 100;
        }
        // 非線性進度，模擬真實加載
        const increment = prev < 30 ? 5 : prev < 60 ? 8 : prev < 80 ? 3 : prev < 95 ? 1 : 0.5;
        return Math.min(prev + increment, 100);
      });
    }, 80);

    return () => clearInterval(interval);
  }, []);

  return (
    <AnimatePresence>
      {isLoading && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.6, ease: 'easeInOut' }}
          className="fixed inset-0 z-[9999] bg-[#0a0a0a] flex flex-col items-center justify-center"
        >
          {/* Logo 動畫 */}
          <motion.div
            initial={{ scale: 0.3, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{
              duration: 0.8,
              ease: [0.25, 0.46, 0.45, 0.94],
            }}
            className="mb-12"
          >
            <motion.img
              src="/logo.svg"
              alt="風水樓"
              width={80}
              height={80}
              className="w-20 h-20 rounded-2xl"
              animate={{
                scale: [1, 1.05, 1],
                filter: [
                  'drop-shadow(0 0 0px rgba(201,169,97,0))',
                  'drop-shadow(0 0 20px rgba(201,169,97,0.4))',
                  'drop-shadow(0 0 0px rgba(201,169,97,0))',
                ],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          </motion.div>

          {/* 品牌名稱 */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="text-center mb-8"
          >
            <h2 className="font-display text-2xl font-bold text-white tracking-wider">
              風水樓
            </h2>
            <p className="text-[#c9a961] text-sm tracking-[0.3em] uppercase mt-1">
              FengShuiLou
            </p>
          </motion.div>

          {/* 進度條容器 */}
          <div className="w-64 max-w-[80%]">
            {/* 進度條背景 */}
            <div className="h-[3px] bg-gray-800 rounded-full overflow-hidden">
              {/* 進度條填充 */}
              <motion.div
                className="h-full rounded-full"
                style={{
                  background: 'linear-gradient(90deg, #1a3c2a, #c9a961)',
                  width: `${progress}%`,
                }}
                initial={{ width: '0%' }}
                transition={{ duration: 0.1 }}
              />
            </div>

            {/* 進度百分比 */}
            <motion.p
              className="text-center text-gray-600 text-xs mt-3 tracking-wider"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              {Math.round(progress)}%
            </motion.p>
          </div>

          {/* 底部提示 */}
          <motion.p
            className="absolute bottom-8 text-gray-700 text-xs tracking-wider"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.5 }}
          >
            AI 智能風水樓盤分析平台
          </motion.p>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
