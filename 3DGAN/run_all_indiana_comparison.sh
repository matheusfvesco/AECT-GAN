#!/usr/bin/env bash
# Generate comparison visuals for Indiana dataset - all 3 model variants on the same patients
# The script iterates over variants internally

python3 indiana_comparison_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --model_root=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --indiana_dir=./data/indiana_png \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --check_point=90 \
  --how_many=3405 \
  --cache=./data/indiana_xray_classification_cache.json \
  --tag=indiana_comparison