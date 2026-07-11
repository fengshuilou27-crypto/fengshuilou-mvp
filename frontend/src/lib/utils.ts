import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatScore(score: number): string {
  return Math.round(score).toString();
}

export function getScoreColor(score: number): string {
  if (score >= 80) return '#2d6a4f';
  if (score >= 60) return '#d4a017';
  if (score >= 40) return '#e67e22';
  return '#c41e3a';
}

export function getScoreLabel(score: number): string {
  if (score >= 85) return '極佳';
  if (score >= 70) return '良好';
  if (score >= 55) return '中等';
  if (score >= 40) return '一般';
  return '不佳';
}

export function getScoreClass(score: number): string {
  if (score >= 80) return 'text-success';
  if (score >= 60) return 'text-warning';
  if (score >= 40) return 'text-orange-500';
  return 'text-danger';
}
