import ImageGallery from '@/components/ImageGallery';

export default function RealIndiana() {
  return (
    <ImageGallery
      dataset="real-indiana"
      title="Real Trained - Indiana University"
      description="These samples are from the Indiana University chest X-ray dataset. The model was trained on real patient X-ray data and applied to this external dataset. Reference CT volumes are not available; only generated CTs are shown."
      showGroundTruth={false}
      xrayLabels={{ xray1: 'Frontal View', xray2: 'Lateral View' }}
    />
  );
}