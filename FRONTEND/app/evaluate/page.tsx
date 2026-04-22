'use client';

import { useState, useCallback, useEffect } from 'react';
import { FileUploader, XRayViewer, MetricsPanel, CTSyncViewer, DisclaimerModal } from '@/components';
import { X2CTResponse } from '@/types';
import { uploadZip } from '@/lib/api';
import Link from 'next/link';
import { SITE } from '@/src/lib/content';

export default function EvaluatePage() {
  const [result, setResult] = useState<X2CTResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = useCallback(async (file: File, modelType: 'real' | 'synthetic' | 'mixed') => {
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

  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);

  useEffect(() => {
    const accepted = sessionStorage.getItem('evaluate_disclaimer_accepted');
    if (accepted === 'true') setDisclaimerAccepted(true);
  }, []);

  if (!disclaimerAccepted) {
    return (
      <main className="min-h-screen bg-slate-900 text-white">
        <DisclaimerModal
          isOpen={true}
          onAccept={() => {
            setDisclaimerAccepted(true);
            sessionStorage.setItem('evaluate_disclaimer_accepted', 'true');
          }}
          variant="evaluate"
        />
      </main>
    );
  }

  const { evaluate, footer } = SITE;

  return (
    <main className="min-h-screen bg-slate-900 text-white">
      <header className="border-b border-slate-700 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/" className="hover:text-blue-400 transition-colors">
                <h1 className="text-2xl font-bold text-white">{evaluate.headerTitle}</h1>
              </Link>
              <p className="text-slate-400 text-sm">{SITE.tagline}</p>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/" className="px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 rounded transition-colors">{evaluate.home}</Link>
              {result && <button onClick={handleReset} className="px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 rounded transition-colors">{evaluate.newUpload}</button>}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {!result ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="text-center mb-8 max-w-2xl">
              <h2 className="text-3xl font-semibold mb-4">{evaluate.sectionHeading}</h2>
              <p className="text-slate-400">{evaluate.uploadInstructions}</p>
            </div>
            <FileUploader onUpload={handleUpload} isLoading={isLoading} error={error} />
          </div>
        ) : (
          <div className="space-y-10">
            <section>
              <h2 className="text-xl font-semibold mb-4 text-slate-200">{evaluate.inputXRays}</h2>
              <XRayViewer xrays={result.xrays} />
            </section>
            <section>
              <h2 className="text-xl font-semibold mb-4 text-slate-200">{evaluate.evaluationMetrics}</h2>
              <MetricsPanel metrics={result.metrics} />
            </section>
            <section>
              <h2 className="text-xl font-semibold mb-4 text-slate-200">{evaluate.ctComparison}</h2>
              <p className="text-slate-400 text-sm mb-4">
                {evaluate.dimensions.replace('{depth}', String(result.dimensions.depth)).replace('{height}', String(result.dimensions.height)).replace('{width}', String(result.dimensions.width))}
              </p>
              <CTSyncViewer generatedSlices={result.ct.generated} originalSlices={result.ct.original} />
            </section>
          </div>
        )}
      </div>

      <footer className="border-t border-slate-700 mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <p className="text-slate-500 text-sm text-center">{footer.privacy}</p>
          <p className="text-slate-600 text-xs text-center mt-1">{footer.clinical}</p>
        </div>
      </footer>
    </main>
  );
}
