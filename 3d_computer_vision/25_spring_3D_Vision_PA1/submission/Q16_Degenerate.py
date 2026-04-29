import os
import cv2
import numpy as np
from matchPics import matchPics
from planarH import computeH_ransac

# ─── Configuration ────────────────────────────────────────────────────────────
IMG_PATHS    = ['../data/paralo_1.png', '../data/paralo_2.png']
OUT_DIR      = '../result'
os.makedirs(OUT_DIR, exist_ok=True)

# RANSAC params for custom stitch
RANSAC_ITERS  = 100
INLIER_THRESH = 2.0
# ────────────────────────────────────────────────────────────────────────────────

def custom_homography_stitch(left, right):
    # 1) match with your code
    matches, locs1, locs2 = matchPics(left, right)
    pts1 = locs1[matches[:,0]]
    pts2 = locs2[matches[:,1]]
    # 2) robust H
    H, _ = computeH_ransac(pts1, pts2, RANSAC_ITERS, INLIER_THRESH)
    # 3) warp + blend
    h1, w1 = left.shape[:2]
    h2, w2 = right.shape[:2]
    canvas = (w1 + w2, max(h1, h2))
    warped = cv2.warpPerspective(right, H, canvas)
    warped[0:h1, 0:w1] = left
    # 4) crop black borders
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x,y,w,h = cv2.boundingRect(max(cnts, key=cv2.contourArea))
    return warped[y:y+h, x:x+w]

def Robust_stitch(imgs):
    # — Step A: ORB feature detection + descriptor extraction
    orb = cv2.ORB_create()
    kps_desc = [orb.detectAndCompute(img, None) for img in imgs]
    kps1, desc1 = kps_desc[0]
    kps2, desc2 = kps_desc[1]

    # — Step B: match descriptors with BFMatcher + ratio test
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    knn_matches = bf.knnMatch(desc1, desc2, k=2)
    good_matches = [m for m,n in knn_matches if m.distance < 0.75 * n.distance]

    match_vis = cv2.drawMatches(imgs[0], kps1, imgs[1], kps2, good_matches, None, flags=2)

    stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)
    status, pano = stitcher.stitch(imgs)

    return pano

def main():
    # load images
    imgs = [cv2.imread(p) for p in IMG_PATHS]
    left, right = imgs

    # 1) Degenerate: custom homography
    try:
        pano1 = custom_homography_stitch(left, right)
        cv2.imwrite(os.path.join(OUT_DIR, 'degenerated_custom.png'), pano1)
        print("Custom‑H panorama saved to degenerated_custom.png")
    except Exception as e:
        print("Custom‑H stitch failed:", e)

    try:
        pano2 = Robust_stitch(imgs)
        cv2.imwrite(os.path.join(OUT_DIR, 'degenerated_fixed.png'), pano2)
        print("Stitcher panorama saved to degenerated_fixed.png")
    except Exception as e:
        print("Stitcher stitch failed:", e)

if __name__ == '__main__':
    main()
