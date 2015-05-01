import math
import numpy as np
from collections import namedtuple
from utils import *


ProjParams = namedtuple("ProjParams", ['width', 'height', 'z_near', 'z_far', 'fov'])


class Matrix4x4:

    I = np.eye(4)

    @staticmethod
    def rotation(rot):
        if not rot:
            return Matrix4x4.I

        ax, ay, az = [to_radian(a) for a in rot]

        sin, cos = math.sin, math.cos

        rotate_x = np.array([
            [    1.0,     0.0,      0.0,     0.0],
            [    0.0, sin(ax),  cos(ax),     0.0],
            [    0.0, cos(ax), -sin(ax),     0.0],
            [    0.0,     0.0,      0.0,     1.0]
        ]) if ax else Matrix4x4.I

        rotate_y = np.array([
            [sin(ay),     0.0,  cos(ay),     0.0],
            [    0.0,     1.0,      0.0,     0.0],
            [cos(ay),     0.0, -sin(ay),     0.0],
            [    0.0,     0.0,      0.0,     1.0]
        ]) if ay else Matrix4x4.I

        rotate_z = np.array([
            [sin(az),  cos(az),     0.0,     0.0],
            [cos(az), -sin(az),     0.0,     0.0],
            [    0.0,      0.0,     1.0,     0.0],
            [    0.0,      0.0,     0.0,     1.0]
        ]) if az else Matrix4x4.I

        return rotate_z.dot(rotate_y).dot(rotate_x)

    @staticmethod
    def translation(trans):
        if not trans:
            return Matrix4x4.I

        px, py, pz = trans
        i = np.eye(4)
        i[:, 3] = np.array([px, py, pz, 1.0])
        return i

    @staticmethod
    def scaling(scale):
        if not scale:
            return Matrix4x4.I

        sx, sy, sz = scale
        return np.array([
            [ sz, 0.0, 0.0, 0.0],
            [0.0,  sy, 0.0, 0.0],
            [0.0, 0.0,  sz, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

    @staticmethod
    def perspective_proj(proj):
        if proj is None:
            return Matrix4x4.I

        ar = proj.width / proj.height  # aspect ratio
        z_near, z_far = proj.z_near, proj.z_far
        z_range = z_near - z_far
        thf = math.tan(to_radian(proj.fov / 2.0))  # half FOV tangens
        a, b = -(z_near + z_far)/z_range, 2.0*z_far*z_near/z_range

        p = np.array([
            [1.0/(thf*ar),     0.0,    0.0,    0.0],
            [         0.0, 1.0/thf,    0.0,    0.0],
            [         0.0,     0.0,      a,      b],
            [         0.0,     0.0,    1.0,    0.0]
        ])
        return p

    @staticmethod
    def camera_rotation(target, up):
        n = target / np.linalg.norm(target)
        u = up / np.linalg.norm(up)
        u = np.cross(u, target)
        v = np.cross(n, u)
        return np.array([
            [u[0], u[1], u[2], 0.0],
            [v[0], v[1], v[2], 0.0],
            [n[0], n[1], n[2], 0.0],
            [ 0.0,  0.0,  0.0, 1.0]
        ])


class Pipeline:

    def __init__(self, **params):
        self.scaling = Matrix4x4.scaling(params.get('scaling', None))
        self.translation = Matrix4x4.translation(params.get('translation', None))
        self.rotation = Matrix4x4.rotation(params.get('rotation', None))
        self.projection = Matrix4x4.perspective_proj(params.get('projection', None))
        self._camera = None

    def set_camera(self, camera):
        self._camera = camera

    def get_trans(self):
        P, T, R, S = self.projection, self.translation, self.rotation, self.scaling
        transformation = P.dot(T).dot(R).dot(S)
        return transformation

    def get_wvp(self):
        P, T, R, S = self.projection, self.translation, self.rotation, self.scaling
        cx, cy, cz = self._camera.pos
        camera_trans = Matrix4x4.translation([-cx, -cy, -cz])
        camera_rot = Matrix4x4.camera_rotation(self._camera.target, self._camera.up)
        transformation = P.dot(camera_trans).dot(camera_rot).dot(T).dot(R).dot(S)
        return transformation





