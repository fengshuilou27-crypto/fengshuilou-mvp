import type { Metadata } from 'next';
import { ALL_PROFILE_IDS, FXTI_PROFILES } from '@/lib/fxti-data';
import { ProfileDetail } from '@/components/fxti/ProfileDetail';

export function generateStaticParams() {
  return ALL_PROFILE_IDS.map((id) => ({ id }));
}

export function generateMetadata({ params }: { params: { id: string } }): Metadata {
  const profile = FXTI_PROFILES[params.id];
  return {
    title: profile ? `${profile.name} · ${profile.title} | FXTI 五行性格` : '角色詳情 | 風水樓',
    description: profile ? profile.description : 'FXTI 五行性格角色詳情',
  };
}

export default function ProfilePage({ params }: { params: { id: string } }) {
  return <ProfileDetail profileId={params.id} />;
}
