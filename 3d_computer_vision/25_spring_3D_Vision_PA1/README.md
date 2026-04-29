# PA1 — Feature Matching, Homography & Augmented Reality

## What this assignment is about

A classic 2D projective-geometry pipeline built end-to-end: detect and describe keypoints,
match them across views, robustly estimate a planar **homography**, and use it for two
downstream applications — **AR overlay** ("Harry-Potterize" a book cover, then a video
frame onto every frame of a clip) and **multi-image panorama stitching**.

The core building blocks implemented from scratch:

- **BRIEF** descriptor matching on FAST keypoints (with rotation / noise sensitivity tests)
- **DLT** for homography estimation (4-point and normalized variants)
- **RANSAC** for robust homography fitting under outliers
- AR pipeline: per-frame homography → warp source video → composite onto target video
- Panorama: pairwise homographies → cylindrical / planar warping → multi-image blending
- Degenerate-configuration analysis (when homography estimation breaks)

## Files

| File | Purpose |
|---|---|
| [submission/Q5_featureMatching.py](submission/Q5_featureMatching.py) | BRIEF feature matching between two views |
| [submission/Q6_briefRotTest.py](submission/Q6_briefRotTest.py) | BRIEF rotation-invariance experiment |
| [submission/Q7_briefNoiseTest.py](submission/Q7_briefNoiseTest.py) | BRIEF noise-robustness experiment |
| [submission/Q9_ComputeH.py](submission/Q9_ComputeH.py) | DLT homography from 4+ point correspondences |
| [submission/Q10_ComputeH_norm.py](submission/Q10_ComputeH_norm.py) | Normalized DLT (Hartley pre-conditioning) |
| [submission/Q11_RANSAC.py](submission/Q11_RANSAC.py) | RANSAC wrapper around the homography solver |
| [submission/Q12_HarryPotterize.py](submission/Q12_HarryPotterize.py) | Warp HP cover onto CV-textbook image |
| [submission/Q13_ar.py](submission/Q13_ar.py) | Per-frame AR video overlay |
| [submission/Q14_Panaroma.py](submission/Q14_Panaroma.py) | Two-image panorama stitching |
| [submission/Q15_Multi_panorama.py](submission/Q15_Multi_panorama.py) | Multi-image panorama (chained homographies) |
| [submission/Q16_Degenerate.py](submission/Q16_Degenerate.py) | Degenerate-case analysis |
| [submission/matchPics.py](submission/matchPics.py) | Shared FAST + BRIEF detect/describe/match helper |
| [submission/planarH.py](submission/planarH.py) | Homography utilities (DLT, normalized DLT, RANSAC, warping/compositing) |
| [submission/helper.py](submission/helper.py) | Plotting / visualization helpers |
| [submission/loadVid.py](submission/loadVid.py) | Video → frame-array loader |
| [submission/report.pdf](submission/report.pdf) | Written report with results and figures |

> The course-provided `data/` folder (image / video inputs) and the generated
> `result/` folder (rendered AR clip and panorama PNGs) are not included in this
> repo to keep it lightweight — they are reproducible from the code above plus the
> course-supplied inputs.

## How to run

Each `Q*.py` is a standalone script (run from inside `submission/`). Example:

```bash
cd submission
python Q5_featureMatching.py
python Q12_HarryPotterize.py
python Q13_ar.py
python Q15_Multi_panorama.py
```

Requires `opencv-python`, `numpy`, `scipy`, `scikit-image`, `matplotlib`.

See `submission/report.pdf` for results, intermediate visualizations, and analysis.
