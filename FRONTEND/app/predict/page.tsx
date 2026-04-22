'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { XRayViewer, CTSyncViewer, DisclaimerModal } from '@/components';
import { X2CTPredictResponse } from '@/types';
import { uploadZipPredict } from '@/lib/api';
import Link from 'next/link';
import { SITE, MODELS } from '@/src/lib/content';

const modelColors = {
  real: 'green',
  synthetic: 'blue',
  mixed: 'purple',
} as const;

type ModelType = 'real' | 'synthetic' | 'mixed';

export default function PredictPage() {
  const [result, setResult] = useState<X2CTPredictResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = useCallback(async (file: File, modelType: ModelType) => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await uploadZipPredict(file, modelType);
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
    const accepted = sessionStorage.getItem('predict_disclaimer_accepted');
    if (accepted === 'true') setDisclaimerAccepted(true);
  }, []);

  if (!disclaimerAccepted) {
    return (
      <main className="min-h-screen bg-slate-900 text-white">
        <DisclaimerModal
          isOpen={true}
          onAccept={() => {
            setDisclaimerAccepted(true);
            sessionStorage.setItem('predict_disclaimer_accepted', 'true');
          }}
          variant="predict"
        />
      </main>
    );
  }

  const { predict, footer } = SITE;
  const modelType = result?.model_type || 'real';

  return (
    <main className="min-h-screen bg-slate-900 text-white">
      <header className="border-b border-slate-700 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/" className="hover:text-purple-400 transition-colors">
                <h1 className="text-2xl font-bold text-white">{predict.headerTitle}</h1>
              </Link>
              <p className="text-slate-400 text-sm">{SITE.tagline}</p>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/" className="px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 rounded transition-colors">{predict.home}</Link>
              {result && <button onClick={handleReset} className="px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 rounded transition-colors">{predict.newUpload}</button>}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {!result ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="text-center mb-8 max-w-2xl">
              <h2 className="text-3xl font-semibold mb-4">{predict.sectionHeading}</h2>
              <p className="text-slate-400">{predict.uploadInstructions}</p>
            </div>
            <PredictFileUploader onUpload={handleUpload} isLoading={isLoading} error={error} />
          </div>
        ) : (
          <div className="space-y-10">
            <section>
              <h2 className="text-xl font-semibold mb-4 text-slate-200">{predict.inputXRays}</h2>
              <XRayViewer xrays={result.xrays} />
            </section>
            <section>
              <h2 className="text-xl font-semibold mb-4 text-slate-200">{predict.generatedCT}</h2>
              <div className="flex items-center gap-3 mb-4">
                <span className="text-slate-400 text-sm">{predict.modelUsed}</span>
                <div className="relative group">
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium cursor-help ${
                      modelColors[modelType] === 'green'
                        ? 'bg-green-900/50 text-green-400 border border-green-700'
                        : modelColors[modelType] === 'blue'
                        ? 'bg-blue-900/50 text-blue-400 border border-blue-700'
                        : 'bg-purple-900/50 text-purple-400 border border-purple-700'
                    }`}
                  >
                    {MODELS[modelType].label}
                  </span>
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-slate-800 text-white text-xs rounded-lg border border-slate-600 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                    {MODELS[modelType].tooltip}
                    <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-800" />
                  </div>
                </div>
              </div>
              <p className="text-slate-400 text-sm mb-4">
                {predict.dimensions.replace('{depth}', String(result.dimensions.depth)).replace('{height}', String(result.dimensions.height)).replace('{width}', String(result.dimensions.width))}
              </p>
              <CTSyncViewer generatedSlices={result.ct.generated} />
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

function PredictFileUploader({ onUpload, isLoading, error }: {
  onUpload: (file: File, modelType: ModelType) => void;
  isLoading: boolean;
  error: string | null;
}) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [modelType, setModelType] = useState<ModelType>('real');
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFileChange = (e: { target: HTMLInputElement }) => {
    const file = e.target.files?.[0];
    setFileName(file?.name || null);
  };

  const handleSubmit = (e: { preventDefault: () => void }) => {
    e.preventDefault();
    const file = fileInputRef.current?.files?.[0];
    if (file) onUpload(file, modelType);
  };

  return (
    <div className="w-full max-w-2xl">
      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-sm">
          <h3 className="text-slate-200 font-semibold mb-2">{SITE.predict.zipStructure}</h3>
          <p className="text-slate-400 mb-3">{SITE.predict.zipInstruction}</p>
          <ul className="text-slate-300 space-y-1 list-disc list-inside">
            <li><span className="text-white font-medium">{SITE.predict.dicomMode}</span> {SITE.predict.dicomModeDesc}</li>
            <li><span className="text-white font-medium">{SITE.predict.imageMode}</span> {SITE.predict.imageModeDesc}</li>
          </ul>
        </div>

        <div className="border-2 border-dashed border-slate-600 rounded-lg p-6 text-center hover:border-slate-500 transition-colors relative">
          <input ref={fileInputRef} type="file" accept=".zip" onChange={handleFileChange} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
          <div className="flex flex-col items-center gap-3 pointer-events-none">
            <button type="button" className="px-4 py-2 rounded bg-purple-600 text-white text-sm font-semibold hover:bg-purple-700">{SITE.predict.browse}</button>
            <p className="text-slate-400 text-sm">{fileName || SITE.predict.noFileSelected}</p>
          </div>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <label htmlFor="model-type" className="text-slate-200 text-sm font-semibold block mb-1">{SITE.predict.modelType}</label>
          <select id="model-type" value={modelType} onChange={(e) => setModelType(e.target.value as ModelType)}
            disabled={isLoading} className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded text-white text-sm focus:outline-none focus:border-purple-500 disabled:opacity-50">
            <option value="real">{MODELS.real.optionLabel}</option>
            <option value="synthetic">{MODELS.synthetic.optionLabel}</option>
            <option value="mixed">{MODELS.mixed.optionLabel}</option>
          </select>
        </div>

        {error && <div className="text-red-400 text-sm bg-red-900/20 p-3 rounded border border-red-800">{SITE.predict.errorPrefix} {error}</div>}

        <button type="submit" disabled={isLoading}
          className="px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors">
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              {SITE.predict.processing}
            </span>
          ) : SITE.predict.generateCT}
        </button>
      </form>
    </div>
  );
}
