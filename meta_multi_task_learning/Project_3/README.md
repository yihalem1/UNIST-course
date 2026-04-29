# Project 3 — Few-shot Image Classification on miniImageNet

## What this project is about

The task is **5-way 1-shot image classification on miniImageNet**: given only 1 labeled
"support" image per class for 5 unseen classes, classify 15 "query" images per class.
The goal is to learn an embedding that generalizes to novel classes without retraining.

This submission implements **Prototypical Networks (ProtoNet)** with a **ResNet-12**
backbone, **DropBlock** regularization, a **cosine** similarity metric with a learnable
scale, label smoothing, SGD with cosine-annealed learning rate, and 95% confidence
intervals computed across multiple seeds.

The final score is graded by the course's formula:

```
final_score = 70.0 × acc_score × time_score × param_score
```

with hard cutoffs at **50% accuracy** and **9 hours** of training time.

## Method summary

| Component | Choice |
|---|---|
| Algorithm | Prototypical Networks (ProtoNet) |
| Backbone | ResNet-12 (4 residual blocks, channels 64→128→256→512, GAP) |
| Regularization | DropBlock (block_size=5, ramped per stage) + label smoothing 0.1 + grad-clip 5.0 |
| Distance metric | Cosine similarity with learnable, clamped scale (softplus, [1, 50]) |
| Episode setup (train) | N-way = 20, K-shot = 1, Q = 15 query per class |
| Episode setup (test) | 5-way 1-shot, 15 query, 5000 test episodes |
| Optimizer | SGD (momentum 0.9, Nesterov, weight decay 5e-4) |
| LR schedule | Cosine annealing over 20,000 episodes, lr = 0.05 |
| Data augmentation | Random crop / flip / color jitter on the 84×84 inputs |
| Evaluation | Mean ± 95% CI across seeds {0, 1, 2} |

## Files

| File | Purpose |
|---|---|
| [submission/miniimagenet.py](submission/miniimagenet.py) | Main entry point — training loop, evaluation, scoring, CI mode |
| [submission/models.py](submission/models.py) | `CNN` and `ResNet12` backbones, `DropBlock2D` |
| [submission/data_sampling.py](submission/data_sampling.py) | Episode sampler / `DataSampling` wrapper |
| [submission/miniimagenet_dataloader.py](submission/miniimagenet_dataloader.py) | miniImageNet dataloader (with augmentation toggle) |
| [submission/utils.py](submission/utils.py) | Support/query split helpers |
| [submission/report.pdf](submission/report.pdf) | Written report with results and ablations |
| [Project3_Guideline.pdf](Project3_Guideline.pdf) | Original course assignment guideline |

## How to run

```bash
# Single run, default config
python miniimagenet.py

# 95% CI across 3 seeds (graduate bonus)
python miniimagenet.py --ci_seeds 0,1,2

# Ablation: disable augmentation
python miniimagenet.py --no_aug

# Ablation: simple 4-conv CNN backbone instead of ResNet-12
python miniimagenet.py --backbone cnn
```

Requires a CUDA-capable GPU (`run_once` asserts `torch.cuda.is_available()`).

See `submission/report.pdf` for full numerical results, ablations, and the 95% CI.
