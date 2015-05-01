import numpy as np
from OpenGL.GLUT import *
from utils import *


class Camera:

    step_size = 1
    margin = 100

    def __init__(self, pos, target, up, window_width, window_height):
        self._pos = np.array(pos)
        self._target = normalize(np.array(target))
        self._up = normalize(np.array(up))
        self._window_width = window_width
        self._window_height = window_height
        self._h_angle = 0.0
        self._v_angle = 0.0
        self._on_upper_edge = False
        self._on_lower_edge = False
        self._on_left_edge = False
        self._on_right_edge = False
        self._mouse_pos_x = window_width // 2
        self._mouse_pos_y = window_height // 2
        self.setup()

    def setup(self):
        # horizontal target
        h_target = np.array([self._target[0], 0, self._target[2]])
        h_target = normalize(h_target)
        x, y, z = h_target

        if z >= 0.0:
            if x >= 0.0:
                self._h_angle = 360.0 - to_degree(math.asin(z))
            else:
                self._h_angle = 180.0 + to_degree(math.asin(z))

        else:
            if x >= 0.0:
                self._h_angle = to_degree(math.asin(-z))
            else:
                self._h_angle = 90.0 + to_degree(math.asin(-z))

        self._v_angle = -to_degree(math.asin(y))
        glutWarpPointer(int(self._mouse_pos_x), int(self._mouse_pos_y))

    @property
    def pos(self):
        return self._pos

    @property
    def target(self):
        return self._target

    @property
    def up(self):
        return self._up

    def keyboard(self, key):

        if key == GLUT_KEY_UP:
            self._pos += (self._target * self.step_size)
            return True

        elif key == GLUT_KEY_DOWN:
            self._pos -= (self._target * self.step_size)
            return True

        elif key == GLUT_KEY_LEFT:
            left = np.cross(self._target, self._up)
            left = (left / np.linalg.norm(left)) * self.step_size
            self._pos += left
            return True

        elif key == GLUT_KEY_RIGHT:
            right = np.cross(self._up, self._target)
            right = (right / np.linalg.norm(right)) * self.step_size
            self._pos += right
            return True

        return False

    def mouse(self, x, y):
        delta_x = x - self._mouse_pos_x
        delta_y = y - self._mouse_pos_y
        self._mouse_pos_x = x
        self._mouse_pos_y = y
        self._h_angle += delta_x / 20.0
        self._v_angle += delta_y / 20.0

        if delta_x == 0:
            if x <= self.margin:
                self._on_left_edge = True
            elif x >= (self._window_width - self.margin):
                self._on_right_edge = True

        else:
            self._on_left_edge = False
            self._on_right_edge = False

        if delta_y == 0:
            if y <= self.margin:
                self._on_upper_edge = True
            elif y >= (self._window_height - self.margin):
                self._on_lower_edge = True

        else:
            self._on_upper_edge = False
            self._on_lower_edge = False

        self.update()

    def render(self):
        update = False

        if self._on_left_edge:
            self._h_angle -= 0.1
            update = True

        elif self._on_right_edge:
            self._h_angle += 0.1
            update = True

        if self._on_upper_edge and self._v_angle > -90.0:
            self._v_angle -= 0.1
            update = True

        elif self._on_lower_edge and self._v_angle < 90.0:
            self._v_angle += 0.1
            update = True

        if update:
            self.update()

    def update(self):

        # rotate the view vector by the horizontal angle around the vertical axis
        v_axis = np.array([0.0, 1.0, 0.0])
        view = np.array([1.0, 0.0, 0.0])
        view = rotate(view, self._h_angle, v_axis)
        view = normalize(view)

        # rotate the view vector by the vertical angle around the horizontal axis
        h_axis = np.cross(v_axis, view)
        h_axis = normalize(h_axis)
        view = rotate(view, self._v_angle, h_axis)
        view = normalize(view)

        self._target = view
        self._up = normalize(np.cross(self._target, h_axis))