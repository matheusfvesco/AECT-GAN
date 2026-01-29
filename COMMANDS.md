# COMMANDS.md

## AECT-GAN: Example Commands

This file lists concise example commands for running and training AECT-GAN. The following are for the LIDC-IDRI dataset. For other datasets, add similar commands below.

---

### Test (LIDC-IDRI)
Single-view:
```bash
python3 test.py --ymlpath=./experiment/singleview2500/d2_singleview2500.yml --gpu=0 --dataroot=./data/LIDC-HDF5-256 --dataset=test --tag=d2_singleview2500_lidc --data=data/chengsq/AECT-GAN/model_dic/Sig_AECT-GAN --dataset_class=align_ct_xray_std --model_class=SingleView-AECT-GAN --datasetfile=./data/test.txt --resultdir=./save_models/singleView_CTGAN --check_point=90 --how_many=3 --load_path=./save_models/singleView_CTGAN/data/chengsq/AECT-GAN/model_dic/Sig_AECT-GAN/d2_singleview2500/checkpoint
```
Multi-view:
```bash
python3 test.py --ymlpath=./experiment/multiview2500/d2_multiview2500.yml --gpu=0 --dataroot=./data/LIDC-HDF5-256 --dataset=test --tag=d2_multiview2500_lidc --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN --dataset_class=align_ct_xray_views_std --model_class=MultiView-AECT-GAN --datasetfile=./data/test.txt --resultdir=./save_models/multiView_CTGAN --check_point=90 --how_many=3 --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/d2_multiview2500/checkpoint
```

### Train (LIDC-IDRI)
Single-view:
```bash
nohup python train.py --ymlpath=experiment/singleview2500/d2_singleview2500.yml --gpu=0 --dataroot=./data/LIDC-HDF5-256 --dataset=train --tag=d2_singleview2500_lidc --data=data/chengsq/AECT-GAN/model_dic/Sig_AECT-GAN --dataset_class=align_ct_xray_std --model_class=SingleView-AECT-GAN --datasetfile=./data/train.txt --valid_datasetfile=./data/test.txt --valid_dataset=test &
```
Multi-view:
```bash
nohup python train.py --ymlpath=experiment/multiview2500/d2_multiview2500.yml --gpu=0 --dataroot=./data/LIDC-HDF5-256 --dataset=train --tag=d2_multiview2500_lidc --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN --dataset_class=align_ct_xray_views_std --model_class=MultiView-AECT-GAN --datasetfile=./data/train.txt --valid_datasetfile=./data/test.txt --valid_dataset=test &
```

---

Add commands for other datasets below as needed.

---

### Test (GAN-dataset-complete-new-unnorm, synthetic)
Single-view:
```bash
python3 test.py --ymlpath=./experiment/singleview2500/d2_singleview2500.yml --gpu=0 --dataroot=./data/GAN-dataset-complete-new-unnorm --dataset=test --tag=d2_singleview2500_synthetic --data=data/chengsq/AECT-GAN/model_dic/Sig_AECT-GAN --dataset_class=align_ct_xray_std --model_class=SingleView-AECT-GAN --datasetfile=./data/synthetic_test.txt --resultdir=./save_models/singleView_CTGAN --check_point=90 --how_many=3 --load_path=./save_models/singleView_CTGAN/data/chengsq/AECT-GAN/model_dic/Sig_AECT-GAN/d2_singleview2500/checkpoint
```
Multi-view:
```bash
python3 test.py --ymlpath=./experiment/multiview2500/d2_multiview2500.yml --gpu=0 --dataroot=./data/GAN-dataset-complete-new-unnorm --dataset=test --tag=d2_multiview2500_synthetic --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN --dataset_class=align_ct_xray_views_std --model_class=MultiView-AECT-GAN --datasetfile=./data/synthetic_test.txt --resultdir=./save_models/multiView_CTGAN --check_point=90 --how_many=3 --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/d2_multiview2500/checkpoint
```

### Train (GAN-dataset-complete-new-unnorm, synthetic)
Single-view:
```bash
nohup python train.py --ymlpath=experiment/singleview2500/d2_singleview2500.yml --gpu=0 --dataroot=./data/GAN-dataset-complete-new-unnorm --dataset=train --tag=d2_singleview2500_synthetic --data=data/chengsq/AECT-GAN/model_dic/Sig_AECT-GAN --dataset_class=align_ct_xray_std --model_class=SingleView-AECT-GAN --datasetfile=./data/synthetic_train.txt --valid_datasetfile=./data/synthetic_test.txt --valid_dataset=test &
```
Multi-view:
```bash
nohup python train.py --ymlpath=experiment/multiview2500/d2_multiview2500.yml --gpu=0 --dataroot=./data/GAN-dataset-complete-new-unnorm --dataset=train --tag=d2_multiview2500_synthetic --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN --dataset_class=align_ct_xray_views_std --model_class=MultiView-AECT-GAN --datasetfile=./data/synthetic_train.txt --valid_datasetfile=./data/synthetic_test.txt --valid_dataset=test &
```

---

### Test (GAN-dataset-complete-new-real-unnorm, real)
Single-view:
```bash
python3 test.py --ymlpath=./experiment/singleview2500/d2_singleview2500.yml --gpu=0 --dataroot=./data/GAN-dataset-complete-new-real-unnorm --dataset=test --tag=d2_singleview2500_real --data=data/chengsq/AECT-GAN/model_dic/Sig_AECT-GAN --dataset_class=align_ct_xray_std --model_class=SingleView-AECT-GAN --datasetfile=./data/real_test.txt --resultdir=./save_models/singleView_CTGAN --check_point=90 --how_many=3 --load_path=./save_models/singleView_CTGAN/data/chengsq/AECT-GAN/model_dic/Sig_AECT-GAN/d2_singleview2500/checkpoint
```
Multi-view:
```bash
python3 test.py --ymlpath=./experiment/multiview2500/d2_multiview2500.yml --gpu=0 --dataroot=./data/GAN-dataset-complete-new-real-unnorm --dataset=test --tag=d2_multiview2500_real --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN --dataset_class=align_ct_xray_views_std --model_class=MultiView-AECT-GAN --datasetfile=./data/real_test.txt --resultdir=./save_models/multiView_CTGAN --check_point=90 --how_many=3 --load_path=./save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN/d2_multiview2500/checkpoint
```

### Train (GAN-dataset-complete-new-real-unnorm, real)
Single-view:
```bash
nohup python train.py --ymlpath=experiment/singleview2500/d2_singleview2500.yml --gpu=0 --dataroot=./data/GAN-dataset-complete-new-real-unnorm --dataset=train --tag=d2_singleview2500_real --data=data/chengsq/AECT-GAN/model_dic/Sig_AECT-GAN --dataset_class=align_ct_xray_std --model_class=SingleView-AECT-GAN --datasetfile=./data/real_train.txt --valid_datasetfile=./data/real_test.txt --valid_dataset=test &
```
Multi-view:
```bash
nohup python train.py --ymlpath=experiment/multiview2500/d2_multiview2500.yml --gpu=0 --dataroot=./data/GAN-dataset-complete-new-real-unnorm --dataset=train --tag=d2_multiview2500_real --data=data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN --dataset_class=align_ct_xray_views_std --model_class=MultiView-AECT-GAN --datasetfile=./data/real_train.txt --valid_datasetfile=./data/real_test.txt --valid_dataset=test &
```
