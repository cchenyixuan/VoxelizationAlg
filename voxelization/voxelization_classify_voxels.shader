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


layout(local_size_x=2, local_size_y=2, local_size_z=2) in;

//uint gid = gl_GlobalInvocationID.x;
uint x_length = gl_NumWorkGroups.x * gl_WorkGroupSize.x;
uint y_length = gl_NumWorkGroups.y * gl_WorkGroupSize.y;
uint gid = gl_GlobalInvocationID.x + gl_GlobalInvocationID.y*x_length + gl_GlobalInvocationID.z*x_length*y_length;

/*

in uvec3 gl_NumWorkGroups;
in uvec3 gl_WorkGroupID;
in uvec3 gl_LocalInvocationID;
in uvec3 gl_GlobalInvocationID;
in uint  gl_LocalInvocationIndex;
gl_NumWorkGroups
This variable contains the number of work groups passed to the dispatch function.
gl_WorkGroupID
This is the current work group for this shader invocation. Each of the XYZ components will be on the half-open range [0, gl_NumWorkGroups.XYZ).
gl_LocalInvocationID
This is the current invocation of the shader within the work group. Each of the XYZ components will be on the half-open range [0, gl_WorkGroupSize.XYZ).
gl_GlobalInvocationID
This value uniquely identifies this particular invocation of the compute shader among all invocations of this compute dispatch call. It's a short-hand for the math computation:
gl_WorkGroupID * gl_WorkGroupSize + gl_LocalInvocationID;
gl_LocalInvocationIndex
This is a 1D version of gl_LocalInvocationID. It identifies this invocation's index within the work group. It is short-hand for this math computation:
  gl_LocalInvocationIndex =
          gl_LocalInvocationID.z * gl_WorkGroupSize.x * gl_WorkGroupSize.y +
          gl_LocalInvocationID.y * gl_WorkGroupSize.x +
          gl_LocalInvocationID.x;
Compute shader other variables
const uvec3 gl_WorkGroupSize;   // GLSL ≥ 4.30

*/


int voxel_index = int(gid)+1;
float voxel_index_float = float(voxel_index);

void ClassifyVoxel(int voxel_id){
    // if a voxel is not inside, e.g. around or around-around, mark itself and its neighborhoods 0
    if(VoxelAttribute[voxel_id].x != 1.0){
        VoxelAttribute[voxel_id].w = 0.0;
        for(int j=4; j<30; ++j){
            if(Voxel[voxel_id*32+j]!=0){
                VoxelAttribute[(Voxel[voxel_id*32+j]-1)].w = 0.0;
            }
        }
    }
}

void main() {
    ClassifyVoxel(voxel_index-1);
}
