'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-900 text-white">
      <header className="border-b border-slate-700 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-white">AECT-GAN</h1>
          <p className="text-slate-400 text-sm">Adversarial Eulerian CT-GAN for CT synthesis from dual-view X-rays</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            AECT-GAN Paper Results
          </h2>
          <p className="text-slate-400 text-lg max-w-3xl mx-auto leading-relaxed">
            This website presents the qualitative results from our AECT-GAN model,
            trained to reconstruct 3D CT volumes from pairs of dual-view X-ray images.
            Explore the generated CT slices and compare them with ground truth where available.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mt-12">
          {/* Synthetic Trained Model Card */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 hover:border-blue-500 transition-colors">
            <div className="text-blue-400 mb-4">
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-2xl font-semibold mb-3">Synthetic Trained</h3>
            <p className="text-slate-400 mb-6">
              Model trained exclusively on synthetic data generated from real CT volumes.
              View results on both the test set (with ground truth CT) and Indiana University dataset.
            </p>
            <div className="space-y-3">
              <Link href="/synthetic/real-test" className="block w-full text-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">
                Real Test Set
              </Link>
              <Link href="/synthetic/indiana" className="block w-full text-center px-6 py-3 bg-slate-700 text-white font-semibold rounded-lg hover:bg-slate-600 transition-colors">
                Indiana University
              </Link>
            </div>
          </div>

          {/* Mixed Training Model Card */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 hover:border-purple-500 transition-colors">
            <div className="text-purple-400 mb-4">
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 className="text-2xl font-semibold mb-3">Mixed Training</h3>
            <p className="text-slate-400 mb-6">
              Model trained on a combination of synthetic and real data. This approach
              helps bridge the domain gap between synthetic training and real-world X-rays.
            </p>
            <div className="space-y-3">
              <Link href="/mixed/real-test" className="block w-full text-center px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors">
                Real Test Set
              </Link>
              <Link href="/mixed/indiana" className="block w-full text-center px-6 py-3 bg-slate-700 text-white font-semibold rounded-lg hover:bg-slate-600 transition-colors">
                Indiana University
              </Link>
            </div>
          </div>
        </div>

        <div className="mt-16 text-center">
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 max-w-3xl mx-auto">
            <h3 className="text-xl font-semibold mb-4 text-blue-400">About the Datasets</h3>
            <div className="grid md:grid-cols-2 gap-6 text-left">
              <div>
                <h4 className="font-semibold text-slate-300 mb-2">Real Test Set</h4>
                <p className="text-slate-400 text-sm">
                  Contains paired X-rays and reference CT volumes from the LIDC-IDRI dataset.
                  Allows for quantitative comparison between generated and ground truth CTs.
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-slate-300 mb-2">Indiana University</h4>
                <p className="text-slate-400 text-sm">
                  Contains X-rays from the Indiana University chest X-ray dataset.
                  Reference CT volumes are not available; only generated CTs are shown.
                </p>
              </div>
            </div>
          </div>
        </div>
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
