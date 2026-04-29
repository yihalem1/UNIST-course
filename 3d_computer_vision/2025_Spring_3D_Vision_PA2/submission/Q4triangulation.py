import numpy as np
import helper as hlp
from Q3essential_matrix import Q3

# Q4

class Q4(Q3):
    def __init__(self):
        super(Q4, self).__init__()

        """
        Write your own code here 

        Step 1. Compute the camera projection matrices P1 using self.K1
            - P1

        Step 2. Use hlp.camera2 to get 4 camera projection matrices P2
            - P2s

        for loop range of 4:
        
            Step 3. Run triangulate using the projection matrices
                - pts3d = self.triangulate(P1, self.pts1, P2, self.pts2)

            Step 4. Figure out the correct P2
                - P2

        Step 5. Compose the extrinsic matrices and 3D points using the correct P2.
            - Ext1, Ext2, pts3d
        """

        # Step 1: first camera projection P1 = K1 [I | 0]
        Ext1 = np.hstack((np.eye(3), np.zeros((3, 1))))
        P1 = self.K1 @ Ext1

        # Step 2: get four P2 candidates
        P2s = hlp.camera2(self.E)

        # placeholders for best
        best_count = -1
        best_Ext2 = None
        best_P2 = None
        best_pts3d = None
        best_idx = -1

        # iterate candidates
        for idx, Ext2_cand in enumerate(P2s):
            P2_cand = self.K2 @ Ext2_cand
            # Step 3: triangulate
            pts3d_cand = self.triangulate(P1, self.pts1, P2_cand, self.pts2)
            # Step 4: cheirality check
            hom = np.hstack((pts3d_cand, np.ones((pts3d_cand.shape[0], 1)))).T
            d1 = (P1 @ hom)[2]
            d2 = (P2_cand @ hom)[2]
            count = np.sum((d1 > 0) & (d2 > 0))
            if count > best_count:
                best_count = count
                best_Ext2 = Ext2_cand
                best_P2 = P2_cand
                best_pts3d = pts3d_cand
                best_idx = idx

        # Step 5: assign outputs
        Ext2 = best_Ext2
        P2 = best_P2
        pts3d = best_pts3d

        # DO NOT CHANGE HERE!
        self.Ext1, self.Ext2 = Ext1, Ext2
        self.P1, self.P2 = P1, P2
        self.pts3d = pts3d

    """
    Q4 Triangulation
        [I] P1, camera projection matrix 1 (3x4 matrix)
            pts1, points in image 1 (Nx2 matrix)
            P2, camera projection matrix 2 (3x4 matrix)
            pts2, points in image 2 (Nx2 matrix)
        [O] pts3d, 3D points in space (Nx3 matrix)
    """
    def triangulate(self, P1, pts1, P2, pts2):
        """
        Write your own code here
        replace pass by your implementation
        """
        N = pts1.shape[0]
        pts3d = np.zeros((N, 3))
        for i in range(N):
            x1, y1 = pts1[i]
            x2, y2 = pts2[i]
            A = np.vstack([
                x1 * P1[2] - P1[0],
                y1 * P1[2] - P1[1],
                x2 * P2[2] - P2[0],
                y2 * P2[2] - P2[1]
            ])
            _, _, Vt = np.linalg.svd(A)
            X = Vt[-1]
            pts3d[i] = (X[:3] / X[3])
        return pts3d




if __name__ == "__main__":

    Q4 = Q4()
    print("Ext2=", Q4.Ext2)







