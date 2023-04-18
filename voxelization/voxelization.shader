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


layout(local_size_x=4, local_size_y=4, local_size_z=4) in;

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

uniform vec4 voxel_length;
uniform int triangle_number;
uniform vec4 voxel_position_offset;

//Define a ray struct
struct Ray {
    vec3 origin; //origin point
    vec3 direction; //direction
};

//Define a triangle struct
struct Tri {
    vec3 v0; //first vertex
    vec3 v1; //second vertex
    vec3 v2; //third vertex
    vec3 normal;
    float max_y;
    float min_y;
    float max_z;
    float min_z;
};

//Check if a number is close to zero
bool isZero(float x) {
    return abs(x) < 1e-8;
}

//Check if a number is in the [0,1] range
bool isInRange(float x) {
    return x >= 0.0 && x <= 1.0;
}

//Check if a ray intersects a Tri, and return the intersection point and barycentric coordinates (if any)
ivec2 rayTriangleIntersect(Ray ray, Tri tri) {
    vec3 hitLocation;
    vec3 barycentricCoord;
    //Calculate the triangle's normal vector
    vec3 e0 = tri.v1 - tri.v0;
    vec3 e1 = tri.v2 - tri.v0;
    tri.normal = normalize(cross(e0, e1));

    //Calculate the parameter t for the intersection between the ray and the plane
    float nd = dot(tri.normal, ray.direction);

    //If nd is zero, the ray is parallel or coplanar with the plane, and there are no intersections or infinitely many intersections
    if (isZero(nd)) {
        return ivec2(0, 0);
    }

    float t = dot(tri.v0 - ray.origin, tri.normal) / nd;

    //If t is negative, the intersection point is behind the ray's origin, and is not valid
    if (t < 0.0) {
        return ivec2(0, 0);
    }

    //Calculate the intersection point
    hitLocation = ray.origin + ray.direction * t;

    //Calculate the vectors from the intersection point to each vertex of the triangle
    vec3 v0p = hitLocation - tri.v0;
    vec3 v1p = hitLocation - tri.v1;
    vec3 v2p = hitLocation - tri.v2;

    //Calculate the cross products of each edge of the triangle
    vec3 c0 = cross(e0, e1); //same as the normal vector n
    vec3 c1 = cross(v1p, v2p);
    vec3 c2 = cross(v2p, v0p);
    //Calculate the barycentric coordinates
    barycentricCoord.x = dot(c1,tri.normal)/dot(c0,tri.normal);
    barycentricCoord.y=dot(c2,tri.normal)/dot(c0,tri.normal);
    barycentricCoord.z=1.0-barycentricCoord.x-barycentricCoord.y;

    //Check if the intersection point is inside the triangle
    if(isInRange(barycentricCoord.x)&&isInRange(barycentricCoord.y)&&isInRange(barycentricCoord.z)){
        return ivec2(1, 0); //intersecting
    }
    else{
        return ivec2(0, 0); //not intersecting
    }
}

void Voxelization(int voxel_id){
    Ray ray;
    ray.origin = voxel_position_offset.xyz+vec3(float(Voxel[voxel_id*32+1])*voxel_length.x,float(Voxel[voxel_id*32+2])*voxel_length.x,float(Voxel[voxel_id*32+3])*voxel_length.x);
    ray.direction = vec3(1.0, 0.0, 0.0);
    Ray neg_ray;
    neg_ray.origin = voxel_position_offset.xyz+vec3(float(Voxel[voxel_id*32+1])*voxel_length.x,float(Voxel[voxel_id*32+2])*voxel_length.x,float(Voxel[voxel_id*32+3])*voxel_length.x);
    neg_ray.direction = vec3(-1.0, 0.0, 0.0);
    int PosCount = 0;
    int NegCount = 0;
    for(int i=0; i<triangle_number; ++i){
        Tri tri;
        tri.v0 = Vertex[Triangle[i].x].xyz;
        tri.v1 = Vertex[Triangle[i].y].xyz;
        tri.v2 = Vertex[Triangle[i].z].xyz;
        tri.normal = Normal[Triangle[i].w].xyz;
        tri.max_y = max(max(tri.v0.y, tri.v1.y), tri.v2.y);
        tri.max_z = max(max(tri.v0.z, tri.v1.z), tri.v2.z);
        tri.min_y = min(min(tri.v0.y, tri.v1.y), tri.v2.y);
        tri.min_z = min(min(tri.v0.z, tri.v1.z), tri.v2.z);
        //if(ray.origin.y<=tri.max_y && tri.min_y<=ray.origin.y && ray.origin.z<=tri.max_z && tri.min_z<=ray.origin.z){
        //    ;
        //}
        PosCount += rayTriangleIntersect(ray, tri).x;
        NegCount += rayTriangleIntersect(neg_ray, tri).x;


    }
    if((PosCount*NegCount)%2==1){  // master of piece by Q.Shao: p%2==1&&q%2==1 <==> p*q%2==1
        Voxel[voxel_id*32+31]=1; // inside
        VoxelAttribute[voxel_id].x = 1.0;
        for(int j=4; j<30; ++j){
            if(Voxel[voxel_id*32+j]!=0){
                Voxel[(Voxel[voxel_id*32+j]-1)*32+30]=1; // around
                VoxelAttribute[(Voxel[voxel_id*32+j]-1)].y = 1.0;
            }

            for(int k=4; k<30; ++k){
                if(Voxel[(Voxel[voxel_id*32+j]-1)*32+k]!=0){
                    Voxel[(Voxel[(Voxel[voxel_id*32+j]-1)*32+k]-1)*32+30]=1;// around around
                    VoxelAttribute[(Voxel[(Voxel[voxel_id*32+j]-1)*32+k]-1)].z = 1.0;
                }
            }
        }


    }
    else{
        Voxel[voxel_id*32+31]=0; // outside
        VoxelAttribute[voxel_id].x = 0.0;
    }
    // if(voxel_id%1000==0){
    //     for(int j=4; j<30; ++j){
    //         Voxel[(Voxel[voxel_id*32+j]-1)*32+30]+=2; // around
    //     }
    // }
}

void main(){

    Voxelization(voxel_index-1);
}