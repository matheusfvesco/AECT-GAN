#!/usr/bin/env bash
# Generate supplementary visuals for each model on its own test subset

## original

python3 supplementary_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --dataroot=./data/LIDC-HDF5-256 \
  --dataset=test \
  --tag=d2_multiview2500 \
  --result_subdir=test \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --datasetfile=./data/test.txt \
  --resultdir=./save_models/multiView_CTGAN \
  --check_point=90 \
  --how_many=102 \
  --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/d2_multiview2500/checkpoint

## synthetic

python3 supplementary_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --dataroot=./data/GAN-dataset-complete-clipped-shifted \
  --dataset=test \
  --tag=multiview-GAN-dataset-complete-clipped-shifted \
  --result_subdir=test \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --datasetfile=./data/synthetic_test.txt \
  --resultdir=./save_models/multiView_CTGAN \
  --check_point=90 \
  --how_many=222 \
  --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted/checkpoint

## real

python3 supplementary_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --dataroot=./data/GAN-dataset-complete-clipped-shifted-real \
  --dataset=test \
  --tag=multiview-GAN-dataset-complete-clipped-shifted-real \
  --result_subdir=test \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --datasetfile=./data/real_test.txt \
  --resultdir=./save_models/multiView_CTGAN \
  --check_point=90 \
  --how_many=20 \
  --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted-real/checkpoint

## mixed

python3 supplementary_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --dataroot=./data/GAN-dataset-complete-clipped-shifted-real_mixed \
  --dataset=test \
  --tag=multiview-GAN-dataset-complete-clipped-shifted-real_mixed \
  --result_subdir=test \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --datasetfile=./data/mixed_test.txt \
  --resultdir=./save_models/multiView_CTGAN \
  --check_point=90 \
  --how_many=222 \
  --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted-real_mixed/checkpoint

# Test each model on the real subset of the test set

## original -> might be "data leak" from same patient, but since input is real x-rays instead of the original dataset DRRs, the idea here is to test how the model performs on new unseen real x-rays

python3 supplementary_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --dataroot=./data/GAN-dataset-complete-clipped-shifted-real \
  --dataset=test \
  --tag=d2_multiview2500 \
  --result_subdir=real-test \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --datasetfile=./data/real_test.txt \
  --resultdir=./save_models/multiView_CTGAN \
  --check_point=90 \
  --how_many=50 \
  --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/d2_multiview2500/checkpoint

## synthetic

python3 supplementary_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --dataroot=./data/GAN-dataset-complete-clipped-shifted-real \
  --dataset=test \
  --tag=multiview-GAN-dataset-complete-clipped-shifted \
  --result_subdir=real-test \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --datasetfile=./data/real_test.txt \
  --resultdir=./save_models/multiView_CTGAN \
  --check_point=90 \
  --how_many=50 \
  --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted/checkpoint

## real (DO NOT USE, BASICALLY THE SAME AS THE EACH MODEL ON ITS OWN SUBSET)

# python3 supplementary_visuals.py \
#   --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
#   --gpu=0 \
#   --dataroot=./data/GAN-dataset-complete-clipped-shifted-real \
#   --dataset=test \
#   --tag=multiview-GAN-dataset-complete-clipped-shifted-real \
#   --result_subdir=real-test \
#   --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
#   --dataset_class=align_ct_xray_views_std \
#   --model_class=MultiView-AECT-GAN \
#   --datasetfile=./data/real_test.txt \
#   --resultdir=./save_models/multiView_CTGAN \
#   --check_point=90 \
#   --how_many=50 \
#   --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted-real/checkpoint

## mixed

python3 supplementary_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --dataroot=./data/GAN-dataset-complete-clipped-shifted-real \
  --dataset=test \
  --tag=multiview-GAN-dataset-complete-clipped-shifted-real_mixed \
  --result_subdir=real-test \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --datasetfile=./data/real_test.txt \
  --resultdir=./save_models/multiView_CTGAN \
  --check_point=90 \
  --how_many=50 \
  --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted-real_mixed/checkpoint