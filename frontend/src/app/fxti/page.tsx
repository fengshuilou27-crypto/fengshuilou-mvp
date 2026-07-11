import type { Metadata } from 'next';
import { FXTIHero, ProfileGrid } from '@/components/fxti/FXTIHero';

export const metadata: Metadata = {
  title: 'FXTI 五行性格測試 | 風水樓',
  description: '探索 15 種五行性格原型，了解您的優勢、成長方向與最適合的居住環境。',
};

export default function FXTIPage() {
  return (
    <>
      <FXTIHero />
      <ProfileGrid />
    </>
  );
}
