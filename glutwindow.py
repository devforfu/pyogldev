import ctypes
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from pipeline import Pipeline, ProjParams
from camera import Camera
from texture import Texture
from callback import WindowCallback
from techniques.lighting import LightingTechnique


class GlutWindow(WindowCallback):

    def __init__(self, screen_size: tuple, screen_pos: tuple=(0, 0),
                 game_mode: bool=False, title: str='Default Title', **params):
        width, height = screen_size
        self.screen_size = screen_size
        self.screen_pos = screen_pos
        self.width = width
        self.height = height
        self.z_near = 1.0
        self.z_far = 100.0
        self.fov = 60.0
        self.game_mode = game_mode
        self.title = title

        self._vbo = None
        self._vao = None
        self._ibo = None
        self._program = None
        self._texture = None
        self._vertices = None
        self._indexes = None
        self._camera = None
        self._pipeline = None
        self._scale = 0.0
        self._dir_light_color = 1.0, 1.0, 1.0
        self._dir_light_ambient_intensity = 0.5
        self._projection = ProjParams(
            self.width, self.height, self.z_near, self.z_far, self.fov)

        self._log = params.get("log", print)
        self._clear_color = params.get("clearcolor", (0, 0, 0, 0))
        self._vertex_attributes = {"Position": -1, "TexCoord": -1}

        self._init_glut()
        self._init_gl()
        self._create_vertex_buffer()
        self._create_index_buffer()

        self._effect = LightingTechnique("shaders/vs.glsl", "shaders/fs_lighting.glsl")
        self._effect.init()
        self._effect.enable()
        self._effect.set_texture_unit(0)

        self._texture = Texture(GL_TEXTURE_2D, "resources/test.png")
        if not self._texture.load():
            raise ValueError("cannot load texture")

    def _init_glut(self):
        """
        Basic GLUT initialization and callbacks binding
        """
        glutInit(sys.argv[1:])
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_3_2_CORE_PROFILE)
        glutInitWindowSize(self.width, self.height)
        if self.game_mode:
            glutGameModeString("{}x{}@32".format(self.width, self.height))
            glutEnterGameMode()
        else:
            glutCreateWindow(self.title.encode())
            glutInitWindowPosition(*self.screen_pos)
        # callbacks binding
        glutDisplayFunc(self.on_display)
        glutIdleFunc(self.on_display)
        glutPassiveMotionFunc(self.on_mouse)
        glutSpecialFunc(self.on_keyboard)

    def _init_gl(self):
        """
        OpenGL initialization
        """
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearColor(*self._clear_color)
        # seems strange because should be GL_BACK... maybe something with camera?
        glCullFace(GL_FRONT)
        glFrontFace(GL_CW)
        glEnable(GL_CULL_FACE)

    def _create_vertex_buffer(self):
        """
        Creates vertex array and vertex buffer and fills last one with data.
        """
        self._vertices = np.array([
            -1.0, -1.0, 0.5773, 0.0, 0.0,
            0.0, -1.0, -1.15475, 0.5, 0.0,
            1.0, -1.0, 0.5773, 1.0, 0.0,
            0.0, 1.0, 0.0, 0.5, 1.0
        ], dtype=np.float32)

        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)
        self._vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, self._vertices.nbytes, self._vertices, GL_STATIC_DRAW)

    def _create_index_buffer(self):
        """
        Creates index buffer.
        """
        self._indexes = np.array([
            0, 3, 1,
            1, 3, 2,
            2, 3, 0,
            0, 1, 2
        ], dtype=np.uint32)

        self._ibo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self._indexes.nbytes, self._indexes, GL_STATIC_DRAW)

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, value):
        self._camera = value

    def on_display(self):
        """
        Rendering callback.
        """
        self._camera.render()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self._scale += 0.1
        pipeline = Pipeline(rotation=[0, self._scale, 0],
                            translation=[0, 0, 6],
                            projection=self._projection)
        pipeline.set_camera(self._camera)

        self._effect.set_wvp(pipeline.get_wvp())
        self._effect.set_directional_light(
            self._dir_light_color, self._dir_light_ambient_intensity)

        position, tex_coord = 0, 1
        glEnableVertexAttribArray(position)
        glEnableVertexAttribArray(tex_coord)

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glVertexAttribPointer(tex_coord, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ibo)

        self._texture.bind(GL_TEXTURE0)
        glDrawElements(GL_TRIANGLES, 18, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glDisableVertexAttribArray(position)
        glDisableVertexAttribArray(tex_coord)
        glutSwapBuffers()

    def on_mouse(self, x, y):
        """
        Mouse moving events handler.
        """
        self._camera.mouse(x, y)

    def on_keyboard(self, key, x, y):
        """
        Keyboard events handler.
        """
        if key == GLUT_KEY_F1:
            if not bool(glutLeaveMainLoop):
                sys.exit(0)
            glutLeaveMainLoop()
        if key == GLUT_KEY_PAGE_UP:
            self._dir_light_ambient_intensity += 0.05
        if key == GLUT_KEY_PAGE_DOWN:
            self._dir_light_ambient_intensity -= 0.05
        if self._camera:
            self._camera.keyboard(key)

    def run(self):
        glutMainLoop()


SCREEN_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 1024, 768


if __name__ == "__main__":
    shaders = {
        os.path.join("shaders", "vs.glsl"): GL_VERTEX_SHADER,
        os.path.join("shaders", "fs.glsl"): GL_FRAGMENT_SHADER
    }
    window = GlutWindow(SCREEN_SIZE, game_mode=False, shaders=shaders)
    camera_pos = [0.0, 1.0, 0.0]  # camera position
    camera_target = [0.0, -0.5, 1.0]  # "look at" direction
    camera_up = [0.0, 1.0, 0.0]  # camera vertical axis
    camera = Camera(camera_pos, camera_target, camera_up, WINDOW_WIDTH, WINDOW_HEIGHT)
    window.camera = camera
    window.run()
