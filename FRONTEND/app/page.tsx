'use client';

import { useState, useCallback } from 'react';
import { FileUploader, XRayViewer, MetricsPanel, CTSyncViewer } from '@/components';
import { X2CTResponse } from '@/types';
import { uploadZip } from '@/lib/api';

export default function Home() {
  const [result, setResult] = useState<X2CTResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = useCallback(async (file: File, modelType: 'real' | 'synthetic' | 'mixed' | 'x2ct') => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await uploadZip(file, modelType);

      if (response.success && response.data) {
        setResult(response.data);
      } else {
        setError(response.error || 'Upload failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleReset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return (
    <main className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">X2CT Playground</h1>
              <p className="text-slate-400 text-sm">
                X-Ray to CT reconstruction from dual-view X-rays
              </p>
            </div>
            {/* Training Info - only show on upload page, hide on dashboard */}
            {!result && (
              <div className="flex items-center gap-6 text-xs text-slate-400">
                <div>
                  <span className="text-green-400 font-medium">Real Model</span>
                  <br />
                  182 training samples
                </div>
                <div>
                  <span className="text-purple-400 font-medium">Synthetic Model</span>
                  <br />
                  2006 training samples
                </div>
                <div>
                  <span className="text-cyan-400 font-medium">Mixed Model</span>
                  <br />
                  2006 training samples
                </div>
                <div>
                  <span className="text-amber-400 font-medium">X2CT Model</span>
                  <br />
                  916 training samples
                </div>
              </div>
            )}
            {result && (
              <button
                onClick={handleReset}
                className="px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 rounded transition-colors"
              >
                New Upload
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {!result ? (
          /* Upload state */
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="text-center mb-8 max-w-2xl">
              <h2 className="text-3xl font-semibold mb-4">
                Reconstruct CT from X-Rays
              </h2>
              <p className="text-slate-400">
                Upload a ZIP containing a CT scan and frontal + lateral X-rays.
                The model will generate a synthetic CT from the X-rays. Compare
                the generated CT with the original (resized to match) using the
                synchronized 3D slice viewer.
              </p>
            </div>
            <FileUploader
              onUpload={handleUpload}
              isLoading={isLoading}
              error={error}
            />
          </div>
        ) : (
          /* Results state */
          <div className="space-y-10">
            {/* X-Ray Input Section */}
            <section>
              <h2 className="text-xl font-semibold mb-4 text-slate-200">
                Input X-Rays
              </h2>
              <XRayViewer xrays={result.xrays} />
            </section>

            {/* Metrics Section */}
            <section>
              <h2 className="text-xl font-semibold mb-4 text-slate-200">
                Evaluation Metrics
              </h2>
              <MetricsPanel metrics={result.metrics} />
            </section>

            {/* CT Comparison Section */}
            <section>
              <h2 className="text-xl font-semibold mb-4 text-slate-200">
                CT Comparison
              </h2>
              <p className="text-slate-400 text-sm mb-4">
                Dimensions: {result.dimensions.depth} x{' '}
                {result.dimensions.height} x {result.dimensions.width} voxels
              </p>
              <CTSyncViewer
                generatedSlices={result.ct.generated}
                originalSlices={result.ct.original}
              />
            </section>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700 mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <p className="text-slate-500 text-sm text-center">
            X2CT Playground — Ephemeral processing. No data is stored.
          </p>
        </div>
      </footer>
    </main>
  );
}
