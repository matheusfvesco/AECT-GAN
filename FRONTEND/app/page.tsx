'use client';

import Link from 'next/link';
import { SITE } from '@/src/lib/content';
import { ChartBar, Zap } from 'lucide-react';

export default function Home() {
  const { heroHeading, heroDescription, evaluateCard, predictCard } = SITE.home;

  return (
    <main className="min-h-screen bg-slate-900 text-white">
      <header className="border-b border-slate-700 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-white">{SITE.title}</h1>
          <p className="text-slate-400 text-sm">{SITE.tagline}</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold mb-6 pb-2 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            {heroHeading}
          </h2>
          <p className="text-slate-400 text-lg max-w-3xl mx-auto leading-relaxed">
            {heroDescription}
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mt-12">
          <div className="flex flex-col h-full bg-slate-800 border border-slate-700 rounded-xl p-8 hover:border-blue-500 transition-colors">
              <div className="text-blue-400 mb-4">
                <ChartBar className="w-12 h-12" strokeWidth={2} aria-hidden />
              </div>
            <h3 className="text-2xl font-semibold mb-3">{evaluateCard.title}</h3>
            <p className="text-slate-400 mb-6">{evaluateCard.description}</p>
            <ul className="text-slate-300 text-sm space-y-2 mb-8">
              {evaluateCard.bullets.map((bullet, i) => (
                <li key={i}>- {bullet}</li>
              ))}
            </ul>
            <Link href="/evaluate" className="block w-full text-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">
              {evaluateCard.button}
            </Link>
          </div>

          <div className="flex flex-col h-full bg-slate-800 border border-slate-700 rounded-xl p-8 hover:border-purple-500 transition-colors">
            <div className="text-purple-400 mb-4">
              <Zap className="w-12 h-12" strokeWidth={2} aria-hidden />
            </div>
            <h3 className="text-2xl font-semibold mb-3">{predictCard.title}</h3>
            <p className="text-slate-400 mb-6">{predictCard.description}</p>
            <ul className="text-slate-300 text-sm space-y-2 mb-8">
              {predictCard.bullets.map((bullet, i) => (
                <li key={i}>- {bullet}</li>
              ))}
            </ul>
            <Link href="/predict" className="block w-full text-center px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors">
              {predictCard.button}
            </Link>
          </div>
        </div>
      </div>

      <footer className="border-t border-slate-700 mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <p className="text-slate-500 text-sm text-center">{SITE.footer.privacy}</p>
          <p className="text-slate-600 text-xs text-center mt-1">{SITE.footer.clinical}</p>
        </div>
      </footer>
    </main>
  );
}
