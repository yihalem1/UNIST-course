import numpy as np
import cv2
from matchPics import matchPicsORB, matchPics
from planarH import *



# 1. Load the source (cover), target (desk), and overlay (poster) images.
cover_img  = cv2.imread('../data/cv_cover.jpg')
desk_img   = cv2.imread('../data/cv_desk.png')
poster_img = cv2.imread('../data/hp_cover.jpg')

# 2. Detect and match features between cover_img and desk_img.
matches, cover_points, desk_points = matchPics(cover_img, desk_img)

# 3. Extract the matched point coordinates for RANSAC.
src_idx = matches[:, 0]
dst_idx = matches[:, 1]
matched_cover_pts = cover_points[src_idx]
matched_desk_pts  = desk_points[dst_idx]

# 4. Run RANSAC to estimate the best homography mapping cover → desk.
best_H, inlier_mask = computeH_ransac(
    matched_cover_pts,
    matched_desk_pts,
    max_iters=10,
    threshold=2
)

# 5. Resize the poster image to the same size as the cover image.
poster_resized = cv2.resize(
    poster_img,
    dsize=(cover_img.shape[1], cover_img.shape[0]),
    interpolation=cv2.INTER_LINEAR
)

# 6. Warp-and-composite: place the resized poster onto the desk image
result_img = compositeH(best_H, poster_resized, desk_img)

# 7. Save the final composite.
cv2.imwrite('../result/HarryPotterize.jpg', result_img)


