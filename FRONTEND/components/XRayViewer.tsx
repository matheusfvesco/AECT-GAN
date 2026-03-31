'use client';

import { X2CTXrays } from '@/types';
import { getDataUrl } from '@/lib/api';

interface XRayViewerProps {
  xrays: X2CTXrays;
}

export function XRayViewer({ xrays }: XRayViewerProps) {
  return (
    <div className="flex flex-wrap gap-8">
      <div className="flex flex-col items-center">
        <p className="text-slate-400 text-sm mb-2">Frontal View</p>
        <img
          src={getDataUrl(xrays.frontal)}
          alt="Frontal X-ray"
          width={256}
          height={256}
          className="border border-slate-600 rounded"
        />
      </div>
      <div className="flex flex-col items-center">
        <p className="text-slate-400 text-sm mb-2">Lateral View</p>
        <img
          src={getDataUrl(xrays.lateral)}
          alt="Lateral X-ray"
          width={256}
          height={256}
          className="border border-slate-600 rounded"
        />
      </div>
    </div>
  );
}
