import ImageGallery from '@/components/ImageGallery';

export default function RealIndiana() {
  return (
    <ImageGallery
      dataset="real-indiana"
      title="Real Trained - Indiana University"
      description="Samples were generated from Indiana University chest X-rays (external clinical data). The real-trained model was applied to this dataset. Reference CTs are not available; only model-generated CTs are displayed."
      showGroundTruth={false}
      xrayLabels={{ xray1: 'Frontal View', xray2: 'Lateral View' }}
    />
  );
}