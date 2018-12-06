#version 330
uniform mat4 view;
uniform mat4 proj;

in vec3 in_vert; 
in vec2 in_tex; 
in vec2 in_lm; 
in vec3 in_normal; 
in vec4 in_color; 

out vec4 v_color;
out vec2 v_tex;
out vec2 v_lm;
float scale = 1.0;//0.03;

void main() {
	v_color = in_color;
	//v_tex = in_tex;
	v_lm = in_lm;
	gl_Position = proj * view * vec4(scale * in_vert.x, (scale * in_vert.z), -scale * in_vert.y, 1.0);
}

