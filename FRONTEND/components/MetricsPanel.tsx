'use client';

import { X2CTMetrics } from '@/types';
import { MODELS, METRICS } from '@/src/lib/content';

interface MetricsPanelProps {
  metrics: X2CTMetrics;
}

const modelColors = {
  real: 'green',
  synthetic: 'blue',
  mixed: 'purple',
} as const;

export function MetricsPanel({ metrics }: MetricsPanelProps) {
  const { model_type, ...numericMetrics } = metrics;
  const model = MODELS[model_type] || MODELS.real;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <span className="text-slate-400 text-sm">Model used:</span>
        <div className="relative group">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium cursor-help ${
              modelColors[model_type] === 'green'
                ? 'bg-green-900/50 text-green-400 border border-green-700'
                : modelColors[model_type] === 'blue'
                ? 'bg-blue-900/50 text-blue-400 border border-blue-700'
                : 'bg-purple-900/50 text-purple-400 border border-purple-700'
            }`}
          >
            {model.label}
          </span>
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-slate-800 text-white text-xs rounded-lg border border-slate-600 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
            {model.tooltip}
            <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-800" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {(Object.entries(numericMetrics) as [string, number][]).map(
          ([key, value]) => {
            const label = METRICS[key as keyof typeof METRICS] || key;
            return (
              <div
                key={key}
                className="bg-slate-800 border border-slate-700 p-4 rounded-lg"
              >
                <p className="text-slate-400 text-xs mb-1">
                  {label}
                </p>
                <p className="text-white text-2xl font-mono">
                  {typeof value === 'number' ? value.toFixed(4) : value}
                </p>
              </div>
            );
          }
        )}
      </div>
    </div>
  );
}
