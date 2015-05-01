#version 400
out vec4 FragColor;
in vec4 Color;

void main() {
    FragColor = Color;
//    FragColor = vec4(1, 1, 1, 1);
}