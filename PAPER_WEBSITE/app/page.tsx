"use client";

import Link from 'next/link';
import { Activity, Blend, Hospital } from 'lucide-react';
import BrandIcon from '@/components/BrandIcon';

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
            AECT-GAN Paper Results
          </h2>
          <p className="text-slate-400 text-lg max-w-3xl mx-auto leading-relaxed">
            We use AECT-GAN (Cheng et al.) to explore the Domain Shift in Dual-View X-ray to CT Reconstruction when using Real X-rays as inputs. Explore the generated CT slices from models trained on synthetic, mixed, and real data variants and compare them with ground truth where available.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mt-12">
          {/* Synthetic Trained Model Card */}
          <div className="flex flex-col h-full bg-slate-800 border border-slate-700 rounded-xl p-8 hover:border-blue-500 transition-colors">
            <div className="text-blue-400 mb-4">
              <BrandIcon Icon={Activity} className="text-blue-400" />
            </div>
            <h3 className="text-2xl font-semibold mb-3">Synthetic Trained</h3>
<p className="text-slate-400 mb-6 flex-grow">
              Model trained exclusively on synthetic data derived from real CT volumes. View
              outputs on three datasets: the Real Test Set (20 patients with real X-rays as
              inputs and paired reference CTs), the Model Test Set (222 samples with
              synthetic X-ray inputs and paired reference CTs), and the Indiana University
              dataset (3,405 external clinical X-ray studies; no ground-truth CTs).
            </p>
            <div className="space-y-3">
              <Link href="/synthetic/real-test" className="block w-full text-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">
                Real Test Set
              </Link>
              <Link href="/synthetic/indiana" className="block w-full text-center px-6 py-3 bg-slate-700 text-white font-semibold rounded-lg hover:bg-slate-600 transition-colors">
                Indiana University
              </Link>
              <Link href="/synthetic/test" className="block w-full text-center px-6 py-3 bg-slate-700 text-white font-semibold rounded-lg hover:bg-slate-600 transition-colors">
                Synthetic Test Set
              </Link>
            </div>
          </div>

          {/* Mixed Training Model Card */}
          <div className="flex flex-col h-full bg-slate-800 border border-slate-700 rounded-xl p-8 hover:border-purple-500 transition-colors">
            <div className="text-purple-400 mb-4">
              <BrandIcon Icon={Blend} className="text-purple-400" />
            </div>
            <h3 className="text-2xl font-semibold mb-3">Mixed Training</h3>
            <p className="text-slate-400 mb-6 flex-grow">
              Model trained on a combination of synthetic and real X-rays to bridge the
              domain gap. View outputs on three datasets: the Real Test Set (20 patients
              with real X-rays and paired reference CTs), the Model Test Set (222 samples -
              includes synthetic versions of the same 20 real-X-ray cases plus additional
              synthetic cases, all with paired reference CTs), and the Indiana University
              dataset (3,405 external clinical X-ray studies; no ground-truth CTs).
            </p>
            <div className="space-y-3">
              <Link href="/mixed/real-test" className="block w-full text-center px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors">
                Real Test Set
              </Link>
              <Link href="/mixed/indiana" className="block w-full text-center px-6 py-3 bg-slate-700 text-white font-semibold rounded-lg hover:bg-slate-600 transition-colors">
                Indiana University
              </Link>
              <Link href="/mixed/test" className="block w-full text-center px-6 py-3 bg-slate-700 text-white font-semibold rounded-lg hover:bg-slate-600 transition-colors">
                Mixed Test Set
              </Link>
            </div>
          </div>

          {/* Real Trained Model Card */}
          <div className="flex flex-col h-full bg-slate-800 border border-slate-700 rounded-xl p-8 hover:border-green-500 transition-colors">
            <div className="text-green-400 mb-4">
              <BrandIcon Icon={Hospital} className="text-green-400" />
            </div>
            <h3 className="text-2xl font-semibold mb-3">Real Trained</h3>
            <p className="text-slate-400 mb-6 flex-grow">
              Model trained exclusively on real patient X-rays. View outputs on the Real
              Test Set (20 patients with paired reference CTs) and on the Indiana
              University dataset (3,405 external clinical X-ray studies; no ground-truth
              CTs). This approach may generalize better to clinical data, producing more
              plausible results.
            </p>
            <div className="space-y-3">
              <Link href="/real/real-test" className="block w-full text-center px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors">
                Real Test Set
              </Link>
              <Link href="/real/indiana" className="block w-full text-center px-6 py-3 bg-slate-700 text-white font-semibold rounded-lg hover:bg-slate-600 transition-colors">
                Indiana University
              </Link>
              <div aria-hidden="true" className="invisible block w-full px-6 py-3 font-semibold rounded-lg">
                &nbsp;
              </div>
            </div>
          </div>
        </div>

        <div className="mt-16 text-center">
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 max-w-3xl mx-auto">
            <h3 className="text-xl font-semibold mb-4 text-blue-400">About the Datasets</h3>
            <div className="grid md:grid-cols-3 gap-6 text-left">
              <div>
                <h4 className="font-semibold text-slate-300 mb-2">Real Test Set</h4>
                <p className="text-slate-400 text-sm">
                  Real Test Set (20 patients). Paired real X-rays (used as model inputs)
                  and reference CTs are available; this set enables quantitative comparison
                  between generated CT slices (blue) and ground-truth CT slices (green).
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-slate-300 mb-2">Indiana University</h4>
                <p className="text-slate-400 text-sm">
                  Indiana University (3,405 chest X-ray studies). External clinical X-rays
                  only; reference CTs are not available, so only model-generated CTs are
                  displayed.
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-slate-300 mb-2">Synthetic / Mixed Test Sets</h4>
                <p className="text-slate-400 text-sm">
                  Model test split(s) with paired DRRs/X-rays and reference CTs. The
                  Synthetic Model Test Set contains 222 synthetic X-ray samples paired
                  with reference CTs for evaluation in the synthetic domain. The Mixed
                  Test Set uses the same 222-sample split but 20 patients have real
                  X-rays instead of DRRs.
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
