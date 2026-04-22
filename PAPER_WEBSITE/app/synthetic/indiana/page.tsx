import ImageGallery from '@/components/ImageGallery';

export default function SyntheticIndiana() {
  return (
    <ImageGallery
      dataset="synthetic-indiana"
      title="Synthetic Trained - Indiana University"
      description="Samples were generated from Indiana University chest X-rays (external clinical data). Reference CTs are not available; only model-generated CT slices are shown."
      showGroundTruth={false}
      xrayLabels={{ frontal: 'Frontal View', lateral: 'Lateral View' }}
    />
  );
}
