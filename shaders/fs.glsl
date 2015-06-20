#version 400

//in vec4 Color;
in vec2 TexCoord0;

out vec4 FragColor;

uniform sampler2D gSampler;

void main() {
//    FragColor = texture(gSampler, TexCoord0.st);
//    FragColor = Color;
    FragColor = vec4(1, 1, 1, 1);
//    FragColor = texture(gSampler, TexCoord0.st);
}