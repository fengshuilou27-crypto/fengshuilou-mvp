'use client';

import { motion } from 'framer-motion';
import { ArrowLeft, Compass, Home, Lightbulb, AlertTriangle, Heart } from 'lucide-react';
import Link from 'next/link';
import { FXTI_PROFILES, WUXING_RELATIONS } from '@/lib/fxti-data';
import { cn } from '@/lib/utils';

interface ProfileDetailProps {
  profileId: string;
}

export function ProfileDetail({ profileId }: ProfileDetailProps) {
  const profile = FXTI_PROFILES[profileId];
  if (!profile) return null;

  const isPure = profile.type === 'pure';
  const relationKey = profile.elements.join('');
  const relation = WUXING_RELATIONS[relationKey];

  return (
    <div className="min-h-screen bg-paper">
      {/* 頂部橫幅 */}
      <div
        className="relative py-16 overflow-hidden"
        style={{
          background: `linear-gradient(135deg, ${profile.color}20, ${profile.colorSecondary}30)`,
        }}
      >
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-10 right-20 w-64 h-64 rounded-full blur-3xl" style={{ backgroundColor: `${profile.color}20` }} />
          <div className="absolute bottom-10 left-20 w-48 h-48 rounded-full blur-3xl" style={{ backgroundColor: `${profile.colorSecondary}20` }} />
        </div>

        <div className="container-brand relative z-10">
          <Link href="/fxti/" className="inline-flex items-center gap-2 text-gray-600 hover:text-brand-700 mb-6 transition-colors">
            <ArrowLeft className="w-4 h-4" />
            返回 FXTI 首頁
          </Link>

          <div className="max-w-3xl">
            <div className="flex items-center gap-4 mb-4">
              <span className="text-6xl">{profile.symbol}</span>
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <span
                    className={cn(
                      'px-3 py-1 rounded-full text-xs font-semibold',
                      isPure ? 'bg-brand-100 text-brand-700' : 'bg-gold-100 text-gold-700'
                    )}
                  >
                    {isPure ? '純格' : '複合格'} · {profileId}
                  </span>
                </div>
                <h1 className="heading-display text-4xl md:text-5xl text-brand-900">{profile.name}</h1>
                <p className="text-xl mt-1" style={{ color: profile.colorSecondary }}>{profile.title}</p>
              </div>
            </div>

            {/* 五行標籤 */}
            <div className="flex flex-wrap gap-2 mt-6">
              {profile.elements.map((element) => (
                <span
                  key={element}
                  className="px-4 py-2 rounded-xl text-sm font-semibold text-white"
                  style={{ backgroundColor: profile.color }}
                >
                  {element}行
                </span>
              ))}
              {profile.interactionType && relation && (
                <span className="px-4 py-2 rounded-xl text-sm font-medium bg-white border-2" style={{ borderColor: profile.color, color: profile.colorSecondary }}>
                  {relation.relation} · {relation.description}
                </span>
              )}
              <span className="px-4 py-2 rounded-xl text-sm font-medium bg-white border border-gray-200 text-gray-600 flex items-center gap-1">
                <Compass className="w-4 h-4" />
                吉位：{profile.direction}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 內容區 */}
      <div className="container-brand py-12">
        <div className="max-w-3xl mx-auto">
          {/* 核心描述 */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="card-brand p-8 mb-8"
          >
            <h2 className="font-display font-semibold text-xl text-brand-800 mb-4 flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-gold-500" />
              核心特質
            </h2>
            <p className="text-gray-700 text-lg leading-relaxed mb-6">{profile.description}</p>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {profile.traits.map((trait) => (
                <div
                  key={trait}
                  className="text-center py-3 px-2 rounded-xl text-sm font-medium text-white"
                  style={{ backgroundColor: profile.color }}
                >
                  {trait}
                </div>
              ))}
            </div>
          </motion.section>

          {/* 優勢與弱點 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="card-brand p-6"
            >
              <h2 className="font-display font-semibold text-lg text-success mb-3 flex items-center gap-2">
                <Heart className="w-5 h-5" />
                優勢
              </h2>
              <p className="text-gray-700 leading-relaxed">{profile.strengths}</p>
            </motion.section>

            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="card-brand p-6"
            >
              <h2 className="font-display font-semibold text-lg text-warning mb-3 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                成長空間
              </h2>
              <p className="text-gray-700 leading-relaxed">{profile.weaknesses}</p>
            </motion.section>
          </div>

          {/* 核心矛盾 */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="card-brand p-8 mb-8"
          >
            <h2 className="font-display font-semibold text-xl text-brand-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">☯️</span>
              核心矛盾
            </h2>
            <p className="text-gray-700 text-lg leading-relaxed italic border-l-4 border-gold-400 pl-4">
              {profile.coreContradiction}
            </p>
          </motion.section>

          {/* 風水建議 */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="card-brand p-8 mb-8"
          >
            <h2 className="font-display font-semibold text-xl text-brand-800 mb-4 flex items-center gap-2">
              <Home className="w-5 h-5 text-brand-500" />
              風水居住建議
            </h2>
            <p className="text-gray-700 leading-relaxed">{profile.fengshuiAdvice}</p>
          </motion.section>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="text-center"
          >
            <Link href="/fxti/test/" className="btn-gold text-lg px-8 py-4 inline-flex">
              <span className="text-2xl mr-2">✨</span>
              測試您的五行性格
            </Link>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
