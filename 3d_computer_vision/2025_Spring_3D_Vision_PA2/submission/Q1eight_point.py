import numpy as np
import cv2
import helper as hlp


# Q1

class Q1:
    def __init__(self):
        """
        Step1. Load the two temple images and the correspondence points
        Step2. Run eight_point to compute F
        """
        # ----- Step1 -----
        im1 = cv2.imread('../data/im1.png')
        im2 = cv2.imread('../data/im2.png')

        corr = np.load('../data/some_corresp.npz')
        pts1 = corr['pts1']         # (N,2)
        pts2 = corr['pts2']

        # Scale parameter
        M = max(im1.shape[0], im1.shape[1])

        # ----- Step2 -----
        F = self.eight_point(pts1, pts2, M)
        print("Estimated fundamental matrix F:\n", F)

        # DO NOT CHANGE BELOW
        self.im1 = im1
        self.im2 = im2
        self.F = F


    """
    Q1 Eight‑Point Algorithm
        [I]  pts1  Nx2 points in image1
             pts2  Nx2 points in image2
             M     scale (=max(H1,W1))
        [O]  F     3x3 Fundamental matrix
    """
    def eight_point(self, pts1, pts2, M):
        # ---------- 1. Normalize ----------
        T = np.array([[1./M, 0,     0],
                      [0,     1./M, 0],
                      [0,     0,     1]])
        pts1_h = np.hstack([pts1, np.ones((pts1.shape[0], 1))])
        pts2_h = np.hstack([pts2, np.ones((pts2.shape[0], 1))])

        pts1_n = (T @ pts1_h.T).T      # (N,3)
        pts2_n = (T @ pts2_h.T).T

        # ---------- 2. Build A ----------
        x1, y1 = pts1_n[:, 0], pts1_n[:, 1]
        x2, y2 = pts2_n[:, 0], pts2_n[:, 1]
        A = np.column_stack([x2*x1, x2*y1, x2,
                             y2*x1, y2*y1, y2,
                             x1,     y1,   np.ones_like(x1)])

        # ---------- 3. Solve Af = 0 ----------
        _, _, Vt = np.linalg.svd(A)
        F_norm = Vt[-1].reshape(3, 3)

        # ---------- 4. Enforce rank‑2 ----------
        U, S, Vt_f = np.linalg.svd(F_norm)
        S[2] = 0               # smallest σ → 0
        F_norm = U @ np.diag(S) @ Vt_f


        # ---------- 5. Un‑scale ----------
        F = T.T @ F_norm @ T
        return F


if __name__ == "__main__":
    q1 = Q1()
    hlp.displayEpipolarF(q1.im1, q1.im2, q1.F)
