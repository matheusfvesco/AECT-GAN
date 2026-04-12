import ImageGallery from '@/components/ImageGallery';

export default function SyntheticIndiana() {
  return (
    <ImageGallery
      dataset="synthetic-indiana"
      title="Synthetic Trained - Indiana University"
      description="These samples were generated from X-rays from the Indiana University chest X-ray dataset. Reference CT volumes are not available for this dataset, so only generated CT slices are shown."
      showGroundTruth={false}
      xrayLabels={{ frontal: 'Frontal View', lateral: 'Lateral View' }}
    />
  );
}
