import numpy as np

"""
["i", "x", "y", "z"],
["Left", "Right", "Down", "Up"],
["Back", "Front", "LeftDown", "LeftUp"],
["RightDown", "RightUp", "LeftBack", "LeftFront"],
["RightBack", "RightFront", "DownBack", "DownFront"],
["UpBack", "UpFront", "LeftDownBack", "LeftDownFront"],
["LeftUpBack", "LeftUpFront", "RightDownBack", "RightDownFront"],
["RightUpBack", "RightUpFront", "0", "0"],
"""


class Voxel:
    def __init__(self, x_id, y_id, z_id):
        self.x_id = x_id
        self.y_id = y_id
        self.z_id = z_id
        self.id = None
        self.left = None
        self.right = None
        self.down = None
        self.up = None
        self.back = None
        self.front = None
        self.left_down = None
        self.left_up = None
        self.right_down = None
        self.right_up = None
        self.left_back = None
        self.left_front = None
        self.right_back = None
        self.right_front = None
        self.down_back = None
        self.down_front = None
        self.up_back = None
        self.up_front = None
        self.left_down_back = None
        self.left_down_front = None
        self.left_up_back = None
        self.left_up_front = None
        self.right_down_back = None
        self.right_down_front = None
        self.right_up_back = None
        self.right_up_front = None

    def extend(self, max_x, amx_y, max_z, min_x=0, min_y=0, min_z=0):
        if self.left is None and min_x < self.x_id:
            self.left = Voxel(self.x_id - 1, self.y_id, self.z_id)
            # self.left.left = None
            self.left.right = self
            self.left.down = self.left_down
            self.left.up = self.left_up
            self.left.back = self.left_back
            self.left.front = self.left_front
            # self.left.left_down = None
            # self.left.left_up = None
            self.left.right_down = self.down
            self.left.right_up = self.up
            # self.left.left_back = None
            # self.left.left_front = None
            self.left.right_back = self.back
            self.left.right_front = self.front
            self.left.down_back = self.left_down_back
            self.left.down_front = self.left_down_front
            self.left.up_back = self.left_up_back
            self.left.up_front = self.left_up_front
            # self.left.left_down_back = None
            # self.left.left_down_front = None
            # self.left.left_up_back = None
            # self.left.left_up_front = None
            self.left.right_down_back = self.down_back
            self.left.right_down_front = self.down_front
            self.left.right_up_back = self.up_back
            self.left.right_up_front = self.up_front
        if self.right is None and self.x_id < max_x:
            self.right = Voxel(self.x_id + 1, self.y_id, self.z_id)
            self.right.left = self
            self.right.right = None
            self.right.down = self.right_down
            self.right.up = self.right_up
            self.right.back = self.right_back
            self.right.front = self.right_front
            self.right.left_down = self.down
            self.right.left_up = self.up
            self.right.right_down = None
            self.right.right_up = None
            self.right.left_back = self.back
            self.right.left_front = self.front
            self.right.right_back = None
            self.right.right_front = None
            self.right.down_back = self.right_down_back
            self.right.down_front = self.right_down_front
            self.right.up_back = self.right_up_back
            self.right.up_front = self.right_up_front
            self.right.left_down_back = self.down_back
            self.right.left_down_front = self.down_front
            self.right.left_up_back = self.up_back
            self.right.left_up_front = self.up_front
            self.right.right_down_back = None
            self.right.right_down_front = None
            self.right.right_up_back = None
            self.right.right_up_front = None


target = np.array([[0, 0, 0], [5, 5, 5]], dtype=np.float32)
length = 0.3


def create_voxels(geometry, voxel_length):
    lower_bound = np.min(geometry, axis=0)
    upper_bound = np.max(geometry, axis=0)

    x = int(np.ceil((upper_bound[0] - lower_bound[0]) / voxel_length) + 1)
    y = int(np.ceil((upper_bound[1] - lower_bound[1]) / voxel_length) + 1)
    z = int(np.ceil((upper_bound[2] - lower_bound[2]) / voxel_length) + 1)
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
                voxels[voxel_id][5, :] = np.array([up_back, up_front, left_down_back, left_down_front], dtype=np.int32)
                voxels[voxel_id][6, :] = np.array([left_up_back, left_up_front, right_down_back, right_down_front],
                                                  dtype=np.int32)
                voxels[voxel_id][7, :] = np.array([right_up_back, right_up_front, 0, 0], dtype=np.int32)

    return np.vstack((voxel_matrices for voxel_matrices in voxels))


if __name__ == "__main__":
    v = create_voxels(target, length)
