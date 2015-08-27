#version 400
layout (location=0) in vec3 Position;
out vec4 Color;

uniform mat4 gWorld;

void main() {
    gl_Position = gWorld * vec4(Position, 1.0);
    Color = vec4(clamp(Position, 0.1, 1.0), 1.0);
//      gl_Position = vec4(Position, 1.0);
//      Color = vec4(clamp(Position, 0.1, 1.0), 1.0);
}