#!/usr/bin/env bash
# Generate preview images for each model on its test results

## original

python3 preview.py \
  ./outputs/results/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/d2_multiview2500 \
  ./outputs/previews/d2_multiview2500

## synthetic

python3 preview.py \
  ./outputs/results/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted \
  ./outputs/previews/multiview-GAN-dataset-complete-clipped-shifted

## real

python3 preview.py \
  ./outputs/results/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted-real \
  ./outputs/previews/multiview-GAN-dataset-complete-clipped-shifted-real

## mixed

python3 preview.py \
  ./outputs/results/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted-real_mixed \
  ./outputs/previews/multiview-GAN-dataset-complete-clipped-shifted-real_mixed

# Test each model on the real subset of the test set

## original -> might be "data leak" from same patient, but since input is real x-rays instead of the original dataset DRRs, the idea here is to test how the model performs on new unseen real x-rays

python3 preview.py \
  ./outputs/results/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/d2_multiview2500-real-test \
  ./outputs/previews/d2_multiview2500-real-test

## synthetic

python3 preview.py \
  ./outputs/results/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted-real-test \
  ./outputs/previews/multiview-GAN-dataset-complete-clipped-shifted-real-test

## real (DO NOT USE, BASICALLY THE SAME AS THE EACH MODEL ON ITS OWN SUBSET)

python3 preview.py \
   ./outputs/results/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted-real-real-test \
   ./outputs/previews/multiview-GAN-dataset-complete-clipped-shifted-real-real-test

## mixed

python3 preview.py \
  ./outputs/results/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted-real_mixed-real-test \
  ./outputs/previews/multiview-GAN-dataset-complete-clipped-shifted-real_mixed-real-test