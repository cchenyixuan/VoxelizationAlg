import math

import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import time
import re
import pyrr
from voxel_refine import Refine


class Loader:
    def __init__(self, file_path):
        self.file = file_path
        self.vertex_buffer, self.normal_buffer, self.triangle_buffer = self.load_obj(self.file)

    def __call__(self, file_path=None):
        if file_path is None:
            return self.vertex_buffer, self.normal_buffer, self.triangle_buffer
        else:
            self.file = file_path
            self.vertex_buffer, self.normal_buffer, self.triangle_buffer = self.load_obj(self.file)
            return self.vertex_buffer, self.normal_buffer, self.triangle_buffer

    @staticmethod
    def load_obj(file):
        find_vertex = re.compile(r"v (\+?-?[\d.]+) (\+?-?[\d.]+) (\+?-?[\d.]+)\n", re.S)
        find_normal = re.compile(r"vn (\+?-?[\d.]+) (\+?-?[\d.]+) (\+?-?[\d.]+)\n", re.S)
        find_triangle = re.compile(r"f (\d+)/\d+/(\d+) (\d+)/\d+/(\d+) (\d+)/\d+/(\d+)\n", re.S)
        vertex_buffer = []
        normals = []
        normal_buffer = []
        triangle_buffer = []
        with open(file, "r") as f:
            for row in f:
                if row[:2] == "v ":
                    vertex_buffer.append(
                        np.array([*[float(_) for _ in re.findall(find_vertex, row)[0]], 0.0], dtype=np.float32))
                elif row[:2] == "vn":
                    normals.append(
                        np.array([*[float(_) for _ in re.findall(find_normal, row)[0]], 0.0], dtype=np.float32))
                elif row[:2] == "f ":
                    tmp = [int(_) - 1 for _ in re.findall(find_triangle, row)[0] if _ != ""]
                    normal_buffer.append((normals[tmp[1]] + normals[tmp[3]] + normals[tmp[5]]) / 3)
                    triangle_buffer.append(np.array([tmp[0], tmp[2], tmp[4], len(normal_buffer) - 1], dtype=np.int32))
            f.close()
        return np.array(vertex_buffer, dtype=np.float32), np.array(normal_buffer, dtype=np.float32), np.array(
            triangle_buffer, dtype=np.int32)


class Voxelization:
    def __init__(self, file_path, voxel_length):
        self.file = file_path
        self.vertex_buffer, self.normal_buffer, self.triangle_buffer = Loader(file_path)()
        print(f"Vertices: {self.vertex_buffer.shape[0]}")
        print(f"Normals: {self.normal_buffer.shape[0]}")
        print(f"Triangles: {self.triangle_buffer.shape[0]}")
        self.lower_bound = np.min(self.vertex_buffer, axis=0)
        self.upper_bound = np.max(self.vertex_buffer, axis=0)
        self.voxel_position_offset = self.lower_bound
        self.voxel_length = voxel_length
        s = time.time()
        self.voxel_buffer = self.space_division()
        print("shao", time.time() - s)
        s = time.time()
        self.voxel_buffer_chen = self.space_division_chen()
        print("chen 1", time.time() - s)
        s = time.time()
        self.voxel_buffer_chen_2 = self.create_voxels()
        print("chen 2", time.time() - s)
        print(f"Voxels: {self.voxel_buffer.shape[0] // 8}")

    """"""

    def space_division(self):
        lower_bound = self.lower_bound
        upper_bound = self.upper_bound

        x = int(np.ceil((upper_bound[0] - lower_bound[0]) / self.voxel_length) + 1)
        y = int(np.ceil((upper_bound[1] - lower_bound[1]) / self.voxel_length) + 1)
        z = int(np.ceil((upper_bound[2] - lower_bound[2]) / self.voxel_length) + 1)
        n = x * y * z
        xy = x * y

        domain_mat = np.zeros((n, 2 * 4, 4), dtype=np.int32)
        for i in range(n):
            index = i + 1
            # float version
            # domain_mat[i, 0, :] = [index, (i % (x * y) // y) * self.h, (i % (x * y) % y) * self.h,
            #                        i // (x * y) * self.h]
            # int version
            x_id = i % x
            y_id = i // x % y
            z_id = i // xy % z
            domain_mat[i][0, :] = np.array([i + 1, x_id, y_id, z_id], dtype=np.int32)
            back = 0 if z_id <= 0 else i - xy + 1  # i + i = index
            front = 0 if z_id >= z - 1 else i + xy + 1  # i + i = index
            pt = i % xy  # id in a layer

            # left, right, down, up, LeftDown, LeftUp, RightDown, RightUp
            if x_id == 0 and y_id == 0:  # pt == 0:  # left_down_corner
                buf = np.array([0, index + 1, 0, index + x, 0, 0, 0, index + x + 1], dtype=np.int32)
            elif x_id == x - 1 and y_id == 0:  # pt == x - 1:  # right_down_corner
                buf = np.array([index - 1, 0, 0, index + x, 0, index + x - 1, 0, 0], dtype=np.int32)
            elif x_id == 0 and y_id == y - 1:  # pt == x * y - x:  # left_up_corner
                buf = np.array([0, index + 1, index - x, 0, 0, 0, index - x + 1, 0], dtype=np.int32)
            elif x_id == x - 1 and y_id == y - 1:  # pt == x * y - 1:  # right_up_corner
                buf = np.array([index - 1, 0, index - x, 0, index - x - 1, 0, 0, 0], dtype=np.int32)

            elif y_id == 0:  # pt // x == 0:  # down row
                buf = np.array([index - 1, index + 1, 0, index + x, 0, index + x - 1, 0, index + x + 1],
                               dtype=np.int32)
            elif y_id == y - 1:  # pt // x == y - 1:  # up row
                buf = np.array([index - 1, index + 1, index - x, 0, index - x - 1, 0, index - x + 1, 0],
                               dtype=np.int32)
            elif pt % x == 0:  # left col
                buf = np.array([0, index + 1, index - x, index + x, 0, 0, index - x + 1, index + x + 1],
                               dtype=np.int32)
            elif pt % x == x - 1:  # right col
                buf = np.array([index - 1, 0, index - x, index + x, index - x - 1, index + x - 1, 0, 0],
                               dtype=np.int32)
            else:  # center
                buf = np.array([index - 1, index + 1, index - x, index + x,
                                index - x - 1, index + x - 1, index - x + 1, index + x + 1], dtype=np.int32)

            contents = np.zeros((2, 8), dtype=np.int32)
            if back != 0:
                contents[0, :] = [0 if pos == 0 else pos - x * y for pos in buf]
            if front != 0:
                contents[1, :] = [0 if pos == 0 else pos + x * y for pos in buf]

            left_back, right_back, down_back, up_back, left_down_back, left_up_back, right_down_back, right_up_back = contents[
                                                                                                                      0,
                                                                                                                      :]
            left_front, right_front, down_front, up_front, left_down_front, left_up_front, right_down_front, right_up_front = contents[
                                                                                                                              1,
                                                                                                                              :]

            # contents = contents.T
            # contents = contents.reshape(16)
            # contents = np.hstack((buf[:4], back, front, buf[4:], contents, 0, 0))
            # contents = contents.reshape((7, 4))
            # domain_mat[i, 1:8, :] = contents
            tmp = np.array([[*buf[:4]],
                            [back, front, *buf[4:6]],
                            [*buf[6:], left_back, left_front],
                            [right_back, right_front, down_back, down_front],
                            [up_back, up_front, left_down_back, left_down_front],
                            [left_up_back, left_up_front, right_down_back, right_down_front],
                            [right_up_back, right_up_front, 0, 0]], dtype=np.int32)
            domain_mat[i][1:] = tmp

            # re-arrange
            """
            we set x, y, z have 3 status: -1, 0, 1
            Left = (-1, 0, 0)
            Right = (1, 0, 0)
            Down = (0, -1, 0)
            Up = (0, 1, 0)
            Back = (0, 0, -1)
            Front = (0, 0, 1)
            and other combinations of above, i.e.
            LeftUpBack = (-1, 1, -1) = Left + Up + Back

            re_arrange = [
                ["i", "x", "y", "z"],0-3
                [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0)],4-7
                [(0, 0, -1), (0, 0, 1), (-1, -1, 0), (-1, 1, 0)],8-11
                [(1, -1, 0), (1, 1, 0), (-1, 0, -1), (-1, 0, 1)],12-15
                [(1, 0, -1), (1, 0, 1), (0, -1, -1), (0, -1, 1)],16-19
                [(0, 1, -1), (0, 1, 1), (-1, -1, -1), (-1, -1, 1)],20-23
                [(-1, 1, -1), (-1, 1, 1), (1, -1, -1)", (1, -1, 1)],24-27
                [(1, 1, -1), (1, 1, 1), "0", "0"],28-31
            ]

            """
            re_arrange = [
                ["i", "x", "y", "z"],
                ["Left", "Right", "Down", "Up"],
                ["Back", "Front", "LeftDown", "LeftUp"],
                ["RightDown", "RightUp", "LeftBack", "LeftFront"],
                ["RightBack", "RightFront", "DownBack", "DownFront"],
                ["UpBack", "UpFront", "LeftDownBack", "LeftDownFront"],
                ["LeftUpBack", "LeftUpFront", "RightDownBack", "RightDownFront"],
                ["RightUpBack", "RightUpFront", "0", "0"],
            ]

        output_buffer = np.vstack([voxel_matrices for voxel_matrices in domain_mat])

        return output_buffer

    def space_division_chen(self):
        lower_bound = self.lower_bound
        upper_bound = self.upper_bound

        x = int(np.ceil((upper_bound[0] - lower_bound[0]) / self.voxel_length) + 1)
        y = int(np.ceil((upper_bound[1] - lower_bound[1]) / self.voxel_length) + 1)
        z = int(np.ceil((upper_bound[2] - lower_bound[2]) / self.voxel_length) + 1)
        n = x * y * z
        xy = x * y

        domain_mat = np.zeros((n, 2 * 4, 4), dtype=np.int32)
        for i in range(n):
            x_id = i % x
            y_id = i // x % y
            z_id = i // xy % z
            domain_mat[i][0, :] = np.array([i + 1, x_id, y_id, z_id], dtype=np.int32)
            left = 0 if x_id <= 0 else i - 1 + 1  # i + i = index
            right = 0 if x_id >= x - 1 else i + 1 + 1  # i + i = index
            down = 0 if y_id <= 0 else i - x + 1  # i + i = index
            up = 0 if y_id >= y - 1 else i + x + 1  # i + i = index
            back = 0 if z_id <= 0 else i - xy + 1  # i + i = index
            front = 0 if z_id >= z - 1 else i + xy + 1  # i + i = index
            left_down = 0 if left == 0 or down == 0 else i - 1 - x + 1  # i + i = index
            left_up = 0 if left == 0 or up == 0 else i - 1 + x + 1  # i + i = index
            right_down = 0 if right == 0 or down == 0 else i + 1 - x + 1  # i + i = index
            right_up = 0 if right == 0 or up == 0 else i + 1 + x + 1  # i + i = index
            left_back = 0 if left == 0 or back == 0 else i - 1 - xy + 1  # i + i = index
            left_front = 0 if left == 0 or front == 0 else i - 1 + xy + 1  # i + i = index
            right_back = 0 if right == 0 or back == 0 else i + 1 - xy + 1  # i + i = index
            right_front = 0 if right == 0 or front == 0 else i + 1 + xy + 1  # i + i = index
            down_back = 0 if down == 0 or back == 0 else i - x - xy + 1  # i + i = index
            down_front = 0 if down == 0 or front == 0 else i - x + xy + 1  # i + i = index
            up_back = 0 if up == 0 or back == 0 else i + x - xy + 1  # i + i = index
            up_front = 0 if up == 0 or front == 0 else i + x + xy + 1  # i + i = index
            left_down_back = 0 if left == 0 or down == 0 or back == 0 else i - 1 - x - xy + 1  # i + i = index
            left_down_front = 0 if left == 0 or down == 0 or front == 0 else i - 1 - x + xy + 1  # i + i = index
            left_up_back = 0 if left == 0 or up == 0 or back == 0 else i - 1 + x - xy + 1  # i + i = index
            left_up_front = 0 if left == 0 or up == 0 or front == 0 else i - 1 + x + xy + 1  # i + i = index
            right_down_back = 0 if right == 0 or down == 0 or back == 0 else i + 1 - x - xy + 1  # i + i = index
            right_down_front = 0 if right == 0 or down == 0 or front == 0 else i + 1 - x + xy + 1  # i + i = index
            right_up_back = 0 if right == 0 or up == 0 or back == 0 else i + 1 + x - xy + 1  # i + i = index
            right_up_front = 0 if right == 0 or up == 0 or front == 0 else i + 1 + x + xy + 1  # i + i = index

            domain_mat[i][1, :] = np.array([left, right, down, up], dtype=np.int32)
            domain_mat[i][2, :] = np.array([back, front, left_down, left_up], dtype=np.int32)
            domain_mat[i][3, :] = np.array([right_down, right_up, left_back, left_front], dtype=np.int32)
            domain_mat[i][4, :] = np.array([right_back, right_front, down_back, down_front], dtype=np.int32)
            domain_mat[i][5, :] = np.array([up_back, up_front, left_down_back, left_down_front], dtype=np.int32)
            domain_mat[i][6, :] = np.array([left_up_back, left_up_front, right_down_back, right_down_front],
                                           dtype=np.int32)
            domain_mat[i][7, :] = np.array([right_up_back, right_up_front, 0, 0], dtype=np.int32)

        return np.vstack([voxel_matrices for voxel_matrices in domain_mat])

    def create_voxels(self):
        lower_bound = self.lower_bound
        upper_bound = self.upper_bound

        x = int(np.ceil((upper_bound[0] - lower_bound[0]) / self.voxel_length) + 1)
        y = int(np.ceil((upper_bound[1] - lower_bound[1]) / self.voxel_length) + 1)
        z = int(np.ceil((upper_bound[2] - lower_bound[2]) / self.voxel_length) + 1)
        n = x * y * z
        yz = y * z

        voxels = np.zeros([n, 2 * 4, 4], dtype=np.int32)

        for x_id in range(x):
            for y_id in range(y):
                for z_id in range(z):
                    voxel_id = x_id * yz + y_id * z + z_id
                    voxels[voxel_id][0, :] = np.array([voxel_id + 1, x_id, y_id, z_id], dtype=np.int32)
                    left = (x_id - 1) * yz + y_id * z + z_id + 1
                    right = (x_id + 1) * yz + y_id * z + z_id + 1
                    down = x_id * yz + (y_id - 1) * z + z_id + 1
                    up = x_id * yz + (y_id + 1) * z + z_id + 1
                    back = x_id * yz + y_id * z + (z_id - 1) + 1
                    front = x_id * yz + y_id * z + (z_id + 1) + 1
                    left_down = (x_id - 1) * yz + (y_id - 1) * z + z_id + 1
                    left_up = (x_id - 1) * yz + (y_id + 1) * z + z_id + 1
                    right_down = (x_id + 1) * yz + (y_id - 1) * z + z_id + 1
                    right_up = (x_id + 1) * yz + (y_id + 1) * z + z_id + 1
                    left_back = (x_id - 1) * yz + y_id * z + (z_id - 1) + 1
                    left_front = (x_id - 1) * yz + y_id * z + (z_id + 1) + 1
                    right_back = (x_id + 1) * yz + y_id * z + (z_id - 1) + 1
                    right_front = (x_id + 1) * yz + y_id * z + (z_id + 1) + 1
                    down_back = x_id * yz + (y_id - 1) * z + (z_id - 1) + 1
                    down_front = x_id * yz + (y_id - 1) * z + (z_id + 1) + 1
                    up_back = x_id * yz + (y_id + 1) * z + (z_id - 1) + 1
                    up_front = x_id * yz + (y_id + 1) * z + (z_id + 1) + 1
                    left_down_back = (x_id - 1) * yz + (y_id - 1) * z + (z_id - 1) + 1
                    left_down_front = (x_id - 1) * yz + (y_id - 1) * z + (z_id + 1) + 1
                    left_up_back = (x_id - 1) * yz + (y_id + 1) * z + (z_id - 1) + 1
                    left_up_front = (x_id - 1) * yz + (y_id + 1) * z + (z_id + 1) + 1
                    right_down_back = (x_id + 1) * yz + (y_id - 1) * z + (z_id - 1) + 1
                    right_down_front = (x_id + 1) * yz + (y_id - 1) * z + (z_id + 1) + 1
                    right_up_back = (x_id + 1) * yz + (y_id + 1) * z + (z_id - 1) + 1
                    right_up_front = (x_id + 1) * yz + (y_id + 1) * z + (z_id + 1) + 1
                    if x_id == 0:
                        left, left_down, left_up, left_back, left_front, left_down_back, left_down_front, left_up_back, left_up_front = 0, 0, 0, 0, 0, 0, 0, 0, 0
                    if x_id == x - 1:
                        right, right_down, right_up, right_back, right_front, right_down_back, right_down_front, right_up_back, right_up_front = 0, 0, 0, 0, 0, 0, 0, 0, 0
                    if y_id == 0:
                        down, down_back, down_front, left_down, right_down, left_down_back, left_down_front, right_down_back, right_down_front = 0, 0, 0, 0, 0, 0, 0, 0, 0
                    if y_id == y - 1:
                        up, up_back, up_front, left_up, right_up, left_up_back, left_up_front, right_up_back, right_up_front = 0, 0, 0, 0, 0, 0, 0, 0, 0
                    if z_id == 0:
                        back, left_back, right_back, down_back, up_back, left_down_back, left_up_back, right_down_back, right_up_back = 0, 0, 0, 0, 0, 0, 0, 0, 0
                    if z_id == z - 1:
                        front, left_front, right_front, down_front, up_front, left_down_front, left_up_front, right_down_front, right_up_front = 0, 0, 0, 0, 0, 0, 0, 0, 0

                    voxels[voxel_id][1, :] = np.array([left, right, down, up], dtype=np.int32)
                    voxels[voxel_id][2, :] = np.array([back, front, left_down, left_up], dtype=np.int32)
                    voxels[voxel_id][3, :] = np.array([right_down, right_up, left_back, left_front], dtype=np.int32)
                    voxels[voxel_id][4, :] = np.array([right_back, right_front, down_back, down_front], dtype=np.int32)
                    voxels[voxel_id][5, :] = np.array([up_back, up_front, left_down_back, left_down_front],
                                                      dtype=np.int32)
                    voxels[voxel_id][6, :] = np.array([left_up_back, left_up_front, right_down_back, right_down_front],
                                                      dtype=np.int32)
                    voxels[voxel_id][7, :] = np.array([right_up_back, right_up_front, 0, 0], dtype=np.int32)

        return np.vstack([voxel_matrices for voxel_matrices in voxels])


class Demo:
    def __init__(self, file, voxel_length):
        self.voxel_length = voxel_length
        self.TRIANGLE_NUMBER = 0
        self.voxel = Voxelization(file, self.voxel_length)
        self.vertex_buffer = self.voxel.vertex_buffer
        self.normal_buffer = self.voxel.normal_buffer
        self.triangle_buffer = self.voxel.triangle_buffer
        self.voxel_buffer = self.voxel.voxel_buffer
        self.triangle_number = self.triangle_buffer.shape[0]
        self.voxel_position_offset = self.voxel.voxel_position_offset

        # initialize OpenGL
        # vertex_buffer
        self.sbo_vertices = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.sbo_vertices)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.sbo_vertices)
        glNamedBufferStorage(self.sbo_vertices, self.vertex_buffer.nbytes, self.vertex_buffer, GL_DYNAMIC_STORAGE_BIT)

        # normal_buffer
        self.sbo_normals = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.sbo_normals)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.sbo_normals)
        glNamedBufferStorage(self.sbo_normals, self.normal_buffer.nbytes, self.normal_buffer, GL_DYNAMIC_STORAGE_BIT)

        # triangle_buffer
        self.sbo_triangles = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.sbo_triangles)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, self.sbo_triangles)
        glNamedBufferStorage(self.sbo_triangles, self.triangle_buffer.nbytes, self.triangle_buffer,
                             GL_DYNAMIC_STORAGE_BIT)
        # voxel_buffer
        self.sbo_voxels = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.sbo_voxels)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3, self.sbo_voxels)
        glNamedBufferStorage(self.sbo_voxels, 1280000000, None, GL_DYNAMIC_STORAGE_BIT)
        glNamedBufferSubData(self.sbo_voxels, 0, self.voxel_buffer.nbytes, self.voxel_buffer)
        # compute shader
        self.need_init = True

        # compute shader 0
        self.compute_shader_0 = compileProgram(
            compileShader(open("voxelization.shader", "rb"), GL_COMPUTE_SHADER))

        self.c_voxel_length_loc = glGetUniformLocation(self.compute_shader_0, "voxel_length")
        self.c_triangle_number_loc = glGetUniformLocation(self.compute_shader_0, "triangle_number")
        self.c_voxel_position_offset_loc = glGetUniformLocation(self.compute_shader_0, "voxel_position_offset")
        glUseProgram(self.compute_shader_0)
        glUniform4fv(self.c_voxel_length_loc, 1,
                     pyrr.Vector4([self.voxel_length, self.voxel_length, self.voxel_length, self.voxel_length]))
        glUniform1i(self.c_triangle_number_loc, self.triangle_number)
        glUniform4fv(self.c_voxel_position_offset_loc, 1, self.voxel_position_offset)
        # render shader
        self.render_shader = compileProgram(compileShader(open("voxel_vertex.shader", "rb"), GL_VERTEX_SHADER),
                                            compileShader(open("voxel_geometry.shader", "rb"), GL_GEOMETRY_SHADER),
                                            compileShader(open("voxel_fragment.shader", "rb"), GL_FRAGMENT_SHADER))
        glUseProgram(self.render_shader)

        self.projection_loc = glGetUniformLocation(self.render_shader, "projection")
        self.view_loc = glGetUniformLocation(self.render_shader, "view")
        self.voxel_length_loc = glGetUniformLocation(self.render_shader, "voxel_length")
        self.voxel_position_offset_loc = glGetUniformLocation(self.render_shader, "voxel_position_offset")

        glUniform4fv(self.voxel_length_loc, 1,
                     np.array([self.voxel_length, self.voxel_length, self.voxel_length, self.voxel_length],
                              dtype=np.float32))
        glUniform4fv(self.voxel_position_offset_loc, 1, self.voxel_position_offset)

        # render_obj shader
        self.obj_render_shader = compileProgram(compileShader(open("vertex.shader", "rb"), GL_VERTEX_SHADER),
                                                compileShader(open("geometry.shader", "rb"), GL_GEOMETRY_SHADER),
                                                compileShader(open("fragment.shader", "rb"), GL_FRAGMENT_SHADER))
        glUseProgram(self.obj_render_shader)

        self.obj_projection_loc = glGetUniformLocation(self.obj_render_shader, "projection")
        self.obj_view_loc = glGetUniformLocation(self.obj_render_shader, "view")

        # vao of indices
        self.indices_buffer = np.array([i for i in range(10000000)], dtype=np.int32)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.indices_buffer.nbytes, self.indices_buffer, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribIPointer(0, 1, GL_INT, 4, ctypes.c_void_p(0))

    def __call__(self, pause=False, update_voxel=False):
        if self.need_init:
            self.need_init = False
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

            glUseProgram(self.compute_shader_0)
            total_invocations = self.voxel_buffer.shape[0] // 8
            glDispatchCompute(total_invocations, 1, 1)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)

            tmp = np.zeros_like(self.voxel_buffer)
            glGetNamedBufferSubData(self.sbo_voxels, 0, self.voxel_buffer.nbytes, tmp)
            buffer = np.frombuffer(tmp,
                                   dtype=np.int32)
            buffer = buffer.reshape((-1, 8, 4))
            count = 0
            tmp = [0 for _ in range(buffer.shape[0])]
            new_buffer = []
            for voxel in buffer:
                if voxel[-1, -1] != 0 or voxel[-1, -2] != 0:
                    count += 1
                    new_buffer.append(voxel)
                    tmp[voxel[0, 0] - 1] = count
            for voxel in new_buffer:
                voxel[0, 0] = tmp[voxel[0, 0] - 1]
                for i in range(4, 30):
                    voxel[i // 4, i % 4] = tmp[voxel[i // 4, i % 4] - 1]
                # voxel[-1, -1] = 0
                # voxel[-1, -2] = 0
            buffer = np.array(new_buffer, dtype=np.int32)
            buffer = buffer.reshape((-1, 4))
            print(buffer.shape, "here")
            np.save("buffer.npy", buffer)
            self.voxel_buffer = buffer
            # glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.sbo_voxels)
            glNamedBufferSubData(self.sbo_voxels, 0, self.voxel_buffer.nbytes, self.voxel_buffer)

        if update_voxel:
            self.voxel_buffer = Refine(self.voxel_buffer).refine()

            glNamedBufferSubData(self.sbo_voxels, 0, self.voxel_buffer.nbytes, self.voxel_buffer)
            glUseProgram(self.compute_shader_0)
            self.voxel_length /= 2
            self.voxel_position_offset -= np.array([self.voxel_length, self.voxel_length, self.voxel_length, 0.0],
                                                   dtype=np.float32)
            glUniform4fv(self.c_voxel_length_loc, 1,
                         pyrr.Vector4([self.voxel_length, self.voxel_length, self.voxel_length, self.voxel_length]))
            glUniform4fv(self.c_voxel_position_offset_loc, 1, self.voxel_position_offset)
            self.need_init = True
            glUseProgram(self.render_shader)
            glUniform4fv(self.voxel_length_loc, 1,
                         np.array([self.voxel_length, self.voxel_length, self.voxel_length, self.voxel_length],
                                  dtype=np.float32))
            glUniform4fv(self.voxel_position_offset_loc, 1, self.voxel_position_offset)

        glBindVertexArray(self.vao)

        glUseProgram(self.render_shader)

        glLineWidth(5)
        glDrawArrays(GL_POINTS, 0, self.voxel_buffer.shape[0] // 8)

        glUseProgram(self.obj_render_shader)
        glDrawArrays(GL_POINTS, 0, self.triangle_number)


if __name__ == "__main__":
    file = r"C:\Users\cchen\PycharmProjects\VoxelizationAlg/H03_object.obj"
    v = Voxelization(file, 0.1)
