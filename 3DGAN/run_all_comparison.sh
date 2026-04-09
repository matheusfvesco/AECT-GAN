#!/usr/bin/env bash
# Generate comparison visuals - all 4 model variants on the same dataset
# The script iterates over variants internally

## Run on real dataset (GAN-dataset-complete-clipped-shifted-real) with real_test.txt
python3 comparison_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --dataroot=./data/GAN-dataset-complete-clipped-shifted-real \
  --dataset=test \
  --tag=comparison_real \
  --result_subdir=real-test \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --datasetfile=./data/real_test.txt \
  --resultdir=./save_models/multiView_CTGAN \
  --check_point=90 \
  --how_many=50 \
  --model_root=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN
