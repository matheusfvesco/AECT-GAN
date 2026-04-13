'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-900 text-white">
      <header className="border-b border-slate-700 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-white">AECT-GAN</h1>
          <p className="text-slate-400 text-sm">Addressing Domain Shift in Dual-View X-ray to CT Reconstruction</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold mb-6 pb-2 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Reconstruct CT from X-Rays
          </h2>
          <p className="text-slate-400 text-lg max-w-3xl mx-auto leading-relaxed">
            We use AECT-GAN (Cheng et al.) to explore the Domain Shift in Dual-View X-ray to CT Reconstruction when using Real X-rays as inputs. Use Evaluate to compare against a provided reference CT volume, or Predict for inference only.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mt-12">
          {/* Evaluate Card */}
          <div className="flex flex-col h-full bg-slate-800 border border-slate-700 rounded-xl p-8 hover:border-blue-500 transition-colors">
            <div className="text-blue-400 mb-4">
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-2xl font-semibold mb-3">Evaluate</h3>
            <p className="text-slate-400 mb-6">
              Upload DICOM files (CT scan + X-rays) to evaluate model performance with full metrics.
            </p>
            <ul className="text-slate-300 text-sm space-y-2 mb-8">
              <li>- Requires CT scan + X-rays</li>
              <li>- Returns evaluation metrics</li>
              <li>- Compares generated vs original CT</li>
            </ul>
            <Link href="/evaluate" className="block w-full text-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">
              Go to Evaluate
            </Link>
          </div>

          {/* Predict Card */}
          <div className="flex flex-col h-full bg-slate-800 border border-slate-700 rounded-xl p-8 hover:border-purple-500 transition-colors">
            <div className="text-purple-400 mb-4">
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-2xl font-semibold mb-3">Predict</h3>
            <p className="text-slate-400 mb-6">
              Upload X-ray images (DICOM or JPEG/PNG) to generate a CT volume without metrics.
            </p>
            <ul className="text-slate-300 text-sm space-y-2 mb-8">
              <li>- Accepts 2 X-ray files</li>
              <li>- No metrics calculation</li>
              <li>- Faster inference</li>
            </ul>
            <Link href="/predict" className="block w-full text-center px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors">
              Go to Predict
            </Link>
          </div>
        </div>
      </div>

      <footer className="border-t border-slate-700 mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <p className="text-slate-500 text-sm text-center">
            AECT-GAN Playground — Ephemeral processing. No data is stored.
          </p>
        </div>
      </footer>
    </main>
  );
}
