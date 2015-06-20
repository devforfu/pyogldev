import math
import numpy as np


def to_radian(x):
    return x * math.pi / 180.0


def to_degree(x):
    return x * 180.0 / math.pi


def normalize(v):
    return v / np.linalg.norm(v)


def rotate(v, angle, axe):
    """ Rotates vector v by specified angle around specified axe.

        Uses simple quaternions class for rotation.
    """
    sin_half = math.sin(to_radian(angle / 2))
    cos_half = math.cos(to_radian(angle / 2))
    axe_x, axe_y, axe_z = axe
    rx = axe_x * sin_half
    ry = axe_y * sin_half
    rz = axe_z * sin_half
    rw = cos_half

    rot = Quaternion(rx, ry, rz, rw)
    conj = rot.conjugate()

    w = rot * v * conj

    return np.array([w.x, w.y, w.z])


class Quaternion:
    """ Simple quaternion implementation for vector rotation support """

    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def normalize(self):
        v = np.array([self.x, self.y, self.z, self.w])
        v = v / np.linalg.norm(v)
        self.x, self.y, self.z, self.w = v

    def conjugate(self):
        return Quaternion(-self.x, -self.y, -self.z, self.w)

    def __mul__(self, other):
        l, r = self, other
        if isinstance(other, Quaternion):
            w = l.w*r.w - l.x*r.x - l.y*r.y - l.z*r.z
            x = l.x*r.w + l.w*r.x + l.y*r.z - l.z*r.y
            y = l.y*r.w + l.w*r.y + l.z*r.x - l.x*r.z
            z = l.z*r.w + l.w*r.z + l.x*r.y - l.y*r.x
            return Quaternion(x, y, z, w)

        if isinstance(other, (list, tuple, np.ndarray)):
            vx, vy, vz = other
            w = -l.x*vx - l.y*vy - l.z*vz
            x = l.w*vx + l.y*vz - l.z*vy
            y = l.w*vy + l.z*vx - l.x*vz
            z = l.w*vz + l.x*vy - l.y*vx
            return Quaternion(x, y, z, w)

        raise TypeError("cannot multiply {} by {}"
                        .format(self.__class__.__name__, type(other).__name__))

