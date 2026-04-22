'use client';

import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { getDataUrl } from '@/lib/api';
import { CTSYNCVIEWER } from '@/src/lib/content';

interface CTSyncViewerProps {
  generatedSlices: string[];
  originalSlices?: string[];
}

export function CTSyncViewer({
  generatedSlices,
  originalSlices,
}: CTSyncViewerProps) {
  const totalSlices = generatedSlices.length;
  const [currentSlice, setCurrentSlice] = useState(totalSlices / 2);
  const [imageSize, setImageSize] = useState<128 | 256 | 512>(128);
  const containerRef = useRef<HTMLDivElement>(null);
  const hasOriginal = originalSlices && originalSlices.length > 0;

  const sizeOptions: (128 | 256 | 512)[] = [128, 256, 512];

  const generatedUrl = useMemo(
    () => getDataUrl(generatedSlices[currentSlice]),
    [generatedSlices, currentSlice]
  );

  const originalUrl = useMemo(
    () => hasOriginal ? getDataUrl(originalSlices![currentSlice]) : getDataUrl(generatedSlices[currentSlice]),
    [hasOriginal, originalSlices, generatedSlices, currentSlice]
  );

  const handleWheel = useCallback(
    (e: WheelEvent) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 1 : -1;
      setCurrentSlice((prev) =>
        Math.max(0, Math.min(totalSlices - 1, prev + delta))
      );
    },
    [totalSlices]
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
        e.preventDefault();
        setCurrentSlice((prev) => Math.max(0, prev - 1));
      } else if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
        e.preventDefault();
        setCurrentSlice((prev) => Math.min(totalSlices - 1, prev + 1));
      } else if (e.key === 'Home') {
        e.preventDefault();
        setCurrentSlice(0);
      } else if (e.key === 'End') {
        e.preventDefault();
        setCurrentSlice(totalSlices - 1);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [totalSlices]);

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('wheel', handleWheel, { passive: false });
      return () => container.removeEventListener('wheel', handleWheel);
    }
  }, [handleWheel]);

  const sliceIndicator = CTSYNCVIEWER.sliceIndicator
    .replace('{current}', String(currentSlice + 1))
    .replace('{total}', String(totalSlices));

  return (
    <div className="flex flex-col items-center">
      <div className="text-slate-300 text-lg mb-4 font-mono">
        {sliceIndicator}
      </div>

      <div className="flex gap-2 mb-4">
        {sizeOptions.map((size) => (
          <button
            key={size}
            onClick={() => setImageSize(size)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              imageSize === size
                ? 'bg-blue-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            {sizeOptions.indexOf(size) === 0
              ? CTSYNCVIEWER.sizeButtons[0]
              : sizeOptions.indexOf(size) === 1
              ? CTSYNCVIEWER.sizeButtons[1]
              : CTSYNCVIEWER.sizeButtons[2]}
          </button>
        ))}
      </div>

      {imageSize !== 128 && (
        <div className="text-amber-400 text-sm mb-2">
          {CTSYNCVIEWER.resizeNotice}
        </div>
      )}

      <div
        ref={containerRef}
        className="flex flex-col md:flex-row gap-8 cursor-pointer select-none p-4 bg-slate-800/50 rounded-lg"
        tabIndex={0}
      >
        <div className="flex flex-col items-center">
          <span className="text-blue-400 mb-2 font-semibold text-sm">
            {CTSYNCVIEWER.generatedCT}
          </span>
          <img
            src={generatedUrl}
            alt={`Generated slice ${currentSlice}`}
            width={imageSize}
            height={imageSize}
            className="border border-blue-500/50 rounded"
            style={{ imageRendering: imageSize > 128 ? 'auto' : 'pixelated' }}
          />
        </div>

        {hasOriginal && (
          <div className="flex flex-col items-center">
            <span className="text-green-400 mb-2 font-semibold text-sm">
              {CTSYNCVIEWER.originalCT}
            </span>
            <img
              src={originalUrl}
              alt={`Original slice ${currentSlice}`}
              width={imageSize}
              height={imageSize}
              className="border border-green-500/50 rounded"
              style={{ imageRendering: imageSize > 128 ? 'auto' : 'pixelated' }}
            />
          </div>
        )}
      </div>

      <div className="w-full max-w-md mt-6 px-4">
        <input
          type="range"
          min={0}
          max={totalSlices - 1}
          value={currentSlice}
          onChange={(e) => setCurrentSlice(Number(e.target.value))}
          className="w-full h-2 rounded-lg appearance-none cursor-pointer"
        />
      </div>

      <div className="flex gap-6 mt-4 text-slate-500 text-sm">
        <span>{CTSYNCVIEWER.hintWheel}</span>
        <span>{CTSYNCVIEWER.hintArrow}</span>
        <span>{CTSYNCVIEWER.hintHomeEnd}</span>
      </div>
    </div>
  );
}
