'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft, Sparkles, RotateCcw } from 'lucide-react';
import Link from 'next/link';
import { determineProfile, synthesizeResult } from '@/lib/fxti-data';

// 10 題 FXTI 問卷
const QUESTIONS = [
  {
    id: 1,
    question: '當面臨重大決定時，您通常會：',
    options: [
      { text: '仔細分析利弊，尋找最優解', score: { 金: 3, 木: 0, 水: 1, 火: 0, 土: 1 } },
      { text: '聽從直覺，快速決定', score: { 金: 0, 木: 1, 水: 2, 火: 3, 土: 0 } },
      { text: '徵求他人意見，綜合考慮', score: { 金: 1, 木: 1, 水: 3, 火: 0, 土: 2 } },
      { text: '尋找創新方案，突破框架', score: { 金: 0, 木: 3, 水: 1, 火: 1, 土: 0 } },
      { text: '穩步規劃，確保萬無一失', score: { 金: 2, 木: 0, 水: 0, 火: 0, 土: 3 } },
    ],
  },
  {
    id: 2,
    question: '您最喜歡的休閒方式是：',
    options: [
      { text: '閱讀、學習新知識', score: { 金: 2, 木: 1, 水: 3, 火: 0, 土: 0 } },
      { text: '戶外運動、探索自然', score: { 金: 0, 木: 3, 水: 1, 火: 2, 土: 0 } },
      { text: '與朋友聚會、社交活動', score: { 金: 0, 木: 1, 水: 2, 火: 3, 土: 1 } },
      { text: '靜坐冥想、獨處思考', score: { 金: 1, 木: 0, 水: 3, 火: 0, 土: 2 } },
      { text: '整理家務、規劃未來', score: { 金: 2, 木: 0, 水: 0, 火: 0, 土: 3 } },
    ],
  },
  {
    id: 3,
    question: '在團隊中，您通常扮演什麼角色？',
    options: [
      { text: '領導者，帶領團隊前進', score: { 金: 2, 木: 1, 水: 0, 火: 3, 土: 0 } },
      { text: '創意者，提出新點子', score: { 金: 0, 木: 3, 水: 1, 火: 1, 土: 0 } },
      { text: '協調者，化解矛盾', score: { 金: 1, 木: 0, 水: 3, 火: 0, 土: 2 } },
      { text: '執行者，確保任務完成', score: { 金: 3, 木: 0, 水: 0, 火: 1, 土: 2 } },
      { text: '支持者，穩定團隊情緒', score: { 金: 0, 木: 1, 水: 1, 火: 0, 土: 3 } },
    ],
  },
  {
    id: 4,
    question: '您最看重的工作環境特質是：',
    options: [
      { text: '秩序井然、規則明確', score: { 金: 3, 木: 0, 水: 0, 火: 0, 土: 2 } },
      { text: '自由開放、允許創新', score: { 金: 0, 木: 3, 水: 1, 火: 2, 土: 0 } },
      { text: '人際和諧、溝通順暢', score: { 金: 0, 木: 1, 水: 3, 火: 1, 土: 1 } },
      { text: '充滿挑戰、能展現自我', score: { 金: 1, 木: 1, 水: 0, 火: 3, 土: 0 } },
      { text: '穩定安全、有保障', score: { 金: 1, 木: 0, 水: 0, 火: 0, 土: 3 } },
    ],
  },
  {
    id: 5,
    question: '面對壓力時，您的反應是：',
    options: [
      { text: '冷靜分析，尋找解決方案', score: { 金: 3, 木: 0, 水: 2, 火: 0, 土: 1 } },
      { text: '積極行動，快速處理', score: { 金: 1, 木: 2, 水: 0, 火: 3, 土: 0 } },
      { text: '尋求支持，與人傾訴', score: { 金: 0, 木: 0, 水: 3, 火: 1, 土: 2 } },
      { text: '暫時逃避，等待時機', score: { 金: 0, 木: 1, 水: 2, 火: 0, 土: 0 } },
      { text: '按部就班，穩步解決', score: { 金: 2, 木: 0, 水: 0, 火: 0, 土: 3 } },
    ],
  },
  {
    id: 6,
    question: '您最理想的居住環境是：',
    options: [
      { text: '現代簡約、功能齊全', score: { 金: 3, 木: 0, 水: 1, 火: 0, 土: 1 } },
      { text: '綠意盎然、貼近自然', score: { 金: 0, 木: 3, 水: 1, 火: 0, 土: 2 } },
      { text: '臨水而居、視野開闊', score: { 金: 0, 木: 1, 水: 3, 火: 0, 土: 1 } },
      { text: '明亮開闊、朝陽充足', score: { 金: 1, 木: 1, 水: 0, 火: 3, 土: 0 } },
      { text: '方正穩重、厚實安全', score: { 金: 1, 木: 0, 水: 0, 火: 0, 土: 3 } },
    ],
  },
  {
    id: 7,
    question: '與人發生衝突時，您傾向於：',
    options: [
      { text: '據理力爭，堅持原則', score: { 金: 3, 木: 0, 水: 0, 火: 2, 土: 0 } },
      { text: '尋求共識，創造雙贏', score: { 金: 0, 木: 2, 水: 2, 火: 0, 土: 1 } },
      { text: '退讓迴避，避免爭執', score: { 金: 0, 木: 0, 水: 3, 火: 0, 土: 2 } },
      { text: '直接表達，不藏心事', score: { 金: 1, 木: 1, 水: 0, 火: 3, 土: 0 } },
      { text: '耐心溝通，慢慢化解', score: { 金: 0, 木: 0, 水: 1, 火: 0, 土: 3 } },
    ],
  },
  {
    id: 8,
    question: '您的理財觀念是：',
    options: [
      { text: '精打細算，嚴格預算', score: { 金: 3, 木: 0, 水: 0, 火: 0, 土: 2 } },
      { text: '敢於投資，追求成長', score: { 金: 0, 木: 3, 水: 1, 火: 2, 土: 0 } },
      { text: '靈活變通，順勢而為', score: { 金: 1, 木: 1, 水: 3, 火: 0, 土: 1 } },
      { text: '大手大腳，享受當下', score: { 金: 0, 木: 0, 水: 1, 火: 3, 土: 0 } },
      { text: '穩健儲蓄，長遠規劃', score: { 金: 2, 木: 0, 水: 0, 火: 0, 土: 3 } },
    ],
  },
  {
    id: 9,
    question: '您描述自己為：',
    options: [
      { text: '完美主義者', score: { 金: 3, 木: 0, 水: 0, 火: 0, 土: 1 } },
      { text: '夢想家', score: { 金: 0, 木: 3, 水: 1, 火: 1, 土: 0 } },
      { text: '觀察者', score: { 金: 1, 木: 0, 水: 3, 火: 0, 土: 1 } },
      { text: '行動派', score: { 金: 0, 木: 1, 水: 0, 火: 3, 土: 0 } },
      { text: '可靠夥伴', score: { 金: 0, 木: 0, 水: 1, 火: 0, 土: 3 } },
    ],
  },
  {
    id: 10,
    question: '面對變化，您的態度是：',
    options: [
      { text: '謹慎評估，逐步適應', score: { 金: 3, 木: 0, 水: 1, 火: 0, 土: 2 } },
      { text: '興奮期待，主動擁抱', score: { 金: 0, 木: 3, 水: 1, 火: 2, 土: 0 } },
      { text: '靜觀其變，順其自然', score: { 金: 0, 木: 1, 水: 3, 火: 0, 土: 1 } },
      { text: '帶領變革，成為先驅', score: { 金: 1, 木: 2, 水: 0, 火: 3, 土: 0 } },
      { text: '希望穩定，抗拒改變', score: { 金: 1, 木: 0, 水: 0, 火: 0, 土: 3 } },
    ],
  },
];

export default function FXTITestPage() {
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [result, setResult] = useState<ReturnType<typeof determineProfile> | null>(null);
  const [showResult, setShowResult] = useState(false);

  const handleAnswer = (optionIndex: number) => {
    const newAnswers = { ...answers, [currentQ]: optionIndex };
    setAnswers(newAnswers);

    if (currentQ < QUESTIONS.length - 1) {
      setCurrentQ(currentQ + 1);
    } else {
      // 計算結果
      const acquiredScore: Record<string, number> = { 金: 0, 木: 0, 水: 0, 火: 0, 土: 0 };
      Object.entries(newAnswers).forEach(([qIdx, optIdx]) => {
        const question = QUESTIONS[parseInt(qIdx)];
        const option = question.options[optIdx];
        Object.entries(option.score).forEach(([element, score]) => {
          acquiredScore[element] += score;
        });
      });

      // 轉換為百分比
      const total = Object.values(acquiredScore).reduce((a, b) => a + b, 0);
      const acquiredPct: Record<string, number> = {};
      Object.entries(acquiredScore).forEach(([element, score]) => {
        acquiredPct[element] = Math.round((score / total) * 10000) / 100;
      });

      // 簡化：假設先天均等（實際應根據出生時辰計算）
      const innatePct = { 金: 20, 木: 20, 水: 20, 火: 20, 土: 20 };
      const finalPct = synthesizeResult(innatePct, acquiredPct, 0.3, 0.7);
      const profile = determineProfile(finalPct, 25, 15);
      setResult(profile);
      setShowResult(true);
    }
  };

  const handleBack = () => {
    if (currentQ > 0) setCurrentQ(currentQ - 1);
  };

  const handleRestart = () => {
    setCurrentQ(0);
    setAnswers({});
    setResult(null);
    setShowResult(false);
  };

  const progress = ((currentQ + 1) / QUESTIONS.length) * 100;

  if (showResult && result) {
    return (
      <div className="min-h-screen bg-paper py-12">
        <div className="container-brand max-w-2xl">
          <div className="card-brand p-8 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, damping: 20 }}
            >
              <span className="text-6xl">{result.symbol}</span>
            </motion.div>

            <h1 className="heading-display text-3xl mt-4 mb-2">
              您是 <span style={{ color: result.color }}>{result.name}</span>
            </h1>
            <p className="text-xl text-gold-600 mb-6">{result.title}</p>

            <p className="text-gray-700 leading-relaxed mb-8">{result.description}</p>

            {/* 五行分佈 */}
            <div className="bg-gray-50 rounded-xl p-4 mb-6">
              <h3 className="font-semibold text-brand-800 mb-3">五行分佈</h3>
              {Object.entries(result.allPercentages || {}).sort((a, b) => b[1] - a[1]).map(([element, pct]) => (
                <div key={element} className="flex items-center gap-3 mb-2">
                  <span className="w-8 text-sm font-medium">{element}</span>
                  <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ duration: 1, delay: 0.3 }}
                      className="h-full rounded-full"
                      style={{ backgroundColor: result.color }}
                    />
                  </div>
                  <span className="w-12 text-right text-sm">{pct}%</span>
                </div>
              ))}
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href={`/fxti/profiles/${result.id}/`} className="btn-primary">
                查看完整分析
                <ArrowRight className="w-4 h-4" />
              </Link>
              <button onClick={handleRestart} className="btn-secondary">
                <RotateCcw className="w-4 h-4" />
                重新測試
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const question = QUESTIONS[currentQ];

  return (
    <div className="min-h-screen bg-paper py-12">
      <div className="container-brand max-w-2xl">
        {/* 進度條 */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-500 mb-2">
            <span>問題 {currentQ + 1} / {QUESTIONS.length}</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-brand-500 to-gold-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={currentQ}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
            className="card-brand p-8"
          >
            <h2 className="font-display font-semibold text-xl text-brand-800 mb-6">
              {question.question}
            </h2>

            <div className="space-y-3">
              {question.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleAnswer(index)}
                  className="w-full text-left p-4 rounded-xl border-2 border-gray-100 hover:border-gold-400 hover:bg-gold-50 transition-all duration-200 flex items-center gap-3"
                >
                  <span className="w-8 h-8 rounded-lg bg-gray-100 text-gray-600 font-semibold text-sm flex items-center justify-center shrink-0">
                    {String.fromCharCode(65 + index)}
                  </span>
                  <span className="text-gray-700">{option.text}</span>
                </button>
              ))}
            </div>

            {currentQ > 0 && (
              <button
                onClick={handleBack}
                className="mt-6 text-gray-500 hover:text-brand-700 flex items-center gap-2 text-sm transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                上一題
              </button>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
