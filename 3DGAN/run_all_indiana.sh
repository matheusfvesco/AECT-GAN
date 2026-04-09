#!/usr/bin/env bash
# Run indiana_supplementary_visuals.py on each trained model (Section 1: each model on its own test subset)

## original

python3 indiana_supplementary_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --check_point=90 \
  --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/d2_multiview2500/checkpoint \
  --indiana_dir=./data/indiana_png \
  --how_many=3405 \
  --cache=./data/indiana_xray_classification_cache.json

## synthetic

python3 indiana_supplementary_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --check_point=90 \
  --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted/checkpoint \
  --indiana_dir=./data/indiana_png \
  --how_many=3405 \
  --cache=./data/indiana_xray_classification_cache.json

## real

python3 indiana_supplementary_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --check_point=90 \
  --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted-real/checkpoint \
  --indiana_dir=./data/indiana_png \
  --how_many=3405 \
  --cache=./data/indiana_xray_classification_cache.json

## mixed

python3 indiana_supplementary_visuals.py \
  --ymlpath=./experiment/multiview2500/d2_multiview2500.yml \
  --gpu=0 \
  --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN \
  --dataset_class=align_ct_xray_views_std \
  --model_class=MultiView-AECT-GAN \
  --check_point=90 \
  --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/multiview-GAN-dataset-complete-clipped-shifted-real_mixed/checkpoint \
  --indiana_dir=./data/indiana_png \
  --how_many=3405 \
  --cache=./data/indiana_xray_classification_cache.json