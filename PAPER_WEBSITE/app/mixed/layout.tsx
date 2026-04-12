'use client';

import Link from 'next/link';

export default function MixedLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-slate-900 text-white">
      <header className="border-b border-slate-700 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <Link href="/" className="hover:text-purple-400 transition-colors">
              <h1 className="text-2xl font-bold text-white">AECT-GAN</h1>
            </Link>
            <p className="text-slate-400 text-sm">Mixed Training Model</p>
          </div>
          <Link
            href="/"
            className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors text-sm"
          >
            Back to Home
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {children}
      </div>

      <footer className="border-t border-slate-700 mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <p className="text-slate-500 text-sm text-center">
            AECT-GAN — X-Ray to CT reconstruction research
          </p>
        </div>
      </footer>
    </main>
  );
}
