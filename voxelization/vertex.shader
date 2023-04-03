#version 460 core

layout(location=0) in int v_index; // vertex id
out GeometryOutput{
    vec4 v1_pos;
    vec4 v2_pos;
    vec4 v3_pos;
    vec4 v_color;
}g_out;

layout(std430, binding=0) buffer Vertices{
    // x, y, z, 0.0
    vec4 Vertex[];
};
layout(std430, binding=1) buffer Normals{
    // nx, ny, nz, 0.0
    vec4 Normal[];
};
layout(std430, binding=2) buffer Triangles{
    // index of v0, v1, v2, and index of normal
    ivec4 Triangle[];
};

uniform mat4 projection;
uniform mat4 view;


void main() {
    g_out.v1_pos = vec4(Vertex[Triangle[v_index].x].xyz, 1.0);
    g_out.v2_pos = vec4(Vertex[Triangle[v_index].y].xyz, 1.0);
    g_out.v3_pos = vec4(Vertex[Triangle[v_index].z].xyz, 1.0);
    g_out.v_color = vec4(1.0, 1.0, 0.2, 1.0);

}
