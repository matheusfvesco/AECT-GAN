import ImageGallery from '@/components/ImageGallery';

export default function SyntheticTest() {
  return (
    <ImageGallery
      dataset="synthetic-test"
      title="Synthetic Trained - Synthetic Test Set"
      description="These samples are from the Model Test Set (222 synthetic-input samples). Inputs are synthetic X-rays paired with reference CTs; compare generated CT slices (blue) with ground-truth CT slices (green). Note: this split includes synthetic versions of the 20 real-X-ray cases shown in the Real Test Set."
      showGroundTruth={true}
      xrayLabels={{ xray1: 'X-Ray 1 (AP View)', xray2: 'X-Ray 2 (Lateral View)' }}
    />
  );
}