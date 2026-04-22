'use client';

import { X2CTXrays } from '@/types';
import { getDataUrl } from '@/lib/api';
import { XRAYVIEWER } from '@/src/lib/content';

interface XRayViewerProps {
  xrays: X2CTXrays;
}

export function XRayViewer({ xrays }: XRayViewerProps) {
  return (
    <div className="flex flex-wrap gap-8">
      <div className="flex flex-col items-center">
        <p className="text-purple-400 text-sm mb-2 font-semibold">{XRAYVIEWER.frontalLabel}</p>
        <img
          src={getDataUrl(xrays.frontal)}
          alt={XRAYVIEWER.frontalAlt}
          width={256}
          height={256}
          className="border border-purple-500/50 rounded"
        />
      </div>
      <div className="flex flex-col items-center">
        <p className="text-purple-400 text-sm mb-2 font-semibold">{XRAYVIEWER.lateralLabel}</p>
        <img
          src={getDataUrl(xrays.lateral)}
          alt={XRAYVIEWER.lateralAlt}
          width={256}
          height={256}
          className="border border-purple-500/50 rounded"
        />
      </div>
    </div>
  );
}
