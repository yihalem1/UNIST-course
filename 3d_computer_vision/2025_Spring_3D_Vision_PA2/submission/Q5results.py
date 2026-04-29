import numpy as np
import helper as hlp
import matplotlib.pyplot as plt
from Q4triangulation import Q4
import os

# Q5

class Q5(Q4):
    def __init__(self):
        super(Q5, self).__init__()

        """
        Write your own code here 

        Step 1. Complete 'def vis_pts3d' to plot the 3D points computed in Q4.

        Step 2. Load the points from data/some_corresp.npz to compute reprojection error.
                - pts1, pts2

        Step 3. Calculate the reprojection error. You should use the triangulate function in Q4.
                - pts3d_corresp
                - reprojection_error = self.compute_reprojerr(self.P1, pts1, self.P2, pts2, pts3d_corresp)

        Step 4. Save the computed extrinsic parameters (R1,R2,t1,t2) to data/extrinsics.npz. 
                - You should use what you computed in Q4.

        """
        # --- Step 1: Load the corresponding 2D points from data/some_corresp.npz ---
        data_corr = np.load('../data/some_corresp.npz')
        pts1 = data_corr['pts1']  # N×2 array of points in image 1
        pts2 = data_corr['pts2']  # N×2 array of points in image 2

        # --- Step 2: Triangulate to get the 3D points for these correspondences ---
        pts3d_corr = self.triangulate(self.P1, pts1, self.P2, pts2)

        # --- Step 3: Compute and report reprojection error ---
        reproj_err = self.compute_reprojerr(self.P1, pts1, self.P2, pts2, pts3d_corr)
        print(f"Reprojection Error: {reproj_err:.4f} pixels")

        # --- Step 4: Save the computed extrinsic parameters for camera 1 and 2 ---
        #    Ext1 and Ext2 are the [R|t] matrices computed in Q4
        np.savez('../data/extrinsics.npz',
                 R1=self.Ext1[:, :3], t1=self.Ext1[:, 3],
                 R2=self.Ext2[:, :3], t2=self.Ext2[:, 3])

    """
    Q5 Compute Reprojection Error
        [I] P1, camera projection matrix 1 (3x4 matrix)
            pts1, points in image 1 (Nx2 matrix)
            P2, camera projection matrix 2 (3x4 matrix)
            pts2, points in image 2 (Nx2 matrix)
            pts3d, 3D points in space (Nx3 matrix)
        [O] reproj_err, Reprojection Error (float)
    """

    def compute_reprojerr(self, P1, pts1, P2, pts2, pts3d):
        """
        Write your own code here
        replace pass by your implementation
        """
        # make homogeneous 3D
        X_h = np.hstack([pts3d, np.ones((pts3d.shape[0], 1))])  # (N,4)

        # project into image 1
        proj1 = (P1 @ X_h.T)  # (3,N)
        proj1 = proj1[:2] / proj1[2]  # normalize by z
        proj1 = proj1.T  # (N,2)

        # project into image 2
        proj2 = (P2 @ X_h.T)
        proj2 = proj2[:2] / proj2[2]
        proj2 = proj2.T

        # compute mean L2 distances
        err1 = np.linalg.norm(proj1 - pts1, axis=1).mean()
        err2 = np.linalg.norm(proj2 - pts2, axis=1).mean()

        return err1 + err2

    def vis_pts3d(self, pts3d, save=True, outdir="../results"):
        """
        Show (or save) the reconstructed 3‑D points.
        If save=True, three canonical views are saved to disk.
        """
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.scatter(pts3d[:, 0], pts3d[:, 1], pts3d[:, 2],
                   s=8, c='red')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('3D Reconstruction')

        if save:
            views = [(90, 90), (90, -90), (80, 15)]
            os.makedirs(outdir, exist_ok=True)
            for i, (elev, azim) in enumerate(views):
                ax.view_init(elev, azim)
                fig.savefig(f"{outdir}/recon_view_{i+1}.png",
                            dpi=300, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()


if __name__ == "__main__":
    Q5 = Q5()
    Q5.vis_pts3d(Q5.pts3d)