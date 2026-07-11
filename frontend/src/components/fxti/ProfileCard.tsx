'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles } from 'lucide-react';
import { FXTI_PROFILES } from '@/lib/fxti-data';
import { cn } from '@/lib/utils';

interface ProfileCardProps {
  profileId: string;
  compact?: boolean;
}

export function ProfileCard({ profileId, compact = false }: ProfileCardProps) {
  const profile = FXTI_PROFILES[profileId];
  if (!profile) return null;

  const isPure = profile.type === 'pure';

  return (
    <Link href={`/fxti/profiles/${profileId}/`} className="block h-full">
      <motion.div
        whileHover={{ y: -4, scale: 1.02 }}
        transition={{ duration: 0.2 }}
        className={cn(
          'h-full rounded-2xl border transition-all duration-300 overflow-hidden',
          'bg-white border-gray-100 hover:border-gold-300 hover:shadow-card-hover',
          compact ? 'p-4' : 'p-5'
        )}
      >
        {/* 頂部色彩條 */}
        <div
          className={cn('h-1.5 rounded-full mb-4', isPure ? 'bg-gradient-to-r' : 'bg-gradient-to-r')}
          style={{
            background: isPure
              ? `linear-gradient(90deg, ${profile.color}, ${profile.colorSecondary})`
              : `linear-gradient(90deg, ${profile.color}, ${profile.colorSecondary})`,
          }}
        />

        {/* 標籤 */}
        <div className="flex items-center gap-2 mb-3">
          <span
            className={cn(
              'px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider',
              isPure ? 'bg-brand-100 text-brand-700' : 'bg-gold-100 text-gold-700'
            )}
          >
            {isPure ? '純格' : '複合格'}
          </span>
          <span className="text-gray-400 text-xs font-mono">{profileId}</span>
        </div>

        {/* 符號與名稱 */}
        <div className="flex items-center gap-3 mb-3">
          <span className="text-3xl">{profile.symbol}</span>
          <div>
            <h3 className="font-display font-semibold text-brand-800 text-lg leading-tight">
              {profile.name}
            </h3>
            <p className="text-gold-600 text-xs font-medium">{profile.title}</p>
          </div>
        </div>

        {/* 五行標籤 */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          {profile.elements.map((element) => (
            <span
              key={element}
              className="px-2 py-0.5 rounded-md text-xs font-medium"
              style={{
                backgroundColor: `${profile.color}15`,
                color: profile.colorSecondary,
              }}
            >
              {element}
            </span>
          ))}
          {profile.interactionType && (
            <span className="px-2 py-0.5 rounded-md text-xs text-gray-500 bg-gray-100">
              {profile.interactionType.split('（')[0]}
            </span>
          )}
        </div>

        {/* 特質 */}
        {!compact && (
          <div className="flex flex-wrap gap-1 mb-3">
            {profile.traits.slice(0, 3).map((trait) => (
              <span
                key={trait}
                className="px-2 py-0.5 rounded-full text-[10px] bg-gray-50 text-gray-600 border border-gray-100"
              >
                {trait}
              </span>
            ))}
          </div>
        )}

        {/* 簡介 */}
        <p className={cn('text-gray-600 text-sm leading-relaxed', compact ? 'line-clamp-2' : 'line-clamp-3')}>
          {profile.description}
        </p>

        {/* 查看詳情 */}
        <div className="mt-4 flex items-center gap-1 text-sm font-medium" style={{ color: profile.colorSecondary }}>
          查看詳情
          <ArrowRight className="w-4 h-4" />
        </div>
      </motion.div>
    </Link>
  );
}
