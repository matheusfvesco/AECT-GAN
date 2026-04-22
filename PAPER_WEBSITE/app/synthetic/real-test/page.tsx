import ImageGallery from '@/components/ImageGallery';

export default function SyntheticRealTest() {
  return (
    <ImageGallery
      dataset="synthetic-real-test"
      title="Synthetic Trained - Real Test Set"
      description="These samples are from the Real Test Set (20 patients). Each case contains real X-rays as inputs and paired reference CTs - compare generated CT slices (blue) with ground-truth CT slices (green)."
      showGroundTruth={true}
      xrayLabels={{ xray1: 'X-Ray 1 (AP View)', xray2: 'X-Ray 2 (Lateral View)' }}
    />
  );
}
