'use client';

import { useState, useEffect } from 'react';
import CTSyncViewer from './CTSyncViewer';

interface PatientData {
  id: string;
  fakeSlices: string[];
  gtSlices: string[];
  xray1: string | null;
  xray2: string | null;
  frontal: string | null;
  lateral: string | null;
}

interface ImageGalleryProps {
  dataset: string;
  title: string;
  description: string;
  showGroundTruth: boolean;
  xrayLabels?: { xray1?: string; xray2?: string; frontal?: string; lateral?: string };
}

export default function ImageGallery({
  dataset,
  title,
  description,
  showGroundTruth,
  xrayLabels,
}: ImageGalleryProps) {
  const [patients, setPatients] = useState<PatientData[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);

  useEffect(() => {
    async function loadData() {
      try {
        const response = await fetch(`/api/list-patients?dataset=${encodeURIComponent(dataset)}`);
        const data = await response.json();
        setPatients(data.patients || []);
      } catch (error) {
        console.error('Failed to load patients:', error);
        setPatients([]);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [dataset]);

  const currentPatient = patients[currentPage];
  const totalPages = patients.length;

  const goToPrevious = () => {
    setCurrentPage((prev) => Math.max(0, prev - 1));
  };

  const goToNext = () => {
    setCurrentPage((prev) => Math.min(totalPages - 1, prev + 1));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-slate-400">Loading patient data...</div>
      </div>
    );
  }

  if (patients.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-slate-400">
        <p>No patient data found for dataset.</p>
        <p className="text-sm mt-2">{dataset}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-2">{title}</h2>
        <p className="text-slate-400">{description}</p>
      </div>

      {/* Patient Navigation */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
        <div className="flex items-center justify-between">
          <button
            onClick={goToPrevious}
            disabled={currentPage === 0}
            className="px-4 py-2 bg-slate-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600 transition-colors"
          >
            Previous
          </button>
          <div className="text-center">
            <span className="text-xl font-semibold">{currentPatient.id}</span>
            <p className="text-slate-400 text-sm">
              Patient {currentPage + 1} of {totalPages}
            </p>
          </div>
          <button
            onClick={goToNext}
            disabled={currentPage === totalPages - 1}
            className="px-4 py-2 bg-slate-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600 transition-colors"
          >
            Next
          </button>
        </div>
      </div>

      {/* Viewer */}
      {currentPatient && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <CTSyncViewer
            fakeSlices={currentPatient.fakeSlices}
            gtSlices={showGroundTruth ? currentPatient.gtSlices : []}
            xray1={currentPatient.xray1}
            xray2={currentPatient.xray2}
            frontal={currentPatient.frontal}
            lateral={currentPatient.lateral}
            xrayLabels={xrayLabels}
          />
        </div>
      )}

      {/* Pagination Dots */}
      <div className="flex justify-center gap-2 flex-wrap">
        {Array.from({ length: Math.min(totalPages, 20) }).map((_, idx) => (
          <button
            key={idx}
            onClick={() => setCurrentPage(idx)}
            className={`w-3 h-3 rounded-full transition-colors ${
              idx === currentPage ? 'bg-blue-500' : 'bg-slate-600 hover:bg-slate-500'
            }`}
          />
        ))}
        {totalPages > 20 && (
          <span className="text-slate-400 text-sm ml-2">
            +{totalPages - 20} more patients
          </span>
        )}
      </div>
    </div>
  );
}
