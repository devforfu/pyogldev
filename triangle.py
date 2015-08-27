import os
import sys
import ctypes
import numpy as np
# from glfw import *
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from pipeline import Pipeline, ProjParams
from camera import Camera


vertex_code, fragment_code = None, None

camera_pos = [0.0, 1.0, 0.0]  # camera position
camera_target = [0.0, -0.5, 1.0]  # "look at" direction
camera_up = [0.0, 1.0, 0.0]  # camera vertical axis
WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1200
CAMERA = Camera(camera_pos, camera_target, camera_up, WINDOW_WIDTH, WINDOW_HEIGHT)


def tiny_glut(args):
    global vertex_code, fragment_code
    scale = 0.01

    def display():
        CAMERA.render()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        nonlocal scale
        scale_location = gl.glGetUniformLocation(program, "gScale")
        assert scale_location != 0xffffffff
        world_location = gl.glGetUniformLocation(program, "gWorld")
        assert world_location != 0xffffffff

        scale += 0.01

        pipeline = Pipeline(rotation=[0.0, 30*scale, 0.0],
                            # scaling=[math.sin(scale)] * 3,
                            translation=[0, 0, 6],
                            projection=ProjParams(WINDOW_WIDTH, WINDOW_HEIGHT, 1.0, 100.0, 60.0))
        pipeline.set_camera(CAMERA)

        gl.glUniformMatrix4fv(world_location, 1, gl.GL_TRUE, pipeline.get_wvp())
        gl.glDrawElements(gl.GL_TRIANGLES, 18, gl.GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glut.glutSwapBuffers()
        # glut.glutPostRedisplay()

    def mouse(x, y):
        CAMERA.mouse(x, y)

    def keyboard(key, x, y):
        if key == glut.GLUT_KEY_F1:
            sys.exit(0)
        elif key == glut.GLUT_KEY_HOME:
            CAMERA.setup()
        else:
            CAMERA.keyboard(key)

    glut.glutInit(args)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_3_2_CORE_PROFILE)
    glut.glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glut.glutInitWindowPosition(400, 100)
    # glut.glutCreateWindow("Camera Tutorial")
    glut.glutGameModeString("1920x1200@32")
    glut.glutEnterGameMode()

    # callbacks initialization
    glut.glutDisplayFunc(display)
    glut.glutIdleFunc(display)
    # glut.glutKeyboardFunc(keyboard)
    glut.glutPassiveMotionFunc(mouse)
    glut.glutSpecialFunc(keyboard)

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)
    gl.glClearColor(0, 0, 0, 0)

    vertices = np.array([
        -1, -1, 0,
        0, -1, -1,
        1, -1, 0,
        0, -1, 1,
        0, 1, 0
    ], dtype=np.float32)

    indexes = np.array([
        0, 1, 2,
        1, 2, 3,
        0, 1, 4,
        1, 2, 4,
        2, 3, 4,
        3, 0, 4
    ], dtype=np.uint32)

    vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vertex_shader, vertex_code)
    gl.glCompileShader(vertex_shader)

    if not gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS):
        info = gl.glGetShaderInfoLog(vertex_shader)
        print("vertex shader error occurred")
        print(bytes.decode(info))
        return

    fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    gl.glShaderSource(fragment_shader, fragment_code)
    gl.glCompileShader(fragment_shader)

    if not gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS):
        info = gl.glGetShaderInfoLog(fragment_shader)
        print("fragment shader error occurred")
        print(bytes.decode(info))
        return

    program = gl.glCreateProgram()
    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)
    gl.glLinkProgram(program)
    gl.glUseProgram(program)

    vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vao)

    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, ctypes.c_void_p(0))

    ibo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ibo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indexes.nbytes, indexes, gl.GL_STATIC_DRAW)
    glut.glutMainLoop()


if __name__ == "__main__":
    with open(os.path.join("shaders", "vs.glsl")) as f:
        vertex_code = f.read()

    with open(os.path.join("shaders", "fs.glsl")) as f:
        fragment_code = f.read()

    tiny_glut(sys.argv)