'use client';

import { useEffect } from 'react';
import { DISCLAIMER } from '@/src/lib/content';

interface DisclaimerModalProps {
  onAccept: () => void;
  isOpen: boolean;
  variant: 'evaluate' | 'predict';
}

export default function DisclaimerModal({ onAccept, isOpen, variant }: DisclaimerModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const buttonColor = variant === 'evaluate' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-purple-600 hover:bg-purple-700';
  const iconColor = variant === 'evaluate' ? 'text-blue-400' : 'text-purple-400';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" role="dialog" aria-modal="true" aria-labelledby="disclaimer-title" aria-describedby="disclaimer-desc">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      <div className="relative bg-slate-800 border border-slate-600 rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto shadow-2xl">
        <h2 id="disclaimer-title" className={`text-2xl font-bold text-white mb-4 flex items-center gap-3`}>
          <svg className={`w-8 h-8 ${iconColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          {DISCLAIMER.title}
        </h2>

        <div id="disclaimer-desc" className="text-slate-300 space-y-4 mb-6 leading-relaxed">
          <p>
            {DISCLAIMER.body1}
          </p>

          <p className="text-white font-medium">{DISCLAIMER.body2}</p>
          <ul className="list-disc list-inside space-y-1 ml-4">
            {DISCLAIMER.prohibited.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>

          <p>
            {DISCLAIMER.body3}
          </p>

          <p className="text-slate-400 text-sm italic">
            {DISCLAIMER.body4}
          </p>
        </div>

        <button
          onClick={onAccept}
          className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors ${buttonColor} text-white`}
        >
          {DISCLAIMER.accept}
        </button>
      </div>
    </div>
  );
}
