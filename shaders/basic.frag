#version 330
uniform sampler2D lightmap;
uniform sampler2D tex;
in vec4 v_color;
//in vec2 v_tex;
in vec2 v_lm;
out vec4 color;

void main() {
	//vec2 t = in_tex;
	color = v_color;
	if(v_lm.x < -1 && v_lm.y < -1){
		//vec4 t_color = texture(tex, v_tex);
    	color = texture(lightmap, v_lm) * color;
	}
}
