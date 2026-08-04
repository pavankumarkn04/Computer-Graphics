import glfw
from OpenGL.GL import *
import math


# Draw a line
def draw_line():
    glColor3f(1.0, 0.0, 0.0)  # Red

    glBegin(GL_LINES)
    glVertex2f(-0.8, 0.0)
    glVertex2f(0.8, 0.0)
    glEnd()


# Draw a circle
def draw_circle():
    glColor3f(0.0, 1.0, 0.0)  # Green

    radius = 0.4
    center_x = 0.0
    center_y = 0.0

    glBegin(GL_LINE_LOOP)

    for i in range(360):
        angle = math.radians(i)

        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)

        glVertex2f(x, y)

    glEnd()


# Initialize GLFW
if not glfw.init():
    raise Exception("GLFW could not be initialized")


# Create window
window = glfw.create_window(800, 600, "Line and Circle", None, None)

if not window:
    glfw.terminate()
    raise Exception("Window could not be created")


glfw.make_context_current(window)


# Main loop
while not glfw.window_should_close(window):

    glClear(GL_COLOR_BUFFER_BIT)

    # Draw both
    draw_line()
    draw_circle()

    glfw.swap_buffers(window)
    glfw.poll_events()


glfw.terminate()