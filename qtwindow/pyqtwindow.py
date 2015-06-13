import os
import numpy as np
from PyQt4 import QtGui
from PyQt4.QtOpenGL import QGLWidget
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import Qt, QPoint, QTimer
from OpenGL.GL import *
from OpenGL.GLUT import *

from pipeline import Pipeline, ProjParams
from camera import Camera


class QtGlWindow(QMainWindow):

    def __init__(self):
        super(QtGlWindow, self).__init__()
        # self.data = np.array(.2*np.random.randn(100000, 2), dtype=np.float32)
        self.data = np.array([
            -0.5, 0.0, 0.5,
            0.5, 0.0, 0.5,
            0.5, 0.0, -0.5,
            -0.5, 0.0, -0.5,
            0.0, 0.5, 0.0
        ], dtype=np.float32)
        self.index = np.array([
            1, 2, 5,
            2, 3, 5,
            3, 4, 5,
            4, 1, 5,
            1, 2, 3,
            2, 3, 4
        ], dtype=np.uint32)
        self.widget = GlPlotWidget()
        self.widget.set_data(self.data, self.index)
        self.setGeometry(100, 100, self.widget.width, self.widget.height)
        self.setCentralWidget(self.widget)

        # automatically update window
        timer = QTimer(self)
        timer.timeout.connect(self.widget.updateGL)
        timer.start(1)


class GlPlotWidget(QGLWidget):

    width, height = 600, 600

    def __init__(self):
        super(GlPlotWidget, self).__init__()
        self.vbo = None
        self.ibo = None
        self.pipeline = None
        self.camera = None
        self.data = np.array([])
        self.index = np.array([])
        self.count = 0
        self.step = 0.0
        self.shaders = {
            GL_VERTEX_SHADER: os.path.join('qtwindow', 'vs.glsl'),
            GL_FRAGMENT_SHADER: os.path.join('qtwindow', 'fs.glsl')
        }
        self.program = None
        self.initializeGL()

    def set_data(self, data, index):
        self.data = data
        self.index = index
        self.count = data.shape[0]

    def initializeGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glClearColor(0, 0, 0, 1)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER,
                     self.data.nbytes, self.data, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        self.ibo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     self.index.nbytes, self.index, GL_STATIC_DRAW)

        # load and compile shaders
        self.program = glCreateProgram()
        for t, path in self.shaders.items():
            shader = glCreateShader(t)
            with open(path, 'r') as sh:
                glShaderSource(shader, sh.read())
            glCompileShader(shader)
            if not glGetShaderiv(shader, GL_COMPILE_STATUS):
                info = glGetShaderInfoLog(shader)
                print("{} shader error occurred".format(os.path.basename(path)))
                print(bytes.decode(info))
                sys.exit(1)
            glAttachShader(self.program, shader)
            # glDeleteShader(shader)
        glLinkProgram(self.program)
        glUseProgram(self.program)

        # init camera
        camera_pos = [0.0, 0.0, 0.0]  # camera position
        camera_target = [0.0, 0.0, 1.0]  # "look at" direction
        camera_up = [0.0, 1.0, 0.0]  # camera vertical axis

        def warp_pointer(cx, cy):
            c = self.cursor()
            self.cursor()
            c.setPos(self.mapToGlobal(QPoint(cx, cy)))
            c.setShape(Qt.BlankCursor)
            self.setCursor(c)

        self.camera = Camera(camera_pos, camera_target, camera_up,
                             self.width, self.height, warp_pointer)
        #self.pipeline.set_camera(self.camera)

    def paintGL(self):
        self.step += 0.1
        self.camera.render()
        projection = ProjParams(self.width, self.height, 1.0, 100.0, 60.0)
        self.pipeline = Pipeline(rotation=[0, 30*self.step, 0],
                                 translation=[0, 0, 3],
                                 projection=projection)
        self.pipeline.set_camera(self.camera)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnableVertexAttribArray(0)
        world_location = glGetUniformLocation(self.program, "gWorld")
        glUniformMatrix4fv(world_location, 1, GL_TRUE, self.pipeline.get_wvp())
        glDrawElements(GL_TRIANGLES, self.index.shape[0],
                       GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glDisableVertexAttribArray(0)

    def resizeGL(self, width, height):
        self.width, self.height = width, height
        glViewport(0, 0, self.width, self.height)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    window = QtGlWindow()
    window.show()
    app.exec_()
