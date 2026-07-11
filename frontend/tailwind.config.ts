import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // 品牌主色系
        brand: {
          50: '#f0f5f1',
          100: '#d9e6dc',
          200: '#b3cdb8',
          300: '#8db394',
          400: '#679a70',
          500: '#1a3c2a',   // 主色：深翡翠綠
          600: '#163624',
          700: '#112d1e',
          800: '#0d2317',
          900: '#081a11',
        },
        // 品牌輔色系 — 金色
        gold: {
          50: '#fdf9f0',
          100: '#f9edd3',
          200: '#f3dba7',
          300: '#edc97b',
          400: '#e7b74f',
          500: '#c9a961',   // 輔色：古金色
          600: '#b89a52',
          700: '#a78b43',
          800: '#967c34',
          900: '#856d25',
        },
        // 吉祥色系
        auspicious: {
          red: '#c41e3a',    // 吉祥紅
          gold: '#c9a961',   // 吉祥金
          jade: '#2d6a4f',   // 翡翠綠
          ink: '#1a1a2e',    // 墨黑
          paper: '#f5f0e8',  // 宣紙白
        },
        // 功能色
        success: '#2d6a4f',
        warning: '#d4a017',
        danger: '#c41e3a',
        info: '#4a90d9',
      },
      fontFamily: {
        display: ['var(--font-noto-serif)', 'serif'],
        body: ['var(--font-noto-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains)', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-brand': 'linear-gradient(135deg, #1a3c2a 0%, #2d6a4f 100%)',
        'gradient-gold': 'linear-gradient(135deg, #c9a961 0%, #e7b74f 100%)',
        'gradient-hero': 'linear-gradient(180deg, #1a3c2a 0%, #0d2317 100%)',
      },
      boxShadow: {
        'card': '0 4px 20px rgba(26, 60, 42, 0.08)',
        'card-hover': '0 8px 32px rgba(26, 60, 42, 0.15)',
        'glow': '0 0 20px rgba(201, 169, 97, 0.3)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 12s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
