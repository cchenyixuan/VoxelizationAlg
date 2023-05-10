import threading
import time

import pyrr
import numpy as np
from OpenGL.GL import *
import glfw
from camera import Camera
import demo


class DisplayPort:
    def __init__(self):
        glfw.init()
        self.window = glfw.create_window(1920, 1080, "Console", None, None)
        glfw.set_window_pos(self.window, 0, 30)
        glfw.hide_window(self.window)
        print("DisplayPort Initialized.")
        self.cursor_position = (0.0, 0.0)
        self.offset = 0
        self.left_click = False
        self.right_click = False
        self.middle_click = False
        self.pause = True
        self.show_vector = False
        self.show_boundary = False
        self.show_voxel = False
        self.record = False
        self.axis = True
        self.current_step = 0
        self.counter = 0
        self.camera = Camera()

        self.view = self.camera()
        self.view_changed = False

        self.update_voxel = False

    def __call__(self, *args, **kwargs):
        glfw.make_context_current(self.window)
        self.demo = demo.Demo(r"D:\ProgramFiles\PycharmProject\SPH-prototype\models\voxel_for.obj", 0.04)
        glUseProgram(self.demo.render_shader)
        glUniformMatrix4fv(self.demo.projection_loc, 1, GL_FALSE, self.camera.projection)
        glUniformMatrix4fv(self.demo.view_loc, 1, GL_FALSE, self.camera.view)
        glUseProgram(self.demo.obj_render_shader)
        glUniformMatrix4fv(self.demo.obj_projection_loc, 1, GL_FALSE, self.camera.projection)
        glUniformMatrix4fv(self.demo.obj_view_loc, 1, GL_FALSE, self.camera.view)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)

        self.track_cursor()

        glfw.show_window(self.window)

        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.demo(update_voxel=self.update_voxel)
            self.update_voxel = False

            if self.view_changed:
                glUseProgram(self.demo.render_shader)
                glUniformMatrix4fv(self.demo.view_loc, 1, GL_FALSE, self.view)
                glUseProgram(self.demo.obj_render_shader)
                glUniformMatrix4fv(self.demo.obj_view_loc, 1, GL_FALSE, self.view)
                self.view_changed = False

            glClearColor(0.0, 0.0, 0.0, 1.0)
            glfw.swap_buffers(self.window)
        glfw.terminate()
        return self.sph_voxel_buffer()

    def sph_voxel_buffer(self):
        buffer = np.zeros((self.demo.voxel_buffer.shape[0]//8, 182*4, 4), dtype=np.int32)
        for step, tmp in enumerate(self.demo.voxel_buffer.reshape((-1, 8, 4))):
            tmp[-1, -1], tmp[-1, -2] = 0, 0
            buffer[step, :8] = tmp
        # np.save("voxel_buffer.npy", buffer)
        # np.save("voxel_offset.npy", self.demo.voxel_position_offset)
        return buffer, self.demo.voxel_position_offset, self.demo.voxel_attribute_buffer

    def track_cursor(self):
        def cursor_position_clb(*args):
            delta = np.array(args[1:], dtype=np.float32) - self.cursor_position[:]
            self.cursor_position = args[1:]
            if self.left_click:
                self.view = self.camera(pyrr.Vector3((*delta, 0.0)), "left")
                self.view_changed = True
                # glUseProgram(self.demo.render_shader_voxel)
                # glUniformMatrix4fv(self.demo.voxel_view_loc, 1, GL_FALSE, mat)
            elif self.middle_click:
                self.view = self.camera(pyrr.Vector3((-delta[0]*0.1, delta[1]*0.1, 0.0)), "middle")
                self.view_changed = True
                # glUseProgram(self.demo.render_shader_voxel)
                # glUniformMatrix4fv(self.demo.voxel_view_loc, 1, GL_FALSE, mat)

        def mouse_press_clb(window, button, action, mods):
            if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
                self.left_click = True
                self.camera.mouse_left = True
            elif button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
                self.left_click = False
                self.camera.mouse_left = False
            if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
                self.right_click = True
                self.camera.mouse_right = True
                self.update_voxel = True
            elif button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.RELEASE:
                self.right_click = False
                self.camera.mouse_right = False

            if button == glfw.MOUSE_BUTTON_MIDDLE and action == glfw.PRESS:
                self.middle_click = True
                self.camera.mouse_middle = True
            elif button == glfw.MOUSE_BUTTON_MIDDLE and action == glfw.RELEASE:
                self.middle_click = False
                self.camera.mouse_middle = False

        def scroll_clb(window, x_offset, y_offset):
            def f():
                # if sum([abs(item) for item in self.camera.position.xyz]) <= 1.01:
                #     if y_offset >= 0:
                #         return
                for i in range(20):
                    self.camera.position += self.camera.front * y_offset * 0.01
                    self.camera.position = pyrr.Vector4([*self.camera.position.xyz, 1.0])
                    self.view = self.camera(flag="wheel")
                    self.view_changed = True
                    time.sleep(0.005)
                    # if abs(sum([*self.camera.position.xyz])) <= 1.01:
                    #     if y_offset >= 0:
                    #         return

            t = threading.Thread(target=f)
            t.start()

        glfw.set_mouse_button_callback(self.window, mouse_press_clb)
        glfw.set_scroll_callback(self.window, scroll_clb)
        glfw.set_cursor_pos_callback(self.window, cursor_position_clb)


if __name__ == "__main__":
    dp = DisplayPort()
    buffer, offset, attribute_buffer = dp()
    # from ParticleGenerator import ParticleGenerator
    # pg = ParticleGenerator(buffer, offset, dp.demo.voxel_length, dp.demo.voxel_length/2, attribute_buffer)
    # pg.generate_internal_particle()

