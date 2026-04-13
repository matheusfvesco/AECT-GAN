'use client';

import { X2CTMetrics } from '@/types';

interface MetricsPanelProps {
  metrics: X2CTMetrics;
}

const modelInfo = {
  real: {
    label: 'Real CT Model',
    tooltip: 'Trained with 182 real X-ray samples',
    color: 'green',
  },
  synthetic: {
    label: 'Synthetic CT Model',
    tooltip: 'Trained with 2006 CT samples (DRR X-ray pairs)',
    color: 'blue',
  },
  mixed: {
    label: 'Mixed CT Model',
    tooltip: 'Trained with 2006 CT samples: 182 real X-ray pairs + 1824 DRR pairs',
    color: 'purple',
  },
};

export function MetricsPanel({ metrics }: MetricsPanelProps) {
  const { model_type, ...numericMetrics } = metrics;
  const info = modelInfo[model_type] || modelInfo.real;

  return (
    <div className="space-y-4">
      {/* Model Type Badge with Tooltip */}
      <div className="flex items-center gap-3">
        <span className="text-slate-400 text-sm">Model used:</span>
        <div className="relative group">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium cursor-help ${
              info.color === 'green'
                ? 'bg-green-900/50 text-green-400 border border-green-700'
                : info.color === 'blue'
                ? 'bg-blue-900/50 text-blue-400 border border-blue-700'
                : 'bg-purple-900/50 text-purple-400 border border-purple-700'
            }`}
          >
            {info.label}
          </span>
          {/* Tooltip */}
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-slate-800 text-white text-xs rounded-lg border border-slate-600 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
            {info.tooltip}
            {/* Arrow */}
            <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-800" />
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {(Object.entries(numericMetrics) as [string, number][]).map(
          ([key, value]) => (
            <div
              key={key}
              className="bg-slate-800 border border-slate-700 p-4 rounded-lg"
            >
              <p className="text-slate-400 text-xs mb-1">
                {key}
              </p>
              <p className="text-white text-2xl font-mono">
                {typeof value === 'number' ? value.toFixed(4) : value}
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
}
