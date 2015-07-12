import unittest

from OpenGL.GL import *
from OpenGL.GLUT import *

from techniques.technique import Technique, ShaderObjectError, InvalidUniformLocationError


class TechniqueTest(unittest.TestCase):

    vertex_shader_code = """
#version 400
layout (location=0) in vec3 Position;

out vec4 Color;
uniform float scaleX;
uniform float scaleY;

void main() {
    gl_Position = vec4(Position.x * scaleX, Position.y * scaleY, Position.z, 1.0);
    Color = vec4(clamp(Position, 0.1, 1.0), 1.0);
}
"""

    fragment_shader_code = """
#version 400

in vec4 Color;
out vec4 FragColor;

void main() {
    FragColor = Color;
}
"""

    def setUp(self):
        glutInit(sys.argv[1:])
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_3_2_CORE_PROFILE)
        glutInitWindowSize(100, 100)
        glutCreateWindow("Test Case")
        glutInitWindowPosition(100, 100)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

    def tearDown(self):
        pass

    def init_technique(self, t):
        t.add_shader_text(GL_VERTEX_SHADER, self.vertex_shader_code)
        t.add_shader_text(GL_FRAGMENT_SHADER, self.fragment_shader_code)
        t.finalize()
        t.enable()

    def test_technique_creation_and_enabling(self):
        with Technique() as t:
            self.init_technique(t)

    def test_technique_creation_failure(self):
        with Technique() as t:
            bad_shader = self.vertex_shader_code.replace("gl_Position", "position")
            self.assertRaises(
                ShaderObjectError,
                lambda: t.add_shader_text(GL_VERTEX_SHADER, bad_shader))

    def test_getting_uniform_location(self):
        with Technique() as t:
            self.init_technique(t)
            loc1 = t.get_uniform_location("scaleX")
            loc2 = t.get_uniform_location("scaleY")
            self.assertNotIn(loc1, (None, -1))
            self.assertNotEqual(loc2, (None, -1))
            self.assertRaises(
                InvalidUniformLocationError,
                lambda: t.get_uniform_location("not_exist"))

    def test_getting_program_param(self):
        with Technique() as t:
            self.init_technique(t)
            self.assertEqual(t.get_program_param(GL_LINK_STATUS), GL_TRUE)
            self.assertEqual(t.get_program_param(GL_VALIDATE_STATUS), GL_TRUE)


if __name__ == '__main__':
    unittest.main()