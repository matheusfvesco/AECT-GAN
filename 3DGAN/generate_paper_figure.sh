#!/usr/bin/env bash

cd /home/matheus/Documents/Projects/AECT-GAN/3DGAN

# Indiana cases
python generate_indiana_paper_figure.py \
    --patient_id CXR1070 \
    --num_slices 6

python generate_indiana_paper_figure.py \
    --patient_id CXR1074 \
    --num_slices 6

# Real test cases (real x-rays, real test.txt)
python generate_comparison_figure.py \
    --tag real_test \
    --patient_id LIDC-IDRI-0013 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted-real \
    --datasetfile data/real_test.txt

# Synthetic test cases (synthetic x-rays, synthetic_test.txt)
python generate_comparison_figure.py \
    --tag synthetic_test \
    --patient_id LIDC-IDRI-0013 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted \
    --datasetfile data/synthetic_test.txt

# Real test cases (real x-rays, real test.txt)
python generate_comparison_figure.py \
    --tag real_test \
    --patient_id LIDC-IDRI-0105 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted-real \
    --datasetfile data/real_test.txt

# Synthetic test cases (synthetic x-rays, synthetic_test.txt)
python generate_comparison_figure.py \
    --tag synthetic_test \
    --patient_id LIDC-IDRI-0105 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted \
    --datasetfile data/synthetic_test.txt

# Real test cases (real x-rays, real test.txt)
python generate_comparison_figure.py \
    --tag real_test \
    --patient_id LIDC-IDRI-0194 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted-real \
    --datasetfile data/real_test.txt

# Synthetic test cases (synthetic x-rays, synthetic_test.txt)
python generate_comparison_figure.py \
    --tag synthetic_test \
    --patient_id LIDC-IDRI-0194 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted \
    --datasetfile data/synthetic_test.txt

#############
# Samples that are also in the original test set


python generate_comparison_figure.py \
    --tag synthetic_test \
    --patient_id LIDC-IDRI-0040 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted \
    --datasetfile data/synthetic_test.txt \
    --original

python generate_comparison_figure.py \
    --tag real_test \
    --patient_id LIDC-IDRI-0040 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted-real \
    --datasetfile data/real_test.txt




#################################

python generate_comparison_figure.py \
    --tag synthetic_test \
    --patient_id LIDC-IDRI-0535 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted \
    --datasetfile data/synthetic_test.txt \
    --original

python generate_comparison_figure.py \
    --tag synthetic_test \
    --patient_id LIDC-IDRI-0720 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted \
    --datasetfile data/synthetic_test.txt \
    --original

python generate_comparison_figure.py \
    --tag synthetic_test \
    --patient_id LIDC-IDRI-0983 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted \
    --datasetfile data/synthetic_test.txt \
    --original

python generate_comparison_figure.py \
    --tag synthetic_test \
    --patient_id LIDC-IDRI-1007 \
    --num_slices 6 \
    --dataroot data/GAN-dataset-complete-clipped-shifted \
    --datasetfile data/synthetic_test.txt \
    --original