#version 460 core

layout(location=0) in int v_index; // vertex id
out GeometryOutput{
    vec4 v_pos;
    vec4 v_color;
}g_out;

layout(std430, binding=3) buffer Voxels{
    // index, x, y, z, topology.., 0, 0  32 integers
    int Voxel[];
};
layout(std430, binding=4) buffer VoxelAttributes{
    // 4 attributes
    vec4 VoxelAttribute[];
};

uniform mat4 projection;
uniform mat4 view;
uniform float voxel_length;
uniform vec4 voxel_position_offset;
uniform int count;

void main() {
    g_out.v_pos = voxel_position_offset+vec4(float(Voxel[v_index*32+1])*voxel_length, float(Voxel[v_index*32+2])*voxel_length, float(Voxel[v_index*32+3])*voxel_length, 1.0);
    if(VoxelAttribute[v_index].x==1.0){
        g_out.v_color = vec4(1.0, 0.0, 0.0, 0.8);
        for(int j=4; j<30; ++j){
            if(Voxel[v_index*32+j]!=0){
                if(VoxelAttribute[Voxel[v_index*32+j]-1].x == 0.0){
                    // cover
                    g_out.v_color = vec4(0.0, 1.0, 0.0, 0.8);
                    // g_out.v_pos = vec4(0.0, 0.0, 0.0, 1.0);
                }
            }
        }

    }
    else if(VoxelAttribute[v_index].y==1.0){
        g_out.v_color = vec4(1.0, 1.0, 0.0, 0.8);
    }
    else if(VoxelAttribute[v_index].z==1.0){
        g_out.v_color = vec4(0.0, 0.0, 1.0, 0.8);
    }
    else{
        g_out.v_color = vec4(0.1, 0.1, 0.1, 0.0);
        g_out.v_pos = vec4(0.0, 0.0, 0.0, 1.0);
    }
    if(VoxelAttribute[v_index].w==1.0){
        g_out.v_color = vec4(0.0, 1.0, 1.0, 0.8);
    }
    /*if(Voxel[v_index*32+31]==1 && Voxel[v_index*32+30]==1){
        g_out.v_color = vec4(1.0, 0.0, 0.0, 0.8);
        for(int j=4; j<30; ++j){
            if(Voxel[v_index*32+j]!=0){
                if(VoxelAttribute[Voxel[v_index*32+j]-1].x == 0.0){
                    g_out.v_color = vec4(0.1, 0.1, 0.1, 0.0);
                    g_out.v_pos = vec4(0.0, 0.0, 0.0, 1.0);
                }
            }
        }

    }
    else if(Voxel[v_index*32+31]==1 && Voxel[v_index*32+30]==0){
        g_out.v_color = vec4(0.0, 1.0, 0.0, 0.8);
    }
    else if(Voxel[v_index*32+31]==0 && Voxel[v_index*32+30]==1){
        g_out.v_color = vec4(0.0, 0.0, 1.0, 0.8);
    }
    else if(Voxel[v_index*32+31]==0 && Voxel[v_index*32+30]==0){
        g_out.v_color = vec4(0.1, 0.1, 0.1, 0.0);
        g_out.v_pos = vec4(0.0, 0.0, 0.0, 1.0);
    }
    else{
        g_out.v_color = vec4(0.0, 1.0, 1.0, 0.8);
    }
    */
    
    /* if(Voxel[v_index*32+30]>=2){
        g_out.v_color = vec4(0.0, 1.0, 1.0, 1.0);
    }
    else{
        g_out.v_color = vec4(0.0, 1.0, 1.0, 0.0);
        g_out.v_pos = vec4(0.0, 0.0, 0.0, 1.0);
    }*/


}
