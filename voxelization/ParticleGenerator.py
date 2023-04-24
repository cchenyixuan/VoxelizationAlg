import numpy as np


class ParticleGenerator:
    """
    A particle generator for SPH Fluid simulator
    """

    def __init__(self, voxel_buffer, voxel_offset, smooth_length, particle_radius, voxel_attribute_buffer):
        self.voxel_buffer = voxel_buffer
        self.voxel_offset = voxel_offset
        self.voxel_attribute_buffer = voxel_attribute_buffer
        self.H = smooth_length  # same as voxel length
        self.R = particle_radius
        self.D = 2 * self.R

    def __call__(self, *args, **kwargs):
        ...

    def generate_internal_particle(self):
        """
        voxel_buffer is in shape [n, r, c]
        |_*____|
        |____*_|
        |_*____|
        Particles inside the voxels marked as internal should be uniformly separated.
        Maximum particle inside a voxel should be less than the capacity 60*16(=960).

        :return:
        """
        # for any voxel:
        count = int(self.H**3//(self.R**3*np.pi*4/3))  # best below 125
        base = np.array((self.D, self.D, self.D), dtype=np.float32)

        if count < 28:
            x_available = np.array([(-1, 0, 0), (0, 0, 0), (1, 0, 0)], dtype=np.float32)
            y_available = np.array([(0, -1, 0), (0, 0, 0), (0, 1, 0)], dtype=np.float32)
            z_available = np.array([(0, 0, -1), (0, 0, 0), (0, 0, 1)], dtype=np.float32)
        elif count < 126:
            x_available = np.array([(-2, 0, 0), (-1, 0, 0), (0, 0, 0), (1, 0, 0), (2, 0, 0)], dtype=np.float32)
            y_available = np.array([(0, -2, 0), (0, -1, 0), (0, 0, 0), (0, 1, 0), (0, 2, 0)], dtype=np.float32)
            z_available = np.array([(0, 0, -2), (0, 0, -1), (0, 0, 0), (0, 0, 1), (0, 0, 2)], dtype=np.float32)
        elif count < 344:
            x_available = np.array([(-3, 0, 0), (-2, 0, 0), (-1, 0, 0), (0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)], dtype=np.float32)
            y_available = np.array([(0, -3, 0), (0, -2, 0), (0, -1, 0), (0, 0, 0), (0, 1, 0), (0, 2, 0), (0, 3, 0)], dtype=np.float32)
            z_available = np.array([(0, 0, -3), (0, 0, -2), (0, 0, -1), (0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 0, 3)], dtype=np.float32)
        else:
            raise Exception("R is TOO LOW!")

        available_position = []
        for x in x_available:
            for y in y_available:
                for z in z_available:
                    available_position.append((x+y+z)*base)
        available_position = np.array(available_position, dtype=np.float32)
        np.random.shuffle(available_position)

        particles = []
        for attribute, voxel in zip(self.voxel_attribute_buffer, self.voxel_buffer):
            if attribute[0] == 1.0:
                center = self.voxel_offset[:3] + voxel[0, 1:] * self.H
                particles.append(np.array(available_position[:count]) + center)
                np.random.shuffle(available_position)  # optional
        particles = np.vstack(particles)
        with open(r"domain.obj", "w") as f:
            for particle in particles:
                f.write(f"v {particle[0]} {particle[1]} {particle[2]}\n")
        return

    def generate_boundary_particle(self):
        """Beta Version"""
        ...
