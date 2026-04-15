import ImageGallery from '@/components/ImageGallery';

export default function SyntheticTest() {
  return (
    <ImageGallery
      dataset="synthetic-test"
      title="Synthetic Trained - Synthetic Test Set"
      description="These samples are from the synthetic test set containing paired X-rays and reference CT volumes. You can compare the generated CT slices (blue) with the ground truth CT slices (green)."
      showGroundTruth={true}
      xrayLabels={{ xray1: 'X-Ray 1 (AP View)', xray2: 'X-Ray 2 (Lateral View)' }}
    />
  );
}