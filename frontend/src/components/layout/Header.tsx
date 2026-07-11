'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X, Home, Search, Building2, Scale, BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';

const navLinks = [
  { href: '/', label: '首頁', icon: Home },
  { href: '/module1/', label: '自測住所', icon: Building2 },
  { href: '/module2/', label: '搜尋樓盤', icon: Search },
  { href: '/module3/', label: '樓盤匹配', icon: Scale },
  { href: '/fxti/', label: 'FXTI 測試', icon: BookOpen },
];

export function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-brand-500/95 backdrop-blur-md border-b border-brand-400/30">
      <div className="container-brand">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <img
              src="/logo.svg"
              alt="風水樓"
              className="w-10 h-10 rounded-lg shadow-glow"
              width={40}
              height={40}
            />
            <div className="flex flex-col">
              <span className="text-white font-display font-bold text-lg leading-tight">風水樓</span>
              <span className="text-brand-200 text-[10px] tracking-widest uppercase hidden sm:block">FengShuiLou</span>
            </div>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
                  'text-brand-200 hover:text-white hover:bg-brand-400/50'
                )}
              >
                <link.icon className="w-4 h-4" />
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 rounded-lg text-brand-200 hover:text-white hover:bg-brand-400/50 transition-colors"
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <div
        className={cn(
          'md:hidden overflow-hidden transition-all duration-300',
          mobileOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        )}
      >
        <div className="container-brand pb-4">
          <nav className="flex flex-col gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-3 px-4 py-3 rounded-lg text-brand-200 hover:text-white hover:bg-brand-400/50 transition-colors"
              >
                <link.icon className="w-5 h-5" />
                <span className="font-medium">{link.label}</span>
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}
