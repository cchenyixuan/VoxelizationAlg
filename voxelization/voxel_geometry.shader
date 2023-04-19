#version 460 core

layout (points) in;
layout (triangle_strip, max_vertices = 14) out;
in GeometryOutput{
    vec4 v_pos;
    vec4 v_color;
}g_in[];
out vec4 v_color;

layout(std430, binding=3) buffer Voxels{
    // index, x, y, z, topology.., 0, 0  32 integers
    int Voxel[];
};

uniform mat4 projection;
uniform mat4 view;
uniform float voxel_length;
uniform vec4 voxel_position_offset;

void CreateCube(){
    // center of voxel
    vec4 center = g_in[0].v_pos;
    // 8 vertices
    vec4 p4 = vec4(center.x-voxel_length/2, center.y-voxel_length/2, center.z-voxel_length/2, 1.0);
    vec4 p3 = vec4(center.x+voxel_length/2, center.y-voxel_length/2, center.z-voxel_length/2, 1.0);
    vec4 p8 = vec4(center.x+voxel_length/2, center.y-voxel_length/2, center.z+voxel_length/2, 1.0);
    vec4 p7 = vec4(center.x-voxel_length/2, center.y-voxel_length/2, center.z+voxel_length/2, 1.0);
    vec4 p6 = vec4(center.x-voxel_length/2, center.y+voxel_length/2, center.z+voxel_length/2, 1.0);
    vec4 p2 = vec4(center.x-voxel_length/2, center.y+voxel_length/2, center.z-voxel_length/2, 1.0);
    vec4 p1 = vec4(center.x+voxel_length/2, center.y+voxel_length/2, center.z-voxel_length/2, 1.0);
    vec4 p5 = vec4(center.x+voxel_length/2, center.y+voxel_length/2, center.z+voxel_length/2, 1.0);

    // vertex color
    v_color = g_in[0].v_color;
    // 12 vertices emittion to generate a full cube in order 4-3-7-8-5-3-1-4-2-7-6-5-2-1
    gl_Position = projection*view*p4;
    EmitVertex();
    gl_Position = projection*view*p3;
    EmitVertex();
    gl_Position = projection*view*p7;
    EmitVertex();
    gl_Position = projection*view*p8;
    EmitVertex();
    gl_Position = projection*view*p5;
    EmitVertex();
    gl_Position = projection*view*p3;
    EmitVertex();
    gl_Position = projection*view*p1;
    EmitVertex();
    gl_Position = projection*view*p4;
    EmitVertex();
    gl_Position = projection*view*p2;
    EmitVertex();
    gl_Position = projection*view*p7;
    EmitVertex();
    gl_Position = projection*view*p6;
    EmitVertex();
    gl_Position = projection*view*p5;
    EmitVertex();
    gl_Position = projection*view*p2;
    EmitVertex();
    gl_Position = projection*view*p1;
    EmitVertex();

    // end of triangle-strip
    EndPrimitive();


}

void main() {
    CreateCube();

}
