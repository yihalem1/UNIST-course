# PA2 — 3D Reconstruction from Epipolar Geometry

## What this assignment is about

Two-view 3D reconstruction from a calibrated stereo pair, end-to-end: estimate the
**fundamental matrix** from point correspondences, recover the **essential matrix**
from intrinsics, **triangulate** matched points into 3D, **rectify** the image pair,
compute a dense **disparity / depth map**, and finally estimate camera **pose** with
PnP and **project** a CAD model back into the image.

Pipeline implemented:

- **Eight-point algorithm** (with Hartley normalization) for the fundamental matrix `F`
- **Epipolar correspondence search** along epipolar lines for additional matches
- **Essential matrix** `E = Kᵀ F K` and 3D **triangulation** via DLT
- **Stereo rectification** to align epipolar lines with image rows
- Dense **disparity** from windowed matching, then **depth** from the calibrated baseline
- **PnP pose estimation** from 3D-2D correspondences
- **CAD-model reprojection** as a qualitative sanity check on the recovered pose

## Files

| File | Purpose |
|---|---|
| [submission/Q1eight_point.py](submission/Q1eight_point.py) | Normalized eight-point algorithm for fundamental matrix `F` |
| [submission/Q2eppipolar_correspodences.py](submission/Q2eppipolar_correspodences.py) | Epipolar-line correspondence search |
| [submission/Q3essential_matrix.py](submission/Q3essential_matrix.py) | Essential matrix `E` from `F` and intrinsics |
| [submission/Q4triangulation.py](submission/Q4triangulation.py) | Linear triangulation (DLT) of 3D points |
| [submission/Q5results.py](submission/Q5results.py) | Reconstruction results and visualizations |
| [submission/Q6rectify.py](submission/Q6rectify.py) | Stereo rectification |
| [submission/Q7disparity.py](submission/Q7disparity.py) | Dense disparity map |
| [submission/Q8depth.py](submission/Q8depth.py) | Depth map from disparity + baseline |
| [submission/Q9estimate_pose.py](submission/Q9estimate_pose.py) | Camera pose estimation via PnP |
| [submission/Q10estimate_params.py](submission/Q10estimate_params.py) | Intrinsic / extrinsic decomposition |
| [submission/Q11project_cad.py](submission/Q11project_cad.py) | Project a CAD model into the image using the estimated pose |
| [submission/helper.py](submission/helper.py) | Shared epipolar-line / visualization utilities |
| [submission/report.pdf](submission/report.pdf) | Written report with results, figures, and analysis |
| [HW2_Guideline.pdf](HW2_Guideline.pdf) | Original course assignment guideline |

> The course-provided `data/` folder (`im1.png`, `im2.png`, `intrinsics.npz`,
> `some_corresp.npz`, `temple_coords.npz`, `pnp.npz`, …) and the rendered
> `results/` folder are not included in this repo — they are reproducible from
> the code above plus the course-supplied inputs.

## How to run

Each `Q*.py` is a standalone script (run from inside `submission/`, with the
course-provided `data/` placed alongside). Example:

```bash
cd submission
python Q1eight_point.py
python Q4triangulation.py
python Q7disparity.py
python Q11project_cad.py
```

Requires `opencv-python`, `numpy`, `scipy`, `matplotlib`.

See `submission/report.pdf` for full numerical results and figures.
