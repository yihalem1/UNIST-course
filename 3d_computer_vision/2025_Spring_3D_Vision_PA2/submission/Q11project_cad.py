import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection           as Poly2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection      as Poly3D
from Q10estimate_params import Q10

class Q11(Q10):
    def __init__(self):
        super(Q11, self).__init__()
        self._load_data()
        self._estimate_pose()
        self._project_points()
        self._show_correspondences()
        self._draw_cad_world()
        self._project_cad_to_image()

    # -------- Step-1 : load pnp data -----------------------------------------
    def _load_data(self):
        d         = np.load('../data/pnp.npz', allow_pickle=True)
        self.X    = d['X']
        self.x    = d['x']
        self.img  = d['image']

        cad       = d['cad']
        self.vtx  = np.asarray(cad['vertices'][0, 0], dtype=np.float32)
        self.fcs  = np.asarray(cad['faces'   ][0, 0], dtype=np.int32) - 1

    # -------- Step-2 : pose estimation ---------------------------------------
    def _estimate_pose(self):
        self.P = self.estimate_pose(self.x, self.X)
        self.K, self.R, self.t = self.estimate_params(self.P)

    # -------- Step-3 : project fiducials -------------------------------------
    def _project_points(self):
        X_h = np.hstack([self.X, np.ones((self.X.shape[0], 1))]).T
        xh  = self.P @ X_h
        self.x_proj = (xh[:2] / xh[2]).T

    # -------- Step-4 : visualise 2-D vs projected ----------------------------
    def _show_correspondences(self):
        plt.figure(figsize=(6, 6))
        plt.imshow(self.img)
        plt.scatter(self.x[:, 0], self.x[:, 1],
                    s=160, facecolors='none', edgecolors='blue')
        plt.scatter(self.x_proj[:, 0], self.x_proj[:, 1],
                    c='k', marker='.')
        plt.legend(); plt.axis('off'); plt.tight_layout(); plt.show()

    # -------- Step-5 : CAD model in world coords -----------------------------
    def _draw_cad_world(self):
        verts_rot = (self.R @ self.vtx.T).T          # rotate only

        fig = plt.figure(figsize=(6, 6))
        ax  = fig.add_subplot(111, projection='3d')
        mesh = Poly3D(verts_rot[self.fcs],
                      facecolors='skyblue', edgecolors='navy', linewidths=0.5)
        ax.add_collection3d(mesh)

        ax.auto_scale_xyz(verts_rot[:, 0], verts_rot[:, 1], verts_rot[:, 2])
        ax.set_box_aspect([1, 1, 1])
        ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
        plt.tight_layout(); plt.show()

    # -------- Step-6 : project complete CAD on image -------------------------
    def _project_cad_to_image(self):
        v_h  = np.hstack([self.vtx, np.ones((self.vtx.shape[0], 1))]).T
        proj = self.P @ v_h
        proj = (proj[:2] / proj[2]).T  # V×2

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(self.img)
        ax.add_collection(Poly2D(proj[self.fcs],
                                 facecolors='none',
                                 edgecolors='maroon', linewidths=0.8))
        ax.axis('off'); plt.tight_layout(); plt.show()

if __name__ == "__main__":
    Q11()
