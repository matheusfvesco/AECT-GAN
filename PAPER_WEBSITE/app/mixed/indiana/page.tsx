import ImageGallery from '@/components/ImageGallery';

export default function MixedIndiana() {
  return (
    <ImageGallery
      dataset="mixed-indiana"
      title="Mixed Training - Indiana University"
      description="These samples were generated from X-rays from the Indiana University chest X-ray dataset. Reference CT volumes are not available for this dataset, so only generated CT slices are shown. The mixed model was trained on both synthetic and real data."
      showGroundTruth={false}
      xrayLabels={{ frontal: 'Frontal View', lateral: 'Lateral View' }}
    />
  );
}
