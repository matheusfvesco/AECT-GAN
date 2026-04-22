'use client';

import { useRef, useState } from 'react';
import { FILEUPLOADER, MODELS } from '@/src/lib/content';

interface FileUploaderProps {
  onUpload: (file: File, modelType: 'real' | 'synthetic' | 'mixed') => void;
  isLoading: boolean;
  error: string | null;
}

export function FileUploader({ onUpload, isLoading, error }: FileUploaderProps) {
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
    if (file) {
      onUpload(file, modelType);
    }
  };

  const modelDescriptions = {
    real: MODELS.real.description,
    synthetic: MODELS.synthetic.description,
    mixed: MODELS.mixed.description,
  };

  return (
    <div className="w-full max-w-2xl">
      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-sm">
          <h3 className="text-slate-200 font-semibold mb-2">{FILEUPLOADER.zipStructure}</h3>
          <p className="text-slate-400 mb-3">{FILEUPLOADER.zipInstruction}</p>
          <ul className="text-slate-300 space-y-1 list-disc list-inside">
            <li>
              <span className="text-white font-medium">{FILEUPLOADER.ctScan}</span> — {FILEUPLOADER.ctScanRequirement}
            </li>
            <li>
              <span className="text-white font-medium">{FILEUPLOADER.xrayViews}</span> — either:
              <ul className="ml-5 text-slate-400 list-circle list-inside mt-1">
                <li>{FILEUPLOADER.multiviewOption}</li>
                <li>{FILEUPLOADER.separateOption}</li>
              </ul>
            </li>
          </ul>
        </div>

        <div className="border-2 border-dashed border-slate-600 rounded-lg p-6 text-center hover:border-slate-500 transition-colors relative">
          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="flex flex-col items-center gap-3 pointer-events-none">
            <button
              type="button"
              className="px-4 py-2 rounded bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700"
            >
              {FILEUPLOADER.browse}
            </button>
            <p className="text-slate-400 text-sm">
              {fileName || FILEUPLOADER.noFileSelected}
            </p>
          </div>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <div className="flex items-start gap-4">
            <div className="flex-1">
              <label htmlFor="model-type" className="text-slate-200 text-sm font-semibold block mb-1">
                {FILEUPLOADER.modelType}
              </label>
              <select
                id="model-type"
                value={modelType}
                onChange={(e) => setModelType(e.target.value as 'real' | 'synthetic' | 'mixed')}
                disabled={isLoading}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded text-white text-sm focus:outline-none focus:border-blue-500 disabled:opacity-50"
              >
                <option value="real">{MODELS.real.optionLabel}</option>
                <option value="synthetic">{MODELS.synthetic.optionLabel}</option>
                <option value="mixed">{MODELS.mixed.optionLabel}</option>
              </select>
            </div>
          </div>
          <p className="text-slate-400 text-xs mt-2">
            {modelDescriptions[modelType]}
          </p>
        </div>

        {error && (
          <div className="text-red-400 text-sm bg-red-900/20 p-3 rounded border border-red-800">
            Error: {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg
                className="animate-spin h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              {FILEUPLOADER.processing}
            </span>
          ) : (
            FILEUPLOADER.uploadAndProcess
          )}
        </button>
      </form>
    </div>
  );
}
