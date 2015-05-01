#version 400
layout (location=0) in vec3 vp;
out vec4 Color;
uniform float gScale;
uniform mat4 gWorld;

void main() {
    gl_Position = gWorld * vec4(vp.x, vp.y, vp.z, 1.0);
    Color = vec4(clamp(vp, 0.1, 1.0), 1.0);
}