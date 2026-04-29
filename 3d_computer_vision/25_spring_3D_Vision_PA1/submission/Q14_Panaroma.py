import os
import cv2
import numpy as np
from matchPics import matchPics, matchPicsORB
from planarH import computeH_ransac

def load_image(path: str) -> np.ndarray:

    img = cv2.imread(path)
    return img

def stitch_images(
    left_img: np.ndarray,
    right_img: np.ndarray,
    ransac_iters: int = 100,
    inlier_thresh: float = 2.0
) -> np.ndarray:

    # 1) Detect and match features
    matches, locs1, locs2 = matchPics(left_img, right_img)

    # 2) Compute robust homography
    pts1 = locs1[matches[:, 0]]
    pts2 = locs2[matches[:, 1]]
    H, _ = computeH_ransac(
        pts1, pts2,
        ransac_iters,
        inlier_thresh
    )

    # 3) Warp right image into left image coordinate frame
    h1, w1 = left_img.shape[:2]
    h2, w2 = right_img.shape[:2]
    canvas_size = (w1 + w2, max(h1, h2))
    warped = cv2.warpPerspective(right_img, H, canvas_size)

    # 4) Composite left image onto the warped canvas
    warped[0:h1, 0:w1] = left_img

    # 5) Crop out black borders
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
    panorama = warped[y:y+h, x:x+w]

    return panorama


if __name__ == '__main__':
    # Paths and parameters
    left_path = '../result/nature_4.png'
    right_path = '../result/nature_3.png'
    output_path = '../result/Nature_panaroma.png'
    ransac_iters = 100
    inlier_thresh = 2.0

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load, stitch, and save
    left = load_image(left_path)
    right = load_image(right_path)
    panorama = stitch_images(left, right, ransac_iters, inlier_thresh)
    cv2.imwrite(output_path, panorama)
    print(f"Panorama saved to: {output_path}")

