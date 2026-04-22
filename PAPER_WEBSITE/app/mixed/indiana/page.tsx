import ImageGallery from '@/components/ImageGallery';

export default function MixedIndiana() {
  return (
    <ImageGallery
      dataset="mixed-indiana"
      title="Mixed Training - Indiana University"
      description="Samples were generated from Indiana University chest X-rays (external clinical data). Reference CTs are not available; only model-generated CT slices are shown. The mixed model evaluated here was trained on both synthetic and real data."
      showGroundTruth={false}
      xrayLabels={{ frontal: 'Frontal View', lateral: 'Lateral View' }}
    />
  );
}
