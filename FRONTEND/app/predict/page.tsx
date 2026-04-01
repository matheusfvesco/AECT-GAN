'use client';

import { useState, useCallback, useRef } from 'react';
import { XRayViewer, CTSyncViewer } from '@/components';
import { X2CTPredictResponse } from '@/types';
import { uploadZipPredict } from '@/lib/api';
import Link from 'next/link';

const modelInfo = {
  real: {
    label: 'Real CT Model',
    tooltip: 'Trained with 182 real X-ray samples',
    color: 'green',
  },
  synthetic: {
    label: 'Synthetic CT Model',
    tooltip: 'Trained with 2006 CT samples (DRR X-ray pairs)',
    color: 'purple',
  },
  mixed: {
    label: 'Mixed CT Model',
    tooltip: 'Trained with 2006 CT samples: 182 real X-ray pairs + 1824 DRR pairs',
    color: 'cyan',
  },
};

export default function PredictPage() {
  const [result, setResult] = useState<X2CTPredictResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = useCallback(async (file: File, modelType: 'real' | 'synthetic' | 'mixed') => {
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

  return (
    <main className="min-h-screen bg-slate-900 text-white">
      <header className="border-b border-slate-700 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">AECT-GAN Predict</h1>
              <p className="text-slate-400 text-sm">Generate CT from X-rays without metrics</p>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/" className="px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 rounded transition-colors">Home</Link>
              {result && <button onClick={handleReset} className="px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 rounded transition-colors">New Upload</button>}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {!result ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="text-center mb-8 max-w-2xl">
              <h2 className="text-3xl font-semibold mb-4">Generate CT from X-Rays</h2>
              <p className="text-slate-400">
                Upload a ZIP containing 2 X-ray images (frontal and lateral views).
                Supported formats: DICOM files or JPEG/PNG images.
              </p>
            </div>
            <PredictFileUploader onUpload={handleUpload} isLoading={isLoading} error={error} />
          </div>
        ) : (
          <div className="space-y-10">
            <section>
              <h2 className="text-xl font-semibold mb-4 text-slate-200">Input X-Rays</h2>
              <XRayViewer xrays={result.xrays} />
            </section>
            <section>
              <h2 className="text-xl font-semibold mb-4 text-slate-200">Generated CT</h2>
              {/* Model Type Badge */}
              <div className="flex items-center gap-3 mb-4">
                <span className="text-slate-400 text-sm">Model used:</span>
                <div className="relative group">
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium cursor-help ${
                      modelInfo[result.model_type as keyof typeof modelInfo]?.color === 'green'
                        ? 'bg-green-900/50 text-green-400 border border-green-700'
                        : modelInfo[result.model_type as keyof typeof modelInfo]?.color === 'purple'
                        ? 'bg-purple-900/50 text-purple-400 border border-purple-700'
                        : 'bg-cyan-900/50 text-cyan-400 border border-cyan-700'
                    }`}
                  >
                    {modelInfo[result.model_type as keyof typeof modelInfo]?.label || 'Unknown'}
                  </span>
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-slate-800 text-white text-xs rounded-lg border border-slate-600 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                    {modelInfo[result.model_type as keyof typeof modelInfo]?.tooltip}
                    <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-800" />
                  </div>
                </div>
              </div>
              <p className="text-slate-400 text-sm mb-4">
                Dimensions: {result.dimensions.depth} x {result.dimensions.height} x {result.dimensions.width} voxels
              </p>
              <CTSyncViewer generatedSlices={result.ct.generated} />
            </section>
          </div>
        )}
      </div>

      <footer className="border-t border-slate-700 mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <p className="text-slate-500 text-sm text-center">AECT-GAN Playground — Ephemeral processing. No data is stored.</p>
        </div>
      </footer>
    </main>
  );
}

// Simplified FileUploader for predict
function PredictFileUploader({ onUpload, isLoading, error }: {
  onUpload: (file: File, modelType: 'real' | 'synthetic' | 'mixed') => void;
  isLoading: boolean;
  error: string | null;
}) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [modelType, setModelType] = useState<'real' | 'synthetic' | 'mixed'>('real');
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
          <h3 className="text-slate-200 font-semibold mb-2">ZIP File Structure</h3>
          <p className="text-slate-400 mb-3">Your ZIP must contain exactly 2 X-ray files:</p>
          <ul className="text-slate-300 space-y-1 list-disc list-inside">
            <li><span className="text-white font-medium">DICOM mode:</span> 2 DICOM X-ray files</li>
            <li><span className="text-white font-medium">Image mode:</span> 2 JPEG/PNG images</li>
          </ul>
        </div>

        <div className="border-2 border-dashed border-slate-600 rounded-lg p-6 text-center hover:border-slate-500 transition-colors relative">
          <input ref={fileInputRef} type="file" accept=".zip" onChange={handleFileChange} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
          <div className="flex flex-col items-center gap-3 pointer-events-none">
            <button type="button" className="px-4 py-2 rounded bg-purple-600 text-white text-sm font-semibold hover:bg-purple-700">Browse</button>
            <p className="text-slate-400 text-sm">{fileName || 'No file selected'}</p>
          </div>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <label htmlFor="model-type" className="text-slate-200 text-sm font-semibold block mb-1">Model Type</label>
          <select id="model-type" value={modelType} onChange={(e) => setModelType(e.target.value as 'real' | 'synthetic' | 'mixed')}
            disabled={isLoading} className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded text-white text-sm focus:outline-none focus:border-purple-500 disabled:opacity-50">
            <option value="real">Real — trained with real X-rays (182 samples)</option>
            <option value="synthetic">Synthetic — trained with DRRs (2006 samples)</option>
            <option value="mixed">Mixed — 182 real + 1824 DRR pairs (2006 total)</option>
          </select>
        </div>

        {error && <div className="text-red-400 text-sm bg-red-900/20 p-3 rounded border border-red-800">{error}</div>}

        <button type="submit" disabled={isLoading}
          className="px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors">
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Processing...
            </span>
          ) : 'Generate CT'}
        </button>
      </form>
    </div>
  );
}
