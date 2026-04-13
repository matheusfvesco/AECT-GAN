import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const dataset = searchParams.get('dataset');

  if (!dataset) {
    return NextResponse.json({ error: 'Dataset parameter is required' }, { status: 400 });
  }

  // Map dataset names to paths
  const datasetPaths: Record<string, string> = {
    'synthetic-real-test': 'data/synthetic-real-test',
    'synthetic-indiana': 'data/synthetic-indiana',
    'mixed-real-test': 'data/mixed-real-test',
    'mixed-indiana': 'data/mixed-indiana',
    'real-real-test': 'data/real-real-test',
    'real-indiana': 'data/real-indiana',
  };

  const relativePath = datasetPaths[dataset];
  if (!relativePath) {
    return NextResponse.json({ error: 'Invalid dataset' }, { status: 400 });
  }

  // Resolve to absolute path for Next.js static files
  const baseDir = path.join(process.cwd(), 'public', relativePath);

  try {
    if (!fs.existsSync(baseDir)) {
      return NextResponse.json({ patients: [], error: 'Dataset not found' }, { status: 200 });
    }

    const entries = fs.readdirSync(baseDir, { withFileTypes: true });
    const patientDirs = entries
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));

    const patients = patientDirs.map((patientId) => {
      const patientDir = path.join(baseDir, patientId);
      const files = fs.readdirSync(patientDir);

      const fakeSlices = files
        .filter((f) => f.startsWith('fake_slice_') && f.endsWith('.png'))
        .sort((a, b) => {
          const numA = parseInt(a.match(/fake_slice_(\d+)/)?.[1] || '0', 10);
          const numB = parseInt(b.match(/fake_slice_(\d+)/)?.[1] || '0', 10);
          return numA - numB;
        })
        .map((f) => `/data/${dataset}/${patientId}/${f}`);

      const gtSlices = files
        .filter((f) => f.startsWith('gt_slice_') && f.endsWith('.png'))
        .sort((a, b) => {
          const numA = parseInt(a.match(/gt_slice_(\d+)/)?.[1] || '0', 10);
          const numB = parseInt(b.match(/gt_slice_(\d+)/)?.[1] || '0', 10);
          return numA - numB;
        })
        .map((f) => `/data/${dataset}/${patientId}/${f}`);

      const xray1 = files.includes('xray1.png') ? `/data/${dataset}/${patientId}/xray1.png` : null;
      const xray2 = files.includes('xray2.png') ? `/data/${dataset}/${patientId}/xray2.png` : null;
      const frontal = files.includes('frontal.png') ? `/data/${dataset}/${patientId}/frontal.png` : null;
      const lateral = files.includes('lateral.png') ? `/data/${dataset}/${patientId}/lateral.png` : null;

      // Clean patient ID - remove _ct_xray_data suffix if present
      const cleanPatientId = patientId.replace(/_ct_xray_data$/, '');

      return {
        id: cleanPatientId,
        fakeSlices,
        gtSlices,
        xray1,
        xray2,
        frontal,
        lateral,
      };
    });

    return NextResponse.json({ patients });
  } catch (error) {
    console.error('Error reading directory:', error);
    return NextResponse.json({ patients: [], error: 'Failed to read directory' }, { status: 500 });
  }
}
