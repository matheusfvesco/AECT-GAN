import ImageGallery from '@/components/ImageGallery';

export default function MixedRealTest() {
  return (
    <ImageGallery
      dataset="mixed-real-test"
      title="Mixed Training - Real Test Set"
      description="These samples are from the Real Test Set (20 patients). Compare generated CT slices (blue) with ground-truth CT slices (green). The mixed model evaluated here was trained on both synthetic and real X-rays."
      showGroundTruth={true}
      xrayLabels={{ xray1: 'X-Ray 1 (AP View)', xray2: 'X-Ray 2 (Lateral View)' }}
    />
  );
}
