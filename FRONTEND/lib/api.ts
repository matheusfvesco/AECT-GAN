import { X2CTResponse, X2CTPredictResponse } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface UploadResult {
  success: boolean;
  data?: X2CTResponse;
  error?: string;
}

export interface PredictResult {
  success: boolean;
  data?: X2CTPredictResponse;
  error?: string;
}

// Evaluate endpoint - calls /evaluate
export async function uploadZip(file: File, modelType: 'real' | 'synthetic' | 'mixed' = 'real'): Promise<UploadResult> {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_type', modelType);

    const response = await fetch(`${API_URL}/evaluate`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      return { success: false, error: errorText || `HTTP ${response.status}` };
    }

    const data: X2CTResponse = await response.json();
    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error occurred';
    return { success: false, error: message };
  }
}

// Predict endpoint - calls /predict (no metrics)
export async function uploadZipPredict(file: File, modelType: 'real' | 'synthetic' | 'mixed' = 'real'): Promise<PredictResult> {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_type', modelType);

    const response = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      return { success: false, error: errorText || `HTTP ${response.status}` };
    }

    const data: X2CTPredictResponse = await response.json();
    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error occurred';
    return { success: false, error: message };
  }
}

export function getDataUrl(base64: string, mimeType: string = 'image/jpeg'): string {
  return `data:${mimeType};base64,${base64}`;
}
