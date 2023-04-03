#version 460 core

layout (points) in;
layout (triangle_strip, max_vertices = 3) out;
in GeometryOutput{
    vec4 v1_pos;
    vec4 v2_pos;
    vec4 v3_pos;
    vec4 v_color;
}g_in[];
out vec4 v_color;


uniform mat4 projection;
uniform mat4 view;

void CreateTriangle(){
    // vertex color
    v_color = g_in[0].v_color;
    // 3 vertices emittion to generate a Triangle
    gl_Position = projection*view*g_in[0].v1_pos;
    EmitVertex();
    gl_Position = projection*view*g_in[0].v2_pos;
    EmitVertex();
    gl_Position = projection*view*g_in[0].v3_pos;
    EmitVertex();

    // end of triangle-strip
    EndPrimitive();


}

void main() {
    CreateTriangle();

}
