from OpenGL.GL import *

from .technique import Technique


class LightingTechnique(Technique):

    def __init__(self, vs_path: str, fs_path: str):
        super(LightingTechnique, self).__init__()
        self._vs_path = vs_path
        self._fs_path = fs_path
        self._wvp_location = None
        self._sampler_location = None
        self._dir_light_color_location = None
        self._dir_light_ambient_intensity_location = None

    def init(self):
        super().init()
        self.add_shader(GL_VERTEX_SHADER, self._vs_path)
        self.add_shader(GL_FRAGMENT_SHADER, self._fs_path)
        self.finalize()
        self._wvp_location = self.get_uniform_location("gWVP")
        self._sampler_location = self.get_uniform_location("gSampler")
        self._dir_light_color_location = \
            self.get_uniform_location("gDirectionalLight.Color")
        self._dir_light_ambient_intensity_location = \
            self.get_uniform_location("gDirectionalLight.AmbientIntensity")

    def set_wvp(self, matrix):
        glUniformMatrix4fv(self._wvp_location, 1, GL_TRUE, matrix)

    def set_texture_unit(self, texture_unit):
        glUniform1i(self._sampler_location, texture_unit)

    def set_directional_light(self, color, ambient_intensity):
        x, y, z = color
        glUniform3f(self._dir_light_color_location, x, y, z)
        glUniform1f(self._dir_light_ambient_intensity_location, ambient_intensity)