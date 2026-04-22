import ImageGallery from '@/components/ImageGallery';

export default function MixedTest() {
  return (
    <ImageGallery
      dataset="mixed-test"
      title="Mixed Training - Mixed Test Set"
      description="These samples are from the Mixed / Model Test Set (222 samples). The dataset provides paired X-rays and reference CTs - compare generated CT slices (blue) with ground-truth CT slices (green). The mixed model evaluated here was trained on both synthetic and real data. Note: the test split includes the same 20 real X-ray cases used in the Real Test Set."
      showGroundTruth={true}
      xrayLabels={{ xray1: 'X-Ray 1 (AP View)', xray2: 'X-Ray 2 (Lateral View)' }}
    />
  );
}