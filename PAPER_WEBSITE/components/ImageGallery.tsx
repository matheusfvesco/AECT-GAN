'use client';

import { useState, useEffect, useRef } from 'react';
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
  const [searchQuery, setSearchQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  const filteredPatients = searchQuery
    ? patients.filter((p) => p.id.toLowerCase().includes(searchQuery.toLowerCase()))
    : [];

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

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

  const selectPatient = (patientId: string) => {
    const index = patients.findIndex((p) => p.id === patientId);
    if (index !== -1) {
      setCurrentPage(index);
      setSearchQuery('');
      setShowDropdown(false);
    }
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
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold mb-2">{title}</h2>
            <p className="text-slate-400">{description}</p>
          </div>
          {/* Search */}
          <div ref={searchRef} className="relative w-full sm:w-auto">
            <input
              type="text"
              placeholder="Search patient..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 w-full sm:w-48 focus:outline-none focus:border-blue-500"
            />
            {showDropdown && searchQuery && (
              <div className="absolute top-full mt-1 left-0 right-0 bg-slate-700 border border-slate-600 rounded-lg shadow-xl max-h-60 overflow-y-auto z-10">
                {filteredPatients.length > 0 ? (
                  filteredPatients.slice(0, 20).map((patient) => (
                    <button
                      key={patient.id}
                      onClick={() => selectPatient(patient.id)}
                      className="w-full px-4 py-2 text-left text-white hover:bg-slate-600 transition-colors"
                    >
                      {patient.id}
                    </button>
                  ))
                ) : (
                  <div className="px-4 py-2 text-slate-400">No patients found</div>
                )}
              </div>
            )}
          </div>
        </div>
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
