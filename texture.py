import sys
from scipy import misc
from OpenGL.GL import *


class Texture:

    def __init__(self, target, filename: str):
        self.target = target
        self.filename = filename
        self.texture_obj = None
        self.image = None
        self.blob = None

    @property
    def ready(self):
        return self.blob and self.texture_obj

    def load(self):
        try:
            self.blob = misc.imread(self.filename)
        except Exception as e:
            print("Error occurred: " + str(e), file=sys.stderr)
            return False

        self.texture_obj = glGenTextures(1)
        h, w, _ = self.blob.shape
        glBindTexture(self.target, self.texture_obj)
        glTexImage2D(self.target, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.blob.flatten())
        glTexParameterf(self.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(self.target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(self.target, 0)
        return True

    def bind(self, texture_unit):
        glActiveTexture(texture_unit)
        glBindTexture(self.target, self.texture_obj)
