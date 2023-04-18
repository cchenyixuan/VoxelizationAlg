import numpy as np


class ParticleGenerator:
    """
    A particle generator for SPH Fluid simulator
    """

    def __init__(self, voxel_buffer, smooth_length, particle_radius):
        self.voxel_buffer = voxel_buffer
        self.H = smooth_length
        self.R = particle_radius

    def __call__(self, *args, **kwargs):
        ...

    def generate_internal_particle(self):
        """
        |_*____|
        |____*_|
        |_*____|
        Particles inside the voxels marked as internal should be uniformly separated.
        Maximum particle inside a voxel should be less than the capacity 60*16.

        :return:
        """
        count = int(self.H**3//(self.R**3*np.pi*4/3))

        ...

    def generate_boundary_particle(self):
        """Beta Version"""
        ...
