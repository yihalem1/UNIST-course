import os
import cv2
import numpy as np
from collections import defaultdict

from planarH import computeH_ransac, warpPerspective
from matchPics import matchPicsORB

# ---------------- parameters ----------------
ORB_NFEAT     = 4000
RANSAC_TH     = 3.0
RANSAC_ITERS  = 2000    # for computeH_ransac debug calls
FOCAL_F       = 1.2
DATA_DIR      = "../data"
SAVE_DIR      = "../result"
IMG_LIST      = [f"image{i}.png" for i in (1,2,3,4)]

# --------------- helpers --------------------
def cylindrical(img, f):
    h, w = img.shape[:2]
    cyl  = np.zeros_like(img)
    mask = np.zeros((h, w), np.uint8)
    K = np.array([[f, 0, w/2],
                  [0, f, h/2],
                  [0, 0,   1 ]])
    y_i, x_i = np.indices((h, w))
    homog     = np.stack([x_i, y_i, np.ones_like(x_i)], -1).reshape(-1, 3).T
    pts       = (np.linalg.inv(K) @ homog).T
    A = np.stack([np.sin(pts[:,0]), pts[:,1], np.cos(pts[:,0])], -1)
    A = (K @ A.T).T; A[:, :2] /= A[:, 2:3]
    x, y = A[:,0].reshape(h, w).astype(int), A[:,1].reshape(h, w).astype(int)
    valid = (x >= 0) & (x < w) & (y >= 0) & (y < h)
    cyl[y[valid], x[valid]] = img[y_i[valid], x_i[valid]]
    mask[y[valid], x[valid]] = 255
    return cyl, mask

def orb_desc(gray):
    orb = cv2.ORB_create(ORB_NFEAT)
    kp, des = orb.detectAndCompute(gray, None)
    return np.array([k.pt for k in kp], np.float32), des

def median_shift(kp1, kp2, des1, des2):
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = matcher.knnMatch(des1, des2, 2)
    good = [m for m, n in matches if m.distance < 0.75 * n.distance]
    if len(good) < 4:
        return None, None, 0

    p1 = kp1[[m.queryIdx for m in good]]
    p2 = kp2[[m.trainIdx for m in good]]

    # compute H via OpenCV RANSAC
    H, inl = cv2.findHomography(p2, p1, cv2.RANSAC, RANSAC_TH)
    if H is None:
        return None, None, 0

    # Debug: compare with planarH.computeH_ransac
    try:
        H_dbg, mask_dbg = computeH_ransac(p1, p2, RANSAC_ITERS, RANSAC_TH)
        print(f"[DEBUG] computeH_ransac inliers: {mask_dbg.sum()}")
    except Exception as e:
        print(f"[DEBUG] computeH_ransac failed: {e}")

    shift = np.median((p1 - cv2.perspectiveTransform(p2[None], H)[0]), axis=0)
    return H, (shift[0], shift[1]), int(inl.sum())

# --------------- 1. load & preprocess -------------
imgs, thumbs, masks, kps, descs = [], [], [], [], []
for name in IMG_LIST:
    path = os.path.join(DATA_DIR, name)
    im = cv2.imread(path)
    if im is None:
        raise FileNotFoundError(f"Could not load {path}")
    imgs.append(im)

    cyl, m = cylindrical(im, FOCAL_F * im.shape[1])
    thumbs.append(cyl)
    masks.append(m)

    kp, des = orb_desc(cv2.cvtColor(cyl, cv2.COLOR_BGR2GRAY))
    kps.append(kp)
    descs.append(des)

# --------- 2. build match graph & yaw ordering -------
shifts, support = {}, defaultdict(int)
n = len(imgs)
for i in range(n):
    for j in range(i+1, n):
        # Debug: call matchPicsORB for diagnostics only
        try:
            dbg_matches, dbg_locs1, dbg_locs2 = matchPicsORB(thumbs[i], thumbs[j])
            print(f"[DEBUG] matchPicsORB({i},{j}) returned {len(dbg_matches)} matches")
        except Exception as e:
            print(f"[DEBUG] matchPicsORB failed: {e}")

        _, dxy, inl = median_shift(kps[i], kps[j], descs[i], descs[j])
        if dxy is None:
            continue
        shifts[(i, j)] = dxy
        shifts[(j, i)] = (-dxy[0], -dxy[1])
        support[i] += inl
        support[j] += inl

ref = max(support, key=support.get)
ordered = sorted(range(n),
                 key=lambda idx: shifts[(ref, idx)][0] if idx != ref else 0)

# ------------- 3. progressive stitching -------------
def stitch_subset(indices, out_name):
    # Debug warp: call the high‑level warpPerspective to inspect output shape
    try:
        sample_warp, sample_mask = warpPerspective(
            imgs[indices[0]], np.eye(3), imgs[indices[0]].shape[:2]
        )
        print(f"[DEBUG] warpPerspective sample shape: {sample_warp.shape}")
    except Exception as e:
        print(f"[DEBUG] warpPerspective failed: {e}")

    st = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)
    st.setPanoConfidenceThresh(0.1)

    try:
        st.setFeaturesFinder(cv2.ORB_create(ORB_NFEAT))
    except AttributeError:
        pass
    try:
        warper = cv2.PyRotationWarper("cylindrical", FOCAL_F * imgs[0].shape[1])
        st.setWarper(warper)
    except AttributeError:
        pass

    status, pano = st.stitch([imgs[i] for i in indices])
    if status != cv2.Stitcher_OK:
        raise RuntimeError(f"Stitcher failed on subset {indices} (code {status})")

    os.makedirs(SAVE_DIR, exist_ok=True)
    cv2.imwrite(os.path.join(SAVE_DIR, out_name), pano)
    print(f"Saved {out_name}")

stitch_subset(ordered[:2], "panorama_2.png")
stitch_subset(ordered[:3], "panorama_3.png")
stitch_subset(ordered,     "panorama_4.png")

print("All panoramas saved to", SAVE_DIR)