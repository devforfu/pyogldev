"""
Wraps manipulations with shaders with simple OO interface
"""

from OpenGL.GL import *
from OpenGL.GLU import gluErrorString


class ShaderException(Exception):
    pass


class ShaderObjectError(ShaderException):
    pass


class ShaderProgramError(ShaderException):
    pass


class InvalidUniformLocationError(ShaderException):
    pass


class Technique:

    def __init__(self):
        self.shader_program = None
        self.shader_objects = []

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()

    def init(self):
        """Initializes OpenGL shader program."""
        self.shader_program = glCreateProgram()
        if not self.shader_program:
            raise ShaderProgramError("cannot create shader program")

    def dispose(self):
        """Deletes shaders and shader program created earlier."""
        for obj in self.shader_objects:
            glDeleteShader(obj)
        if self.shader_program is not None:
            glDeleteProgram(self.shader_program)
            self.shader_program = None

    def enable(self):
        glUseProgram(self.shader_program)

    def add_shader(self, shader_type: GLenum, file_name: str):
        """Creates shader object of specified type from specified shader file."""

        with open(file_name, "r") as shader:
            content = shader.read()
        shader_object = glCreateShader(shader_type)
        if not shader_object:
            raise ShaderObjectError("cannot create shader object (path: %s)" % file_name)
        self._add_shader(shader_object, content)

    def add_shader_text(self, shader_type: GLenum, content: str):
        """Creates shader object of specified type from shader text string."""
        shader_object = glCreateShader(shader_type)
        if not shader_object:
            raise ShaderObjectError("cannot create shader from content")
        self._add_shader(shader_object, content)

    def _add_shader(self, shader_object: GLuint, content: str):
        self.shader_objects.append(shader_object)
        glShaderSource(shader_object, content)
        glCompileShader(shader_object)
        if not glGetShaderiv(shader_object, GL_COMPILE_STATUS):
            info = glGetShaderInfoLog(shader_object)
            raise ShaderObjectError("cannot compile shader: %s" % info)
        glAttachShader(self.shader_program, shader_object)

    def finalize(self):
        """Links and validates earlier compiled shader program."""
        glLinkProgram(self.shader_program)
        if not glGetProgramiv(self.shader_program, GL_LINK_STATUS):
            info = glGetProgramInfoLog(self.shader_program)
            raise ShaderProgramError("program linkage error: %s" % info.decode())

        glValidateProgram(self.shader_program)
        if not glGetProgramiv(self.shader_program, GL_VALIDATE_STATUS):
            info = glGetProgramInfoLog(self.shader_program)
            raise ShaderProgramError("program validation error: %s" % info.decode())

        # delete the intermediate shader objects
        for shader_object in self.shader_objects:
            glDeleteShader(shader_object)

        self.shader_objects.clear()

        e = glGetError()
        if e != GL_NO_ERROR:
            raise ShaderProgramError("error occurred: %s" % gluErrorString(e))

    def get_uniform_location(self, uniform_name: str) -> GLuint:
        location = glGetUniformLocation(self.shader_program, uniform_name)
        if location in (None, -1):
            raise InvalidUniformLocationError("cannot get uniform location: %s" % uniform_name)
        return location

    def get_program_param(self, param: GLint) -> GLuint:
        """Returns a parameter from a shader program.

        Arguments:
            param(GLint): OpenGL symbolic name such as GL_LINK_STATUS

        Returns:
            GLuint: requested parameter value
        """
        return glGetProgramiv(self.shader_program, param)