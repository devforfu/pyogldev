import ctypes
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from pipeline import Pipeline, ProjParams
from camera import Camera
from texture import Texture


class GlutWindow:

    def __init__(self, screen_size: tuple, screen_pos: tuple=(0, 0),
                 game_mode: bool=False, title: str='Default Title', **params):
        width, height = screen_size
        self.screen_size = screen_size
        self.screen_pos = screen_pos
        self.width = width
        self.height = height
        self.game_mode = game_mode
        self.title = title
        self._vbo = None
        self._vao = None
        self._ibo = None
        self._camera = None
        self._program = None
        self._pipeline = None
        self._log = params.get("log", print)
        self._pipeline_creation = params.get("pipelinecreation", None)
        self._clear_color = params.get("clearcolor", (0, 0, 0, 0))
        self._shaders = params.get("shaders", {})
        # self._vertices = np.array([
        #     -1, -1, -1, 0.0, 0.0,
        #     -1, -1, 1, 1.0, 0.0,
        #     1, -1, 1, 1.0, 1.0,
        #     1, -1, -1, 0.0, 1.0,
        #     0, 1, 0, 0.5, 0.5
        # ], dtype=np.float32)
        # self._indexes = np.array([
        #     0, 1, 2,
        #     2, 3, 0,
        #     0, 1, 4,
        #     1, 2, 4,
        #     2, 3, 4,
        #     3, 0, 4
        # ], dtype=np.uint32)
        self._vertices = np.array([
            -1.0, -1.0, 0.5773, 0.0, 0.0,
            0.0, -1.0, -1.15475, 0.5, 0.0,
            1.0, -1.0, 0.5773, 1.0, 0.0,
            0.0, 1.0, 0.0, 0.5, 1.0
        ], dtype=np.float32)
        self._indexes = np.array([
            0, 3, 1,
            1, 3, 2,
            2, 3, 0,
            0, 1, 2
        ], dtype=np.uint32)
        self._vertex_attributes = {"Position": -1, "TexCoord": -1}
        self._texture = None
        self._setup()

    def _setup(self):
        glutInit(sys.argv[1:])
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_3_2_CORE_PROFILE)
        glutInitWindowSize(self.width, self.height)
        if self.game_mode:
            glutGameModeString("{}x{}@32".format(self.width, self.height))
            glutEnterGameMode()
        else:
            glutCreateWindow(self.title)
            glutInitWindowPosition(*self.screen_pos)
        self.bind_callbacks()
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearColor(*self._clear_color)
        # seems strange because should be GL_BACK... maybe something with camera?
        glCullFace(GL_FRONT)
        glFrontFace(GL_CW)
        glEnable(GL_CULL_FACE)

        self._program = glCreateProgram()
        for file, shader_type in self._shaders.items():
            self.add_shader(file, shader_type)
        glLinkProgram(self._program)
        glUseProgram(self._program)
        self.get_attributes()
        self.create_vertex_buffer()
        self.create_index_buffer()
        texture = Texture(GL_TEXTURE_2D, "resources/test.png")
        if not texture.load():
            raise ValueError("cannot load texture")
        self._texture = texture

    def get_attributes(self):
        """ Extracts attributes defined in vertex shader program """
        for attr_name in self._vertex_attributes.keys():
            position_attr = glGetAttribLocation(self._program, attr_name)
            if position_attr == -1:
                self._log("cannot bind attribute: %s" % attr_name)
            self._vertex_attributes[attr_name] = position_attr

    def bind_callbacks(self):
        glutDisplayFunc(self.on_display)
        glutIdleFunc(self.on_display)
        glutPassiveMotionFunc(self.on_mouse)
        glutSpecialFunc(self.on_keyboard)

    def create_vertex_buffer(self):
        """ Creates vertex array and vertex buffer and fills last one with data """
        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)
        self._vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, self._vertices.nbytes, self._vertices, GL_STATIC_DRAW)

    def create_index_buffer(self):
        self._ibo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self._indexes.nbytes, self._indexes, GL_STATIC_DRAW)

    def add_shader(self, file, shader_type):
        shader = glCreateShader(shader_type)
        with open(file) as sf:
            glShaderSource(shader, sf.read())
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            info = glGetShaderInfoLog(shader)
            self._log("{} shader error occurred".format(os.path.basename(file)))
            self._log(bytes.decode(info))
            sys.exit(1)
        glAttachShader(self._program, shader)
        # glDeleteShader(shader)

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, cam):
        self._camera = cam

    def get_pipeline(self):
        if callable(self._pipeline_creation):
            return self._pipeline_creation()
        projection = ProjParams(self.width, self.height, 1.0, 100.0, 60.0)
        pipeline = Pipeline(rotation=[0, 30, 0], translation=[0, 0, 6], projection=projection)
        return pipeline

    def on_display(self):
        """ Rendering callback """
        self._camera.render()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        scale_location = glGetUniformLocation(self._program, "gScale")
        world_location = glGetUniformLocation(self._program, "gWorld")
        sampler = glGetUniformLocation(self._program, "gSampler")
        if scale_location == 0xffffffff or world_location == 0xffffffff:
            self._log("cannot get uniform parameters")
            sys.exit(1)

        glUniform1f(scale_location, 2.0)
        glUniformMatrix4fv(world_location, 1, GL_TRUE, self._pipeline.get_wvp())
        glUniform1i(sampler, 0)

        # glEnableVertexAttribArray(0)
        a = self._vertex_attributes
        glEnableVertexAttribArray(a["Position"])
        glEnableVertexAttribArray(a["TexCoord"])

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glVertexAttribPointer(a["Position"], 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glVertexAttribPointer(a["TexCoord"], 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ibo)

        self._texture.bind(GL_TEXTURE0)
        glDrawElements(GL_TRIANGLES, 18, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glDisableVertexAttribArray(a["Position"])
        glDisableVertexAttribArray(a["TexCoord"])
        glutSwapBuffers()

    def on_mouse(self, x, y):
        self._camera.mouse(x, y)

    def on_keyboard(self, key, x, y):
        if key == GLUT_KEY_F1:
            sys.exit(0)
        self.camera.keyboard(key)

    def run(self):
        self._pipeline = self.get_pipeline()
        self._pipeline.set_camera(self._camera)
        glutMainLoop()


SCREEN_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720


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