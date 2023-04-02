import numpy as np


class Refine:
    def __init__(self, voxel_buffer):
        self.voxel_buffer = voxel_buffer.reshape((-1, 8, 4))

    def refine(self):
        """
        Each voxel is subdivided into 8 parts.
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
        for each voxel:
            original center = (x_id, y_id, z_id)
            (0, 0, 0) -> (0, 0, 0), (1, 1, 1)
            (1, 1, 1) -> (2, 2, 2), (3, 3, 3)
            (1, 0, 0) -> (2, 0, 0), (3, 1, 1)
            (i, j, k) -> (2i, 2j, 2k), (2i+1, 2j+2, 2k+1)
            new_centers = [
                (2*x_id, 2*y_id, 2*z_id),  # left below --> No.0
                (2*x_id+1, 2*y_id, 2*z_id),  # right below --> No.1
                (2*x_id, 2*y_id+1, 2*z_id),  # left up --> No.2
                (2*x_id, 2*y_id, 2*z_id+1),  # left front --> No.3
                (2*x_id+1, 2*y_id+1, 2*z_id),  # right up --> No.4
                (2*x_id, 2*y_id+1, 2*z_id+1),  # left up front --> No.5
                (2*x_id+1, 2*y_id, 2*z_id+1),  # right front --> No.6
                (2*x_id+1, 2*y_id+1, 2*z_id+1)  # right up front --> No.7
            ]

        :return: subdivided voxel buffer
        """
        n = self.voxel_buffer.shape[0] * 8
        domain_mat = np.zeros((n, 2 * 4, 4), dtype=np.int32)
        for i, voxel in enumerate(self.voxel_buffer):
            """
            8 new voxels
            id, x_id, y_id, z_id
            topology requires future data? --> no
            neighborhood 26 voxels' id are known
            new voxels in neighborhood 26 voxels are fixed.
            consider them one by one
            """
            x_id, y_id, z_id = voxel[0, 1:]
            try:
                assert i == voxel[0, 0] - 1  # sanity check
            except AssertionError:
                raise AssertionError("Index not match!")
            v1, v2, v3, v4, v5, v6, v7, v8 = np.zeros((8, 8, 4), dtype=np.int32)
            v1[0, :] = np.array([8 * i + 1, 2 * x_id, 2 * y_id, 2 * z_id], dtype=np.int32)
            v2[0, :] = np.array([8 * i + 2, 2 * x_id + 1, 2 * y_id, 2 * z_id], dtype=np.int32)
            v3[0, :] = np.array([8 * i + 3, 2 * x_id, 2 * y_id + 1, 2 * z_id], dtype=np.int32)
            v4[0, :] = np.array([8 * i + 4, 2 * x_id, 2 * y_id, 2 * z_id + 1], dtype=np.int32)
            v5[0, :] = np.array([8 * i + 5, 2 * x_id + 1, 2 * y_id + 1, 2 * z_id], dtype=np.int32)
            v6[0, :] = np.array([8 * i + 6, 2 * x_id, 2 * y_id + 1, 2 * z_id + 1], dtype=np.int32)
            v7[0, :] = np.array([8 * i + 7, 2 * x_id + 1, 2 * y_id, 2 * z_id + 1], dtype=np.int32)
            v8[0, :] = np.array([8 * i + 8, 2 * x_id + 1, 2 * y_id + 1, 2 * z_id + 1], dtype=np.int32)
            # check topology for current voxel
            left = self.voxel_buffer[voxel[1, 0] - 1] if voxel[1, 0] != 0 else None
            right = self.voxel_buffer[voxel[1, 1] - 1] if voxel[1, 1] != 0 else None
            down = self.voxel_buffer[voxel[1, 2] - 1] if voxel[1, 2] != 0 else None
            up = self.voxel_buffer[voxel[1, 3] - 1] if voxel[1, 3] != 0 else None
            back = self.voxel_buffer[voxel[2, 0] - 1] if voxel[2, 0] != 0 else None
            front = self.voxel_buffer[voxel[2, 1] - 1] if voxel[2, 1] != 0 else None
            left_down = self.voxel_buffer[voxel[2, 2] - 1] if voxel[2, 2] != 0 else None
            left_up = self.voxel_buffer[voxel[2, 3] - 1] if voxel[2, 3] != 0 else None
            right_down = self.voxel_buffer[voxel[3, 0] - 1] if voxel[3, 0] != 0 else None
            right_up = self.voxel_buffer[voxel[3, 1] - 1] if voxel[3, 1] != 0 else None
            left_back = self.voxel_buffer[voxel[3, 2] - 1] if voxel[3, 2] != 0 else None
            left_front = self.voxel_buffer[voxel[3, 3] - 1] if voxel[3, 3] != 0 else None
            right_back = self.voxel_buffer[voxel[4, 0] - 1] if voxel[4, 0] != 0 else None
            right_front = self.voxel_buffer[voxel[4, 1] - 1] if voxel[4, 1] != 0 else None
            down_back = self.voxel_buffer[voxel[4, 2] - 1] if voxel[4, 2] != 0 else None
            down_front = self.voxel_buffer[voxel[4, 3] - 1] if voxel[4, 3] != 0 else None
            up_back = self.voxel_buffer[voxel[5, 0] - 1] if voxel[5, 0] != 0 else None
            up_front = self.voxel_buffer[voxel[5, 1] - 1] if voxel[5, 1] != 0 else None
            left_down_back = self.voxel_buffer[voxel[5, 2] - 1] if voxel[5, 2] != 0 else None
            left_down_front = self.voxel_buffer[voxel[5, 3] - 1] if voxel[5, 3] != 0 else None
            left_up_back = self.voxel_buffer[voxel[6, 0] - 1] if voxel[6, 0] != 0 else None
            left_up_front = self.voxel_buffer[voxel[6, 1] - 1] if voxel[6, 1] != 0 else None
            right_down_back = self.voxel_buffer[voxel[6, 2] - 1] if voxel[6, 2] != 0 else None
            right_down_front = self.voxel_buffer[voxel[6, 3] - 1] if voxel[6, 3] != 0 else None
            right_up_back = self.voxel_buffer[voxel[7, 0] - 1] if voxel[7, 0] != 0 else None
            right_up_front = self.voxel_buffer[voxel[7, 1] - 1] if voxel[7, 1] != 0 else None
            # check topology for v1
            v1_left = 8 * (left[0, 0] - 1) + 2 if left is not None else 0  # -+*-
            v1_right = v2[0, 0]
            v1_down = 8 * (down[0, 0] - 1) + 3 if down is not None else 0
            v1_up = v3[0, 0]
            v1_back = 8 * (back[0, 0] - 1) + 4 if back is not None else 0
            v1_front = v4[0, 0]
            v1_left_down = 8 * (left_down[0, 0] - 1) + 5 if left_down is not None else 0
            v1_left_up = 8 * (left[0, 0] - 1) + 5 if left is not None else 0
            v1_right_down = 8 * (down[0, 0] - 1) + 5 if down is not None else 0
            v1_right_up = v5[0, 0]
            v1_left_back = 8 * (left_back[0, 0] - 1) + 7 if left_back is not None else 0
            v1_left_front = 8 * (left[0, 0] - 1) + 7 if left is not None else 0
            v1_right_back = 8 * (back[0, 0] - 1) + 7 if back is not None else 0
            v1_right_front = v7[0, 0]
            v1_down_back = 8 * (down_back[0, 0] - 1) + 6 if down_back is not None else 0
            v1_down_front = 8 * (down[0, 0] - 1) + 6 if down is not None else 0
            v1_up_back = 8 * (back[0, 0] - 1) + 6 if back is not None else 0
            v1_up_front = v6[0, 0]
            v1_left_down_back = 8 * (left_down_back[0, 0] - 1) + 8 if left_down_back is not None else 0
            v1_left_down_front = 8 * (left_down[0, 0] - 1) + 8 if left_down is not None else 0
            v1_left_up_back = 8 * (left_back[0, 0] - 1) + 8 if left_back is not None else 0
            v1_left_up_front = 8 * (left[0, 0] - 1) + 8 if left is not None else 0
            v1_right_down_back = 8 * (down_back[0, 0] - 1) + 8 if down_back is not None else 0
            v1_right_down_front = 8 * (down[0, 0] - 1) + 8 if down is not None else 0
            v1_right_up_back = 8 * (back[0, 0] - 1) + 8 if back is not None else 0
            v1_right_up_front = v8[0, 0]
            v1[1:, :] = np.array([[v1_left, v1_right, v1_down, v1_up],
                                  [v1_back, v1_front, v1_left_down, v1_left_up],
                                  [v1_right_down, v1_right_up, v1_left_back, v1_left_front],
                                  [v1_right_back, v1_right_front, v1_down_back, v1_down_front],
                                  [v1_up_back, v1_up_front, v1_left_down_back, v1_left_down_front],
                                  [v1_left_up_back, v1_left_up_front, v1_right_down_back, v1_right_down_front],
                                  [v1_right_up_back, v1_right_up_front, 0, 0]], dtype=np.int32)
            # check topology for v2
            v2_left = v1[0, 0]  # --+*--
            v2_right = 8 * (right[0, 0] - 1) + 1 if right is not None else 0
            v2_down = 8 * (down[0, 0] - 1) + 5 if down is not None else 0
            v2_up = v5[0, 0]
            v2_back = 8 * (back[0, 0] - 1) + 7 if back is not None else 0
            v2_front = v7[0, 0]
            v2_left_down = 8 * (down[0, 0] - 1) + 3 if down is not None else 0
            v2_left_up = v3[0, 0]
            v2_right_down = 8 * (right_down[0, 0] - 1) + 3 if right_down is not None else 0
            v2_right_up = 8 * (right[0, 0] - 1) + 3 if right is not None else 0
            v2_left_back = 8 * (back[0, 0] - 1) + 4 if back is not None else 0
            v2_left_front = v4[0, 0]
            v2_right_back = 8 * (right_back[0, 0] - 1) + 4 if right_back is not None else 0
            v2_right_front = 8 * (right[0, 0] - 1) + 4 if right is not None else 0
            v2_down_back = 8 * (down_back[0, 0] - 1) + 8 if down_back is not None else 0
            v2_down_front = 8 * (down[0, 0] - 1) + 8 if down is not None else 0
            v2_up_back = 8 * (back[0, 0] - 1) + 8 if back is not None else 0
            v2_up_front = v8[0, 0]
            v2_left_down_back = 8 * (down_back[0, 0] - 1) + 6 if down_back is not None else 0
            v2_left_down_front = 8 * (down[0, 0] - 1) + 6 if down is not None else 0
            v2_left_up_back = 8 * (back[0, 0] - 1) + 6 if back is not None else 0
            v2_left_up_front = v6[0, 0]
            v2_right_down_back = 8 * (right_down_back[0, 0] - 1) + 6 if right_down_back is not None else 0
            v2_right_down_front = 8 * (right_down[0, 0] - 1) + 6 if right_down is not None else 0
            v2_right_up_back = 8 * (right_back[0, 0] - 1) + 6 if right_back is not None else 0
            v2_right_up_front = 8 * (right[0, 0] - 1) + 6 if right is not None else 0
            v2[1:, :] = np.array([[v2_left, v2_right, v2_down, v2_up],
                                  [v2_back, v2_front, v2_left_down, v2_left_up],
                                  [v2_right_down, v2_right_up, v2_left_back, v2_left_front],
                                  [v2_right_back, v2_right_front, v2_down_back, v2_down_front],
                                  [v2_up_back, v2_up_front, v2_left_down_back, v2_left_down_front],
                                  [v2_left_up_back, v2_left_up_front, v2_right_down_back, v2_right_down_front],
                                  [v2_right_up_back, v2_right_up_front, 0, 0]], dtype=np.int32)
            # check topology for v3
            v3_left = 8 * (left[0, 0] - 1) + 5 if left is not None else 0  # -+*-
            v3_right = v5[0, 0]
            v3_down = v1[0, 0]
            v3_up = 8 * (up[0, 0] - 1) + 1 if up is not None else 0
            v3_back = 8 * (back[0, 0] - 1) + 6 if back is not None else 0
            v3_front = v6[0, 0]
            v3_left_down = 8 * (left[0, 0] - 1) + 2 if left is not None else 0
            v3_left_up = 8 * (left_up[0, 0] - 1) + 2 if left_up is not None else 0
            v3_right_down = v2[0, 0]
            v3_right_up = 8 * (up[0, 0] - 1) + 2 if up is not None else 0
            v3_left_back = 8 * (left_back[0, 0] - 1) + 8 if left_back is not None else 0
            v3_left_front = 8 * (left[0, 0] - 1) + 8 if left is not None else 0
            v3_right_back = 8 * (back[0, 0] - 1) + 8 if back is not None else 0
            v3_right_front = v8[0, 0]
            v3_down_back = 8 * (back[0, 0] - 1) + 4 if back is not None else 0
            v3_down_front = v4[0, 0]
            v3_up_back = 8 * (up_back[0, 0] - 1) + 4 if up_back is not None else 0
            v3_up_front = 8 * (up[0, 0] - 1) + 4 if up is not None else 0
            v3_left_down_back = 8 * (left_back[0, 0] - 1) + 7 if left_back is not None else 0
            v3_left_down_front = 8 * (left[0, 0] - 1) + 7 if left is not None else 0
            v3_left_up_back = 8 * (left_up_back[0, 0] - 1) + 7 if left_up_back is not None else 0
            v3_left_up_front = 8 * (left_up[0, 0] - 1) + 7 if left_up is not None else 0
            v3_right_down_back = 8 * (back[0, 0] - 1) + 7 if back is not None else 0
            v3_right_down_front = v7[0, 0]
            v3_right_up_back = 8 * (up_back[0, 0] - 1) + 7 if up_back is not None else 0
            v3_right_up_front = 8 * (up[0, 0] - 1) + 7 if up is not None else 0
            v3[1:, :] = np.array([[v3_left, v3_right, v3_down, v3_up],
                                  [v3_back, v3_front, v3_left_down, v3_left_up],
                                  [v3_right_down, v3_right_up, v3_left_back, v3_left_front],
                                  [v3_right_back, v3_right_front, v3_down_back, v3_down_front],
                                  [v3_up_back, v3_up_front, v3_left_down_back, v3_left_down_front],
                                  [v3_left_up_back, v3_left_up_front, v3_right_down_back, v3_right_down_front],
                                  [v3_right_up_back, v3_right_up_front, 0, 0]], dtype=np.int32)
            # check topology for v4
            v4_left = 8 * (left[0, 0] - 1) + 7 if left is not None else 0
            v4_right = v7[0, 0]
            v4_down = 8 * (down[0, 0] - 1) + 6 if down is not None else 0
            v4_up = v6[0, 0]
            v4_back = v1[0, 0]
            v4_front = 8 * (front[0, 0] - 1) + 1 if front is not None else 0
            v4_left_down = 8 * (left_down[0, 0] - 1) + 8 if left_down is not None else 0
            v4_left_up = 8 * (left[0, 0] - 1) + 8 if left is not None else 0
            v4_right_down = 8 * (down[0, 0] - 1) + 8 if down is not None else 0
            v4_right_up = v8[0, 0]
            v4_left_back = 8 * (left[0, 0] - 1) + 2 if left is not None else 0
            v4_left_front = 8 * (left_front[0, 0] - 1) + 2 if left_front is not None else 0
            v4_right_back = v2[0, 0]
            v4_right_front = 8 * (front[0, 0] - 1) + 2 if front is not None else 0
            v4_down_back = 8 * (down[0, 0] - 1) + 3 if down is not None else 0
            v4_down_front = 8 * (down_front[0, 0] - 1) + 3 if down_front is not None else 0
            v4_up_back = v3[0, 0]
            v4_up_front = 8 * (front[0, 0] - 1) + 3 if front is not None else 0
            v4_left_down_back = 8 * (left_down[0, 0] - 1) + 5 if left_down is not None else 0
            v4_left_down_front = 8 * (left_down_front[0, 0] - 1) + 5 if left_down_front is not None else 0
            v4_left_up_back = 8 * (left[0, 0] - 1) + 5 if left is not None else 0
            v4_left_up_front = 8 * (left_front[0, 0] - 1) + 5 if left_front is not None else 0
            v4_right_down_back = 8 * (down[0, 0] - 1) + 5 if down is not None else 0
            v4_right_down_front = 8 * (down_front[0, 0] - 1) + 5 if down_front is not None else 0
            v4_right_up_back = v5[0, 0]
            v4_right_up_front = 8 * (front[0, 0] - 1) + 5 if front is not None else 0
            v4[1:, :] = np.array([[v4_left, v4_right, v4_down, v4_up],
                                  [v4_back, v4_front, v4_left_down, v4_left_up],
                                  [v4_right_down, v4_right_up, v4_left_back, v4_left_front],
                                  [v4_right_back, v4_right_front, v4_down_back, v4_down_front],
                                  [v4_up_back, v4_up_front, v4_left_down_back, v4_left_down_front],
                                  [v4_left_up_back, v4_left_up_front, v4_right_down_back, v4_right_down_front],
                                  [v4_right_up_back, v4_right_up_front, 0, 0]], dtype=np.int32)
            # check topology for v5
            v5_left = v3[0, 0]
            v5_right = 8 * (right[0, 0] - 1) + 3 if right is not None else 0
            v5_down = v2[0, 0]
            v5_up = 8 * (up[0, 0] - 1) + 2 if up is not None else 0
            v5_back = 8 * (back[0, 0] - 1) + 8 if back is not None else 0
            v5_front = v8[0, 0]
            v5_left_down = v1[0, 0]
            v5_left_up = 8 * (up[0, 0] - 1) + 1 if up is not None else 0
            v5_right_down = 8 * (right[0, 0] - 1) + 1 if right is not None else 0
            v5_right_up = 8 * (right_up[0, 0] - 1) + 1 if right_up is not None else 0
            v5_left_back = 8 * (back[0, 0] - 1) + 6 if back is not None else 0
            v5_left_front = v6[0, 0]
            v5_right_back = 8 * (right_back[0, 0] - 1) + 6 if right_back is not None else 0
            v5_right_front = 8 * (right[0, 0] - 1) + 6 if right is not None else 0
            v5_down_back = 8 * (back[0, 0] - 1) + 7 if back is not None else 0
            v5_down_front = v7[0, 0]
            v5_up_back = 8 * (up_back[0, 0] - 1) + 7 if up_back is not None else 0
            v5_up_front = 8 * (up[0, 0] - 1) + 7 if up is not None else 0
            v5_left_down_back = 8 * (back[0, 0] - 1) + 4 if back is not None else 0
            v5_left_down_front = v4[0, 0]
            v5_left_up_back = 8 * (up_back[0, 0] - 1) + 4 if up_back is not None else 0
            v5_left_up_front = 8 * (up[0, 0] - 1) + 4 if up is not None else 0
            v5_right_down_back = 8 * (right_back[0, 0] - 1) + 4 if right_back is not None else 0
            v5_right_down_front = 8 * (right[0, 0] - 1) + 4 if right is not None else 0
            v5_right_up_back = 8 * (right_up_back[0, 0] - 1) + 4 if right_up_back is not None else 0
            v5_right_up_front = 8 * (right_up[0, 0] - 1) + 4 if right_up is not None else 0
            v5[1:, :] = np.array([[v5_left, v5_right, v5_down, v5_up],
                                  [v5_back, v5_front, v5_left_down, v5_left_up],
                                  [v5_right_down, v5_right_up, v5_left_back, v5_left_front],
                                  [v5_right_back, v5_right_front, v5_down_back, v5_down_front],
                                  [v5_up_back, v5_up_front, v5_left_down_back, v5_left_down_front],
                                  [v5_left_up_back, v5_left_up_front, v5_right_down_back, v5_right_down_front],
                                  [v5_right_up_back, v5_right_up_front, 0, 0]], dtype=np.int32)
            # check topology for v6
            v6_left = 8 * (left[0, 0] - 1) + 8 if left is not None else 0
            v6_right = v8[0, 0]
            v6_down = v4[0, 0]
            v6_up = 8 * (up[0, 0] - 1) + 4 if up is not None else 0
            v6_back = v3[0, 0]
            v6_front = 8 * (front[0, 0] - 1) + 3 if front is not None else 0
            v6_left_down = 8 * (left[0, 0] - 1) + 7 if left is not None else 0
            v6_left_up = 8 * (left_up[0, 0] - 1) + 7 if left_up is not None else 0
            v6_right_down = v7[0, 0]
            v6_right_up = 8 * (up[0, 0] - 1) + 7 if up is not None else 0
            v6_left_back = 8 * (left[0, 0] - 1) + 5 if left is not None else 0
            v6_left_front = 8 * (left_front[0, 0] - 1) + 5 if left_front is not None else 0
            v6_right_back = v5[0, 0]
            v6_right_front = 8 * (front[0, 0] - 1) + 5 if front is not None else 0
            v6_down_back = v1[0, 0]
            v6_down_front = 8 * (front[0, 0] - 1) + 1 if front is not None else 0
            v6_up_back = 8 * (up[0, 0] - 1) + 1 if up is not None else 0
            v6_up_front = 8 * (up_front[0, 0] - 1) + 1 if up_front is not None else 0
            v6_left_down_back = 8 * (left[0, 0] - 1) + 2 if left is not None else 0
            v6_left_down_front = 8 * (left_front[0, 0] - 1) + 2 if left_front is not None else 0
            v6_left_up_back = 8 * (left_up[0, 0] - 1) + 2 if left_up is not None else 0
            v6_left_up_front = 8 * (left_up_front[0, 0] - 1) + 2 if left_up_front is not None else 0
            v6_right_down_back = v2[0, 0]
            v6_right_down_front = 8 * (front[0, 0] - 1) + 2 if front is not None else 0
            v6_right_up_back = 8 * (up[0, 0] - 1) + 2 if up is not None else 0
            v6_right_up_front = 8 * (up_front[0, 0] - 1) + 2 if up_front is not None else 0
            v6[1:, :] = np.array([[v6_left, v6_right, v6_down, v6_up],
                                  [v6_back, v6_front, v6_left_down, v6_left_up],
                                  [v6_right_down, v6_right_up, v6_left_back, v6_left_front],
                                  [v6_right_back, v6_right_front, v6_down_back, v6_down_front],
                                  [v6_up_back, v6_up_front, v6_left_down_back, v6_left_down_front],
                                  [v6_left_up_back, v6_left_up_front, v6_right_down_back, v6_right_down_front],
                                  [v6_right_up_back, v6_right_up_front, 0, 0]], dtype=np.int32)
            # check topology for v7
            v7_left = v4[0, 0]
            v7_right = 8 * (right[0, 0] - 1) + 4 if right is not None else 0
            v7_down = 8 * (down[0, 0] - 1) + 8 if down is not None else 0
            v7_up = v8[0, 0]
            v7_back = v2[0, 0]
            v7_front = 8 * (front[0, 0] - 1) + 2 if front is not None else 0
            v7_left_down = 8 * (down[0, 0] - 1) + 6 if down is not None else 0
            v7_left_up = v6[0, 0]
            v7_right_down = 8 * (right_down[0, 0] - 1) + 6 if right_down is not None else 0
            v7_right_up = 8 * (right[0, 0] - 1) + 6 if right is not None else 0
            v7_left_back = v1[0, 0]
            v7_left_front = 8 * (front[0, 0] - 1) + 1 if front is not None else 0
            v7_right_back = 8 * (right[0, 0] - 1) + 1 if right is not None else 0
            v7_right_front = 8 * (right_front[0, 0] - 1) + 1 if right_front is not None else 0
            v7_down_back = 8 * (down[0, 0] - 1) + 5 if down is not None else 0
            v7_down_front = 8 * (down_front[0, 0] - 1) + 5 if down_front is not None else 0
            v7_up_back = v5[0, 0]
            v7_up_front = 8 * (front[0, 0] - 1) + 5 if front is not None else 0
            v7_left_down_back = 8 * (down[0, 0] - 1) + 3 if down is not None else 0
            v7_left_down_front = 8 * (down_front[0, 0] - 1) + 3 if down_front is not None else 0
            v7_left_up_back = v3[0, 0]
            v7_left_up_front = 8 * (front[0, 0] - 1) + 3 if front is not None else 0
            v7_right_down_back = 8 * (right_down[0, 0] - 1) + 3 if right_down is not None else 0
            v7_right_down_front = 8 * (right_down_front[0, 0] - 1) + 3 if right_down_front is not None else 0
            v7_right_up_back = 8 * (right[0, 0] - 1) + 3 if right is not None else 0
            v7_right_up_front = 8 * (right_front[0, 0] - 1) + 3 if right_front is not None else 0
            v7[1:, :] = np.array([[v7_left, v7_right, v7_down, v7_up],
                                  [v7_back, v7_front, v7_left_down, v7_left_up],
                                  [v7_right_down, v7_right_up, v7_left_back, v7_left_front],
                                  [v7_right_back, v7_right_front, v7_down_back, v7_down_front],
                                  [v7_up_back, v7_up_front, v7_left_down_back, v7_left_down_front],
                                  [v7_left_up_back, v7_left_up_front, v7_right_down_back, v7_right_down_front],
                                  [v7_right_up_back, v7_right_up_front, 0, 0]], dtype=np.int32)
            # check topology for v8
            v8_left = v6[0, 0]
            v8_right = 8 * (right[0, 0] - 1) + 6 if right is not None else 0
            v8_down = v7[0, 0]
            v8_up = 8 * (up[0, 0] - 1) + 7 if up is not None else 0
            v8_back = v5[0, 0]
            v8_front = 8 * (front[0, 0] - 1) + 5 if front is not None else 0
            v8_left_down = v4[0, 0]
            v8_left_up = 8 * (up[0, 0] - 1) + 4 if up is not None else 0
            v8_right_down = 8 * (right[0, 0] - 1) + 4 if right is not None else 0
            v8_right_up = 8 * (right_up[0, 0] - 1) + 4 if right_up is not None else 0
            v8_left_back = v3[0, 0]
            v8_left_front = 8 * (front[0, 0] - 1) + 3 if front is not None else 0
            v8_right_back = 8 * (right[0, 0] - 1) + 3 if right is not None else 0
            v8_right_front = 8 * (right_front[0, 0] - 1) + 3 if right_front is not None else 0
            v8_down_back = v2[0, 0]
            v8_down_front = 8 * (front[0, 0] - 1) + 2 if front is not None else 0
            v8_up_back = 8 * (up[0, 0] - 1) + 2 if up is not None else 0
            v8_up_front = 8 * (up_front[0, 0] - 1) + 2 if up_front is not None else 0
            v8_left_down_back = v1[0, 0]
            v8_left_down_front = 8 * (front[0, 0] - 1) + 1 if front is not None else 0
            v8_left_up_back = 8 * (up[0, 0] - 1) + 1 if up is not None else 0
            v8_left_up_front = 8 * (up_front[0, 0] - 1) + 1 if up_front is not None else 0
            v8_right_down_back = 8 * (right[0, 0] - 1) + 1 if right is not None else 0
            v8_right_down_front = 8 * (right_front[0, 0] - 1) + 1 if right_front is not None else 0
            v8_right_up_back = 8 * (right_up[0, 0] - 1) + 1 if right_up is not None else 0
            v8_right_up_front = 8 * (right_up_front[0, 0] - 1) + 1 if right_up_front is not None else 0
            v8[1:, :] = np.array([[v8_left, v8_right, v8_down, v8_up],
                                  [v8_back, v8_front, v8_left_down, v8_left_up],
                                  [v8_right_down, v8_right_up, v8_left_back, v8_left_front],
                                  [v8_right_back, v8_right_front, v8_down_back, v8_down_front],
                                  [v8_up_back, v8_up_front, v8_left_down_back, v8_left_down_front],
                                  [v8_left_up_back, v8_left_up_front, v8_right_down_back, v8_right_down_front],
                                  [v8_right_up_back, v8_right_up_front, 0, 0]], dtype=np.int32)
            for v in [v1, v2, v3, v4, v5, v6, v7, v8]:
                domain_mat[v[0, 0]-1, :, :] = v
        return np.vstack([voxel_matrices for voxel_matrices in domain_mat])
