export const SITE = {
  title: 'AECT-GAN',
  tagline: 'Addressing Domain Shift in Dual‑View X‑ray to CT Reconstruction',
  home: {
    heroHeading: 'Reconstruct CT from X‑rays',
    heroDescription:
      'AECT‑GAN (Cheng et al.) is used to study domain shift in dual‑view X‑ray to CT reconstruction with real X‑rays. Use Evaluate to compare model output to a reference CT volume, or Predict for inference‑only reconstruction.',
    evaluateCard: {
      title: 'Evaluate',
      description:
        'Upload a DICOM CT scan plus frontal and lateral X‑rays to evaluate model performance and compute metrics.',
      bullets: [
        'Requires a CT scan and frontal + lateral X‑rays',
        'Returns evaluation metrics (MAE, MSE, SSIM, PSNR, etc.)',
        'Compares generated CT to the reference (original) CT',
      ],
      button: 'Go to Evaluate',
    },
    predictCard: {
      title: 'Predict',
      description:
        'Upload frontal and lateral X‑ray images (DICOM or JPEG/PNG) to generate a CT volume (no evaluation metrics).',
      bullets: [
        'Accepts two X‑ray files (frontal + lateral)',
        'No metrics calculation (inference only)',
        'Faster inference',
      ],
      button: 'Go to Predict',
    },
  },
  footer: {
    privacy: 'AECT‑GAN Playground — Ephemeral processing. No data is stored.',
    clinical:
      'Provided strictly for research, educational, and demonstration purposes. Not a medical device. No warranty. Use is at your own risk.',
  },
  predict: {
    headerTitle: 'AECT‑GAN — Predict',
    sectionHeading: 'Generate CT from X‑rays',
    uploadInstructions:
      'Upload a ZIP containing two X‑ray images (frontal and lateral). Supported formats: DICOM, JPEG, or PNG.',
    inputXRays: 'Input X‑rays',
    generatedCT: 'Generated CT (reconstruction)',
    modelUsed: 'Model used:',
    dimensions: 'CT dimensions: {depth} × {height} × {width} voxels',
    zipStructure: 'ZIP File Structure',
    zipInstruction: 'Your ZIP must contain exactly two X‑ray files:',
    dicomMode: 'DICOM mode:',
    dicomModeDesc: 'Two DICOM X‑ray files',
    imageMode: 'Image mode:',
    imageModeDesc: 'Two JPEG or PNG images',
    browse: 'Select ZIP',
    noFileSelected: 'No file selected',
    modelType: 'Model type',
    errorPrefix: 'Error:',
    processing: 'Processing…',
    generateCT: 'Generate CT',
    home: 'Home',
    newUpload: 'New Upload',
  },
  evaluate: {
    headerTitle: 'AECT‑GAN — Evaluate',
    sectionHeading: 'Evaluate CT Reconstruction',
    uploadInstructions:
      'Upload a ZIP containing a DICOM CT scan and frontal + lateral X‑rays.',
    inputXRays: 'Input X‑rays',
    evaluationMetrics: 'Evaluation Metrics',
    ctComparison: 'CT Comparison (generated vs reference)',
    dimensions: 'CT dimensions: {depth} × {height} × {width} voxels',
    home: 'Home',
    newUpload: 'New Upload',
  },
};

export const MODELS = {
  real: {
    label: 'Real model',
    samples: '182 real X‑ray pairs',
    tooltip:
      'Trained on 182 real X‑ray pairs. Performance on other datasets may vary.',
    optionLabel: 'Real — Trained on 182 real X‑ray pairs',
    description:
      'Real model: Trained on frontal/lateral X‑ray pairs acquired from patients. Performance on different datasets may vary; this model is not validated for clinical use.',
  },
  synthetic: {
    label: 'Synthetic model',
    samples: '2006 DRR pairs',
    tooltip:
      'Trained on 2006 DRR pairs. DRRs are synthetic and may differ from real X‑rays.',
    optionLabel: 'Synthetic — Trained on 2006 DRR pairs',
    description:
      'Synthetic model: Trained on Digitally Reconstructed Radiographs (DRRs) generated from CT scans. DRRs are synthetic and may differ visually and statistically from real X‑rays.',
  },
  mixed: {
    label: 'Mixed model',
    samples: '182 real + 1824 DRR pairs (2006 total)',
    tooltip: 'Trained on 182 real + 1824 DRR pairs (2006 total).',
    optionLabel: 'Mixed — 182 real + 1824 DRR pairs (2006 total)',
    description:
      'Mixed model: Trained on a combination of 182 real pairs and 1824 DRR pairs (2006 total). Intended to combine characteristics of both datasets.',
  },
};

export const METRICS = {
  MAE: 'Mean Absolute Error (MAE)',
  MSE: 'Mean Squared Error (MSE)',
  Cosine_Similarity: 'Cosine Similarity',
  SSIM: 'Structural Similarity Index (SSIM)',
  PSNR_3D: 'PSNR (3D, dB)',
};

export const CTSYNCVIEWER = {
  sliceIndicator: 'Slice {current} of {total}',
  sizeButtons: ['128 × 128', '256 × 256', '512 × 512'],
  resizeNotice: 'Displayed (resized from 128 × 128)',
  generatedCT: 'Generated CT (reconstruction)',
  originalCT: 'Original CT (reference)',
  hintWheel: 'Use the mouse wheel or drag the slider',
  hintArrow: 'Arrow keys for stepwise navigation',
  hintHomeEnd: 'Home / End keys go to first / last slice',
};

export const XRAYVIEWER = {
  frontalLabel: 'Frontal View',
  lateralLabel: 'Lateral View',
  frontalAlt: 'Frontal X‑ray',
  lateralAlt: 'Lateral X‑ray',
};

export const FILEUPLOADER = {
  zipStructure: 'ZIP File Structure',
  zipInstruction: 'Your ZIP must include 2–3 DICOM directories:',
  ctScan: '1 CT scan (DICOM)',
  ctScanRequirement: 'Must contain at least 10 DICOM files',
  xrayViews: '1–2 X‑ray views',
  multiviewOption:
    'One multiview directory containing both frontal and lateral X‑rays, OR',
  separateOption:
    'Two separate directories: one frontal, one lateral X‑ray',
  browse: 'Select ZIP',
  noFileSelected: 'No file selected',
  modelType: 'Model type',
  processing: 'Processing…',
  uploadAndProcess: 'Upload & Process',
};

export const DISCLAIMER = {
  title: 'Important Disclaimer',
  sections: [
    {
      heading: '',
      content:
        'This software and its outputs are provided strictly for research, educational, and demonstration purposes. The model generates synthetic CT volumes from X-ray inputs using an experimental deep learning method. The generated outputs are not real medical images and may contain significant artifacts, inaccuracies, or misleading structures.',
    },
    {
      heading: 'Not for Medical Use',
      content:
        'This software is **not a medical device** and has not been evaluated or approved by any regulatory authority (including, but not limited to, the FDA or equivalent bodies). It must not be used for:',
      bullets: [
        'Medical diagnosis',
        'Treatment planning',
        'Clinical decision-making',
        'Any form of patient care or medical workflow',
      ],
      prohibited: true,
    },
    {
      heading: 'No Warranty',
      content:
        'This software is provided "as is," without warranty of any kind, express or implied, including but not limited to accuracy, reliability, fitness for a particular purpose, or non-infringement.',
    },
    {
      heading: 'Limitation of Liability',
      content:
        'In no event shall the authors or contributors be liable for any claim, damages, or other liability arising from, out of, or in connection with the software or its use.',
    },
    {
      heading: 'User Responsibility',
      content: 'Users are solely responsible for:',
      bullets: [
        'Ensuring compliance with applicable laws and regulations',
        'Handling any medical or personal data appropriately',
        'Verifying that input data is used with proper authorization',
      ],
    },
    {
      heading: 'Acknowledgment',
      content:
        'By using this software, you acknowledge that you understand these limitations and agree to use it only for non-clinical research purposes.',
    },
  ],
  accept: 'I Understand and Accept',
};
