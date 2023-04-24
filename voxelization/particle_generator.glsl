#version 460 compatibility

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
layout(std430, binding=3) buffer Voxels{
    // index, x, y, z, topology.., 0, 0  32 integers
    int Voxel[];
};
layout(std430, binding=4) buffer VoxelAttributes{
    // 4 attributes
    vec4 VoxelAttribute[];
};
layout(std430, binding=5) buffer Particles{
    // index(0), x, y, z
    vec4 Particle[];
};


layout(local_size_x=4, local_size_y=4, local_size_z=4) in;

//uint gid = gl_GlobalInvocationID.x;
uint x_length = gl_NumWorkGroups.x * gl_WorkGroupSize.x;
uint y_length = gl_NumWorkGroups.y * gl_WorkGroupSize.y;
uint gid = gl_GlobalInvocationID.x + gl_GlobalInvocationID.y*x_length + gl_GlobalInvocationID.z*x_length*y_length;

int voxel_index = int(gid)+1;
float voxel_index_float = float(voxel_index);

uniform float voxel_length;  // H
uniform vec4 voxel_position_offset;  // offset
uniform float particle_radius;  // R
uniform int particle_quantity;  // = int(H**3//(R**3*pi*4/3))
uniform vec3 base;

int triple32(int x){
    // hash function
    x ^= x >> 17;
    x *= 0xed5ad4bb;
    x ^= x >> 11;
    x *= 0xac4c1b51;
    x ^= x >> 15;
    x *= 0x31848bab;
    x ^= x >> 14;
    return x;
}
// buffer
vec3 x_available[7];
vec3 y_available[7];
vec3 z_available[7];
vec3 available_position[343];

void CreateParticle(){
    if(particle_quantity < 344){
        x_available[0] = vec3(0, 0, 0);
        x_available[1] = vec3(-1, 0, 0);
        x_available[2] = vec3(1, 0, 0);
        x_available[3] = vec3(-2, 0, 0);
        x_available[4] = vec3(2, 0, 0);
        x_available[5] = vec3(-3, 0, 0);
        x_available[6] = vec3(3, 0, 0);
        y_available[0] = vec3(0, 0, 0);
        y_available[1] = vec3(0, -1, 0);
        y_available[2] = vec3(0, 1, 0);
        y_available[3] = vec3(0, -2, 0);
        y_available[4] = vec3(0, 2, 0);
        y_available[5] = vec3(0, -3, 0);
        y_available[6] = vec3(0, 3, 0);
        z_available[0] = vec3(0, 0, 0);
        z_available[1] = vec3(0, 0, -1);
        z_available[2] = vec3(0, 0, 1);
        z_available[3] = vec3(0, 0, -2);
        z_available[4] = vec3(0, 0, 2);
        z_available[5] = vec3(0, 0, -3);
        z_available[6] = vec3(0, 0, 3);
    }
    else{
        return;
    }

}