export interface X2CTMetrics {
  MAE: number;
  MSE: number;
  Cosine_Similarity: number;
  SSIM: number;
  PSNR_3D: number;
  model_type: 'real' | 'synthetic' | 'mixed';
}

export interface X2CTXrays {
  frontal: string;
  lateral: string;
}

export interface X2CTDimensions {
  depth: number;
  height: number;
  width: number;
}

export interface X2CTResponse {
  status: 'ok';
  metrics: X2CTMetrics;
  xrays: X2CTXrays;
  ct: {
    generated: string[];
    original: string[];
  };
  dimensions: X2CTDimensions;
}

// New type for /predict endpoint response (no metrics, no original CT)
export interface X2CTPredictResponse {
  status: 'ok';
  model_type: 'real' | 'synthetic' | 'mixed';
  xrays: X2CTXrays;
  ct: {
    generated: string[];
  };
  dimensions: X2CTDimensions;
}

export interface UploadState {
  isLoading: boolean;
  progress: number;
  error: string | null;
  result: X2CTResponse | null;
}
