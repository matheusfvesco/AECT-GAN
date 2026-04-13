import ImageGallery from '@/components/ImageGallery';

export default function RealRealTest() {
  return (
    <ImageGallery
      dataset="real-real-test"
      title="Real Trained - Real Test Set"
      description="These samples are from the test set containing paired X-rays and reference CT volumes. You can compare the generated CT slices (blue) with the ground truth CT slices (green). The real model was trained exclusively on real patient X-ray data."
      showGroundTruth={true}
      xrayLabels={{ xray1: 'X-Ray 1 (AP View)', xray2: 'X-Ray 2 (Lateral View)' }}
    />
  );
}