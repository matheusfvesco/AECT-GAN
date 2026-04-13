'use client';

import { useState, useCallback, useEffect, useRef } from 'react';

interface CTSyncViewerProps {
  fakeSlices: string[];
  gtSlices: string[];
  xray1?: string | null;
  xray2?: string | null;
  frontal?: string | null;
  lateral?: string | null;
  xrayLabels?: { xray1?: string; xray2?: string; frontal?: string; lateral?: string };
}

const prefetchImage = (src: string) => {
  if (typeof window !== 'undefined') {
    const img = new Image();
    img.src = src;
  }
};

export default function CTSyncViewer({
  fakeSlices,
  gtSlices,
  xray1,
  xray2,
  frontal,
  lateral,
  xrayLabels,
}: CTSyncViewerProps) {
  const totalSlices = fakeSlices.length;
  const [currentSlice, setCurrentSlice] = useState(Math.floor(totalSlices / 2));
  const [imageSize, setImageSize] = useState<128 | 256 | 512>(128);
  const containerRef = useRef<HTMLDivElement>(null);
  const prefetchedSlices = useRef<Set<number>>(new Set());

  const sizeOptions: (128 | 256 | 512)[] = [128, 256, 512];

  const prefetchSlices = useCallback(
    (centerSlice: number) => {
      const toPrefetch = [
        centerSlice - 2,
        centerSlice - 1,
        centerSlice + 1,
        centerSlice + 2,
      ];
      toPrefetch.forEach((idx) => {
        if (idx >= 0 && idx < totalSlices && !prefetchedSlices.current.has(idx)) {
          prefetchImage(fakeSlices[idx]);
          if (gtSlices.length > 0) {
            prefetchImage(gtSlices[idx]);
          }
          prefetchedSlices.current.add(idx);
        }
      });
    },
    [fakeSlices, gtSlices, totalSlices]
  );

  useEffect(() => {
    const initialIdx = Math.floor(totalSlices / 2);
    prefetchSlices(initialIdx);
    if (xray1) prefetchImage(xray1);
    if (xray2) prefetchImage(xray2);
    if (frontal) prefetchImage(frontal);
    if (lateral) prefetchImage(lateral);
  }, [xray1, xray2, frontal, lateral, prefetchSlices, totalSlices]);

  useEffect(() => {
    prefetchSlices(currentSlice);
  }, [currentSlice, prefetchSlices]);

  // Detect patient change - when fakeSlices reference changes, prefetch all slices
  useEffect(() => {
    prefetchedSlices.current.clear();
    fakeSlices.forEach((slice) => prefetchImage(slice));
    if (gtSlices.length > 0) {
      gtSlices.forEach((slice) => prefetchImage(slice));
    }
    if (xray1) prefetchImage(xray1);
    if (xray2) prefetchImage(xray2);
    if (frontal) prefetchImage(frontal);
    if (lateral) prefetchImage(lateral);
  }, [fakeSlices, gtSlices, xray1, xray2, frontal, lateral]);

  // Wheel-based navigation
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

  // Keyboard navigation
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

  // Attach wheel listener
  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('wheel', handleWheel, { passive: false });
      return () => container.removeEventListener('wheel', handleWheel);
    }
  }, [handleWheel]);

  return (
    <div className="flex flex-col items-center">
      {/* Slice indicator */}
      <div className="text-slate-300 text-lg mb-4 font-mono">
        Slice {currentSlice + 1} / {totalSlices}
      </div>

      {/* Size selector buttons */}
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
            {size}x{size}
          </button>
        ))}
      </div>

      {/* X-Rays display */}
      {(xray1 || xray2 || frontal || lateral) && (
        <div className="flex gap-4 mb-6">
          {xray1 && (
            <div className="flex flex-col items-center">
              <span className="text-purple-400 mb-2 font-semibold text-sm">
                {xrayLabels?.xray1 || 'X-Ray 1 (AP)'}
              </span>
              <img
                src={xray1}
                alt="X-Ray 1"
                width={imageSize}
                height={imageSize}
                className="border border-purple-500/50 rounded"
                style={{ imageRendering: imageSize > 128 ? 'auto' : 'pixelated' }}
              />
            </div>
          )}
          {xray2 && (
            <div className="flex flex-col items-center">
              <span className="text-purple-400 mb-2 font-semibold text-sm">
                {xrayLabels?.xray2 || 'X-Ray 2 (Lateral)'}
              </span>
              <img
                src={xray2}
                alt="X-Ray 2"
                width={imageSize}
                height={imageSize}
                className="border border-purple-500/50 rounded"
                style={{ imageRendering: imageSize > 128 ? 'auto' : 'pixelated' }}
              />
            </div>
          )}
          {frontal && (
            <div className="flex flex-col items-center">
              <span className="text-purple-400 mb-2 font-semibold text-sm">
                {xrayLabels?.frontal || 'Frontal'}
              </span>
              <img
                src={frontal}
                alt="Frontal"
                width={imageSize}
                height={imageSize}
                className="border border-purple-500/50 rounded"
                style={{ imageRendering: imageSize > 128 ? 'auto' : 'pixelated' }}
              />
            </div>
          )}
          {lateral && (
            <div className="flex flex-col items-center">
              <span className="text-purple-400 mb-2 font-semibold text-sm">
                {xrayLabels?.lateral || 'Lateral'}
              </span>
              <img
                src={lateral}
                alt="Lateral"
                width={imageSize}
                height={imageSize}
                className="border border-purple-500/50 rounded"
                style={{ imageRendering: imageSize > 128 ? 'auto' : 'pixelated' }}
              />
            </div>
          )}
        </div>
      )}

      {/* Side-by-side CT viewers */}
      <div
        ref={containerRef}
        className="flex flex-col md:flex-row gap-8 cursor-pointer select-none p-4 bg-slate-800/50 rounded-lg"
        tabIndex={0}
      >
        {/* Generated CT */}
        <div className="flex flex-col items-center">
          <span className="text-blue-400 mb-2 font-semibold text-sm">
            Generated CT
          </span>
          <img
            src={fakeSlices[currentSlice]}
            alt={`Generated slice ${currentSlice}`}
            width={imageSize}
            height={imageSize}
            className="border border-blue-500/50 rounded"
            style={{ imageRendering: imageSize > 128 ? 'auto' : 'pixelated' }}
          />
        </div>

        {/* Ground Truth CT */}
        {gtSlices.length > 0 && (
          <div className="flex flex-col items-center">
            <span className="text-green-400 mb-2 font-semibold text-sm">
              Ground Truth CT
            </span>
            <img
              src={gtSlices[currentSlice]}
              alt={`Ground truth slice ${currentSlice}`}
              width={imageSize}
              height={imageSize}
              className="border border-green-500/50 rounded"
              style={{ imageRendering: imageSize > 128 ? 'auto' : 'pixelated' }}
            />
          </div>
        )}
      </div>

      {/* Slice slider */}
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

      {/* Navigation hints */}
      <div className="flex gap-6 mt-4 text-slate-500 text-sm">
        <span>Scroll or drag slider</span>
        <span>Arrow keys for step-by-step</span>
        <span>Home/End for first/last</span>
      </div>
    </div>
  );
}
