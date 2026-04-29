import numpy as np
import cv2
import random

def computeH(target_points, source_points):
    # Build the linear system Ax = 0 for homography estimation.
    A = []
    for i in range(len(target_points)):
        # Coordinates from the target image (e.g., image 1).
        x_t, y_t = target_points[i][0], target_points[i][1]
        # Coordinates from the source image (e.g., image 2).
        x_s, y_s = source_points[i][0], source_points[i][1]
        # Append the two rows corresponding to the current matching point pair.
        A.append([-x_s, -y_s, -1, 0, 0, 0, x_t * x_s, x_t * y_s, x_t])
        A.append([0, 0, 0, -x_s, -y_s, -1, y_t * x_s, y_t * y_s, y_t])

    A = np.array(A)

    # Compute the Singular Value Decomposition (SVD) of matrix A.
    U, S, V = np.linalg.svd(A)

    # The solution for the homography is the last row of V (flattened).
    homography = V[-1].reshape(3, 3)
    #

    return homography

def warpPerspective(input_image, homography, output_dims):

    out_height, out_width = output_dims

    # (1) Create a grid of homogeneous coordinates for each pixel in the output image.
    # For every pixel (x, y) in the output, we create [x, y, 1].
    pixel_grid = np.array([[x, y, 1] for y in range(out_height) for x in range(out_width)])

    # (2) Apply the homography to each coordinate.
    # The matrix multiplication maps each output coordinate to a coordinate in the input image.
    warped_grid = np.dot(homography, pixel_grid.T).T

    # (3) Normalize the homogeneous coordinates.
    # Divide the x and y coordinates by the third coordinate so that the points become (x, y) in Cartesian coordinates.
    warped_grid[:, 0] /= warped_grid[:, 2]
    warped_grid[:, 1] /= warped_grid[:, 2]

    # (4) Reshape the coordinate array to a (height, width, 2) shape for remapping.
    remap_coords = warped_grid[:, :2].reshape(out_height, out_width, 2)

    # (5) Remap the input image to the output image using the computed coordinates.
    # cv2.remap uses the two maps (one for x and one for y) to assign pixels from the input image.
    warped_image = cv2.remap(input_image, remap_coords[:, :, 0].astype(np.float32),
                             remap_coords[:, :, 1].astype(np.float32),
                             interpolation=cv2.INTER_NEAREST)

    # (6) Create a mask to indicate the filled pixels.
    mask = np.ones((out_height, out_width), dtype=np.uint8) * 255
    if len(input_image.shape) == 3 and input_image.shape[2] == 3:
        mask[warped_image.sum(axis=2) == 0] = 0
    else:
        mask[warped_image == 0] = 0

    return warped_image, mask


def computeH_norm(target_pts, source_pts):

    # 1) Compute centroids of each point set.
    centroid_t = np.mean(target_pts, axis=0)
    centroid_s = np.mean(source_pts, axis=0)
    # 2) Shift points so their centroids lie at the origin.
    shifted_t = target_pts - centroid_t
    shifted_s = source_pts - centroid_s
    # 3) Find the maximum distance from the origin in each shifted set.
    max_dist_t = np.max(np.linalg.norm(shifted_t, axis=1))
    max_dist_s = np.max(np.linalg.norm(shifted_s, axis=1))
    # 4) Scale points so that the farthest point is at √2 from the origin.
    norm_t = (np.sqrt(2) / max_dist_t) * shifted_t
    norm_s = (np.sqrt(2) / max_dist_s) * shifted_s

    # 5) Build the similarity transforms that encapsulate the shift+scale.
    T_t = np.array([
        [np.sqrt(2) / max_dist_t, 0, - (np.sqrt(2) / max_dist_t) * centroid_t[0]],
        [0, np.sqrt(2) / max_dist_t, - (np.sqrt(2) / max_dist_t) * centroid_t[1]],
        [0, 0, 1]
    ])
    T_s = np.array([
        [np.sqrt(2) / max_dist_s, 0, - (np.sqrt(2) / max_dist_s) * centroid_s[0]],
        [0, np.sqrt(2) / max_dist_s, - (np.sqrt(2) / max_dist_s) * centroid_s[1]],
        [0, 0, 1]
    ])

    # 6) Compute the homography on the normalized points.
    H_norm = computeH(norm_t, norm_s)
    # 7) Denormalize: undo the similarity transforms.
    H_denorm = np.linalg.inv(T_t) @ H_norm @ T_s
    # 8) Final scale normalization (make H[2,2] = 1)
    H_denorm /= (H_denorm[2, 2] + 1e-10)

    return H_denorm


import numpy as np

def computeH_ransac(src_pts, dst_pts, max_iters, threshold=2):

    # 1) Flip (x,y) → (row, col) so we can treat them as image coordinates
    src_pix = src_pts[:, [1, 0]]
    dst_pix = dst_pts[:, [1, 0]]

    # 2) Make dst_pix homogeneous: (row, col, 1)
    dst_hom = np.hstack([dst_pix, np.ones((len(dst_pix), 1))])

    best_inlier_count = -np.inf
    best_H = None
    best_inlier_mask = None

    # 3) RANSAC loop
    for _ in range(max_iters):
        # 3a) Randomly sample 4 correspondences
        idx = np.random.choice(len(src_pix), 4, replace=False)
        src_sample = src_pix[idx]
        dst_sample = dst_pix[idx]

        # 3b) Estimate homography on sampled points (normalized method)
        H = computeH_norm(src_sample, dst_sample)

        # 3c) Apply H to all dst_hom points
        warped = (H @ dst_hom.T).T  # shape (N, 3)
        warped[:, 0] /= warped[:, 2]
        warped[:, 1] /= warped[:, 2]

        # 3d) Count inliers: distance between src_pix and warped[:, :2]
        dists = np.linalg.norm(src_pix - warped[:, :2], axis=1)
        mask = (dists <= threshold)
        inlier_count = mask.sum()

        # 3e) Keep the model with the most inliers
        if inlier_count > best_inlier_count:
            best_inlier_count = inlier_count
            best_H = H
            best_inlier_mask = mask.astype(int)

        # 3f) Early exit if perfect fit
        if inlier_count == len(src_pix):
            break

    return best_H, best_inlier_mask



def compositeH(homography, overlay_img, base_img):

    # 1) Invert the homography so we can map overlay → base coordinates
    inv_H = np.linalg.inv(homography)

    # 2) Create a binary mask the same size as the overlay
    overlay_mask = np.ones(overlay_img.shape, dtype=np.uint8)

    # 3) Warp that mask into the base image’s frame
    warped_mask_custom, _ = warpPerspective(overlay_mask, inv_H, base_img.shape[:2])
    warped_mask_cv2 = cv2.warpPerspective(
        overlay_mask, inv_H,
        (base_img.shape[1], base_img.shape[0])
    )

    # 4) Warp the overlay image itself into the base image’s frame
    warped_overlay = cv2.warpPerspective(
        overlay_img, inv_H,
        (base_img.shape[1], base_img.shape[0])
    )

    # 5) Combine: wherever the warped mask is 1, we use the warped overlay;
    #    elsewhere we keep the base image pixel.
    composite = warped_overlay + base_img * (warped_mask_cv2 == 0)

    return composite



