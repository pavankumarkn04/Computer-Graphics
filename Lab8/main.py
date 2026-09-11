import glfw
from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np
import ctypes
import math


# ============================================================
# VERTEX SHADER
# ============================================================

VERTEX_SHADER = """
#version 330 core

layout (location = 0) in vec2 aPos;
layout (location = 1) in vec3 aColor;

out vec3 vertexColor;

uniform mat3 transform;

void main()
{
    // Convert 2D coordinate to homogeneous coordinate
    vec3 position = vec3(aPos, 1.0);

    // Apply 3x3 transformation matrix
    vec3 result = transform * position;

    gl_Position = vec4(result.xy, 0.0, 1.0);

    vertexColor = aColor;
}
"""


# ============================================================
# FRAGMENT SHADER
# ============================================================

FRAGMENT_SHADER = """
#version 330 core

in vec3 vertexColor;

out vec4 FragColor;

void main()
{
    FragColor = vec4(vertexColor, 1.0);
}
"""


# ============================================================
# 2D TRANSFORMATION MATRICES
# ============================================================

def identity():
    return np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ], dtype=np.float32)


def translation(tx, ty):
    return np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ], dtype=np.float32)


def rotation(angle):
    theta = math.radians(angle)

    c = math.cos(theta)
    s = math.sin(theta)

    return np.array([
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ], dtype=np.float32)


def scaling(sx, sy):
    return np.array([
        [sx, 0,  0],
        [0,  sy, 0],
        [0,  0,  1]
    ], dtype=np.float32)


def shear_x(value):
    return np.array([
        [1, value, 0],
        [0, 1,     0],
        [0, 0,     1]
    ], dtype=np.float32)


def shear_y(value):
    return np.array([
        [1,     0, 0],
        [value, 1, 0],
        [0,     0, 1]
    ], dtype=np.float32)


def reflection_x():
    return np.array([
        [1,  0, 0],
        [0, -1, 0],
        [0,  0, 1]
    ], dtype=np.float32)


def reflection_y():
    return np.array([
        [-1, 0, 0],
        [0,  1, 0],
        [0,  0, 1]
    ], dtype=np.float32)


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # INITIALIZE GLFW
    # --------------------------------------------------------

    if not glfw.init():
        raise Exception("GLFW initialization failed")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(
        glfw.OPENGL_PROFILE,
        glfw.OPENGL_CORE_PROFILE
    )

    # --------------------------------------------------------
    # CREATE WINDOW
    # --------------------------------------------------------

    window = glfw.create_window(
        900,
        700,
        "EX-8: Interactive 2D Transformations",
        None,
        None
    )

    if not window:
        glfw.terminate()
        raise Exception("Window creation failed")

    glfw.make_context_current(window)

    # --------------------------------------------------------
    # VIEWPORT
    # --------------------------------------------------------

    def resize(window, width, height):
        if height == 0:
            height = 1

        glViewport(0, 0, width, height)

    glfw.set_framebuffer_size_callback(window, resize)

    width, height = glfw.get_framebuffer_size(window)
    glViewport(0, 0, width, height)

    # --------------------------------------------------------
    # COMPILE SHADERS
    # --------------------------------------------------------

    try:

        vertex_shader = shaders.compileShader(
            VERTEX_SHADER,
            GL_VERTEX_SHADER
        )

        fragment_shader = shaders.compileShader(
            FRAGMENT_SHADER,
            GL_FRAGMENT_SHADER
        )

        program = shaders.compileProgram(
            vertex_shader,
            fragment_shader
        )

    except Exception as e:

        glfw.terminate()
        raise Exception("Shader error:\n" + str(e))

    # ========================================================
    # TRIANGLE
    # ========================================================

    vertices = np.array([

        # X       Y       R      G      B

        -0.35,   -0.30,   1.0,   0.0,   0.0,

         0.35,   -0.30,   0.0,   1.0,   0.0,

         0.00,    0.40,   0.0,   0.2,   1.0

    ], dtype=np.float32)

    # ========================================================
    # VAO + VBO
    # ========================================================

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    glBufferData(
        GL_ARRAY_BUFFER,
        vertices.nbytes,
        vertices,
        GL_STATIC_DRAW
    )

    # Position
    glVertexAttribPointer(
        0,
        2,
        GL_FLOAT,
        GL_FALSE,
        5 * vertices.itemsize,
        ctypes.c_void_p(0)
    )

    glEnableVertexAttribArray(0)

    # Color
    glVertexAttribPointer(
        1,
        3,
        GL_FLOAT,
        GL_FALSE,
        5 * vertices.itemsize,
        ctypes.c_void_p(
            2 * vertices.itemsize
        )
    )

    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    # ========================================================
    # TRANSFORMATION UNIFORM
    # ========================================================

    transform_location = glGetUniformLocation(
        program,
        "transform"
    )

    # ========================================================
    # TRANSFORMATION VARIABLES
    # ========================================================

    angle = 0.0

    rotation_speed = 90.0

    pos_x = 0.0
    pos_y = 0.0

    scale_value = 1.0

    shear_value = 0.0

    auto_rotate = True

    # ========================================================
    # KEY STATES
    # ========================================================

    previous_space = False
    previous_r = False
    previous_c = False
    previous_1 = False
    previous_2 = False
    previous_0 = False

    # ========================================================
    # PRINT CONTROLS
    # ========================================================

    print()
    print("=" * 60)
    print("          EXPERIMENT - 8")
    print("   VERTEX & FRAGMENT SHADERS")
    print("   INTERACTIVE 2D TRANSFORMATIONS")
    print("=" * 60)

    print()
    print("ROTATION")
    print("R       : Start automatic rotation")
    print("SPACE   : Pause / Resume")
    print("Q       : Rotate counter-clockwise")
    print("E       : Rotate clockwise")

    print()
    print("TRANSLATION")
    print("LEFT    : Move left")
    print("RIGHT   : Move right")
    print("UP      : Move up")
    print("DOWN    : Move down")

    print()
    print("SCALING")
    print("+       : Increase size")
    print("-       : Decrease size")

    print()
    print("SHEARING")
    print("X       : X-axis shear")
    print("Y       : Y-axis shear")

    print()
    print("REFLECTION")
    print("1       : Reflection about X-axis")
    print("2       : Reflection about Y-axis")

    print()
    print("OTHER")
    print("C       : Combined transformation")
    print("0       : Reset")
    print("ESC     : Exit")

    print("=" * 60)

    # ========================================================
    # TIME
    # ========================================================

    previous_time = glfw.get_time()

    # ========================================================
    # RENDER LOOP
    # ========================================================

    while not glfw.window_should_close(window):

        current_time = glfw.get_time()

        delta_time = current_time - previous_time

        previous_time = current_time

        if delta_time > 0.1:
            delta_time = 0.1

        # ====================================================
        # ESC
        # ====================================================

        if glfw.get_key(
            window,
            glfw.KEY_ESCAPE
        ) == glfw.PRESS:

            glfw.set_window_should_close(
                window,
                True
            )

        # ====================================================
        # SPACE - PAUSE / RESUME
        # ====================================================

        space = (
            glfw.get_key(
                window,
                glfw.KEY_SPACE
            ) == glfw.PRESS
        )

        if space and not previous_space:

            auto_rotate = not auto_rotate

        previous_space = space

        # ====================================================
        # R - START ROTATION
        # ====================================================

        key_r = (
            glfw.get_key(
                window,
                glfw.KEY_R
            ) == glfw.PRESS
        )

        if key_r and not previous_r:

            auto_rotate = True

        previous_r = key_r

        # ====================================================
        # AUTOMATIC ROTATION
        # ====================================================

        if auto_rotate:

            angle += rotation_speed * delta_time

        # ====================================================
        # Q / E - MANUAL ROTATION
        # ====================================================

        if glfw.get_key(
            window,
            glfw.KEY_Q
        ) == glfw.PRESS:

            angle += 120 * delta_time

            auto_rotate = False

        if glfw.get_key(
            window,
            glfw.KEY_E
        ) == glfw.PRESS:

            angle -= 120 * delta_time

            auto_rotate = False

        # ====================================================
        # TRANSLATION
        # ====================================================

        movement = 0.8 * delta_time

        if glfw.get_key(
            window,
            glfw.KEY_LEFT
        ) == glfw.PRESS:

            pos_x -= movement

        if glfw.get_key(
            window,
            glfw.KEY_RIGHT
        ) == glfw.PRESS:

            pos_x += movement

        if glfw.get_key(
            window,
            glfw.KEY_UP
        ) == glfw.PRESS:

            pos_y += movement

        if glfw.get_key(
            window,
            glfw.KEY_DOWN
        ) == glfw.PRESS:

            pos_y -= movement

        # ====================================================
        # SCALING
        # ====================================================

        if glfw.get_key(
            window,
            glfw.KEY_EQUAL
        ) == glfw.PRESS:

            scale_value += 0.5 * delta_time

        if glfw.get_key(
            window,
            glfw.KEY_MINUS
        ) == glfw.PRESS:

            scale_value -= 0.5 * delta_time

        # Limit scale
        scale_value = max(
            0.3,
            min(scale_value, 2.0)
        )

        # ====================================================
        # X SHEAR
        # ====================================================

        if glfw.get_key(
            window,
            glfw.KEY_X
        ) == glfw.PRESS:

            shear_value += 0.8 * delta_time

            if shear_value > 0.8:
                shear_value = 0.8

            auto_rotate = False

        # ====================================================
        # Y SHEAR
        # ====================================================

        if glfw.get_key(
            window,
            glfw.KEY_Y
        ) == glfw.PRESS:

            shear_value -= 0.8 * delta_time

            if shear_value < -0.8:
                shear_value = -0.8

            auto_rotate = False

        # ====================================================
        # REFLECTION X
        # ====================================================

        key_1 = (
            glfw.get_key(
                window,
                glfw.KEY_1
            ) == glfw.PRESS
        )

        if key_1 and not previous_1:

            # Reflect Y coordinate
            pos_y = -pos_y

            print("\nReflection about X-axis")

        previous_1 = key_1

        # ====================================================
        # REFLECTION Y
        # ====================================================

        key_2 = (
            glfw.get_key(
                window,
                glfw.KEY_2
            ) == glfw.PRESS
        )

        if key_2 and not previous_2:

            # Reflect X coordinate
            pos_x = -pos_x

            print("\nReflection about Y-axis")

        previous_2 = key_2

        # ====================================================
        # COMBINED TRANSFORMATION
        # ====================================================

        key_c = (
            glfw.get_key(
                window,
                glfw.KEY_C
            ) == glfw.PRESS
        )

        if key_c and not previous_c:

            # Combined transformation:
            #
            # Translation × Rotation × Scaling

            T = translation(
                0.25,
                0.10
            )

            R = rotation(
                30
            )

            S = scaling(
                1.25,
                1.25
            )

            transformation = T @ R @ S

            glClearColor(
                0.05,
                0.05,
                0.08,
                1.0
            )

            glClear(GL_COLOR_BUFFER_BIT)

            glUseProgram(program)

            glUniformMatrix3fv(
                transform_location,
                1,
                GL_TRUE,
                transformation
            )

            glBindVertexArray(VAO)

            glDrawArrays(
                GL_TRIANGLES,
                0,
                3
            )

            glfw.swap_buffers(window)
            glfw.poll_events()

        previous_c = key_c

        # ====================================================
        # RESET
        # ====================================================

        key_0 = (
            glfw.get_key(
                window,
                glfw.KEY_0
            ) == glfw.PRESS
        )

        if key_0 and not previous_0:

            angle = 0.0
            pos_x = 0.0
            pos_y = 0.0
            scale_value = 1.0
            shear_value = 0.0

            auto_rotate = True

            print("\nReset all transformations.")

        previous_0 = key_0

        # ====================================================
        # CREATE TRANSFORMATION MATRIX
        # ====================================================

        T = translation(
            pos_x,
            pos_y
        )

        R = rotation(
            angle
        )

        S = scaling(
            scale_value,
            scale_value
        )

        H = shear_x(
            shear_value
        )

        # ====================================================
        # FINAL TRANSFORMATION
        # ====================================================
        #
        # P' = T × R × H × S × P
        #
        # Scaling
        #     ↓
        # Shearing
        #     ↓
        # Rotation
        #     ↓
        # Translation
        #
        # ====================================================

        transformation = (
            T @ R @ H @ S
        )

        # ====================================================
        # UPDATE WINDOW TITLE
        # ====================================================

        status = "ROTATING" if auto_rotate else "PAUSED"

        glfw.set_window_title(
            window,
            f"EX-8 | {status} | "
            f"Angle: {angle % 360:.1f}° | "
            f"Scale: {scale_value:.2f}"
        )

        # ====================================================
        # CLEAR SCREEN
        # ====================================================

        glClearColor(
            0.04,
            0.04,
            0.07,
            1.0
        )

        glClear(
            GL_COLOR_BUFFER_BIT
        )

        # ====================================================
        # USE SHADER
        # ====================================================

        glUseProgram(program)

        # ====================================================
        # SEND MATRIX TO VERTEX SHADER
        # ====================================================

        glUniformMatrix3fv(
            transform_location,
            1,
            GL_TRUE,
            transformation
        )

        # ====================================================
        # DRAW TRIANGLE
        # ====================================================

        glBindVertexArray(VAO)

        glDrawArrays(
            GL_TRIANGLES,
            0,
            3
        )

        glBindVertexArray(0)

        # ====================================================
        # DISPLAY
        # ====================================================

        glfw.swap_buffers(window)

        glfw.poll_events()

    # ========================================================
    # CLEANUP
    # ========================================================

    glDeleteVertexArrays(
        1,
        [VAO]
    )

    glDeleteBuffers(
        1,
        [VBO]
    )

    glDeleteProgram(
        program
    )

    glfw.terminate()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()