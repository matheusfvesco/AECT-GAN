'use client';

import { useEffect } from 'react';

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
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      <div className="relative bg-slate-800 border border-slate-600 rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto shadow-2xl">
        <h2 className={`text-2xl font-bold text-white mb-4 flex items-center gap-3`}>
          <svg className={`w-8 h-8 ${iconColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Important Disclaimer
        </h2>

        <div className="text-slate-300 space-y-4 mb-6 leading-relaxed">
          <p>
            Content generated through this website is intended for <span className="text-white font-medium">research and demonstration purposes only</span>. The CT images and metrics produced by the AECT-GAN model are experimental and have <span className="text-red-400 font-medium">NOT</span> been validated for clinical use.
          </p>

          <p className="text-white font-medium">Content accessed through this platform should NOT be used for:</p>
          <ul className="list-disc list-inside space-y-1 ml-4">
            <li>Medical diagnosis</li>
            <li>Treatment planning</li>
            <li>Clinical decision-making</li>
            <li>Any medical purpose</li>
          </ul>

          <p>
            This is a research demonstration of deep learning technology for dual-view X-ray to CT reconstruction. Results may contain artifacts, inaccuracies, or unrealistic structures. This model has not been approved by any regulatory body (including the FDA) for medical use.
          </p>

          <p className="text-slate-400 text-sm italic">
            By proceeding, you acknowledge that this tool is for demonstration and research purposes only, and that any use of generated content for clinical purposes is at the user&apos;s own risk and discretion.
          </p>
        </div>

        <button
          onClick={onAccept}
          className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors ${buttonColor} text-white`}
        >
          I Understand and Accept
        </button>
      </div>
    </div>
  );
}