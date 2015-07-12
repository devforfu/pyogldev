#version 400
layout (location=0) in vec3 Position;
layout (location=1) in vec2 TexCoord;

out vec4 Color;
out vec2 TexCoord0;

uniform float gScale;
uniform mat4 gWorld;

void main() {
    gl_Position = gWorld * vec4(Position * gScale, 1.0);
    Color = vec4(clamp(Position, 0.1, 1.0), 1.0);
    TexCoord0 = TexCoord;
}