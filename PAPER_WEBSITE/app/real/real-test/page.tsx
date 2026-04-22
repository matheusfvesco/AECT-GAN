import ImageGallery from '@/components/ImageGallery';

export default function RealRealTest() {
  return (
    <ImageGallery
      dataset="real-real-test"
      title="Real Trained - Real Test Set"
      description="These samples are from the Real Test Set (20 patients). Compare generated CT slices (blue) with ground-truth CT slices (green). The real model evaluated here was trained exclusively on real patient X-rays."
      showGroundTruth={true}
      xrayLabels={{ xray1: 'X-Ray 1 (AP View)', xray2: 'X-Ray 2 (Lateral View)' }}
    />
  );
}