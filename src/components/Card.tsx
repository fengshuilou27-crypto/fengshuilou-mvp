import type { ReactNode } from 'react'

export default function Card({ title, children, sub }: { title: string; children: ReactNode; sub?: string }) {
  return (
    <section className="rounded-xl border border-slate-800 bg-[#0f1729] p-5">
      <h2 className="text-base font-semibold text-white mb-1">{title}</h2>
      {sub && <p className="text-xs text-slate-400 mb-3">{sub}</p>}
      {children}
    </section>
  )
}
