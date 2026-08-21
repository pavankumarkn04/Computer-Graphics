"""Experiment 3: 2-D transformations using homogeneous coordinates.

Requirements: pip install PyOpenGL PyOpenGL_accelerate
Blue shows the original object; orange shows the transformed object.
On startup, enter the polygon coordinates, then choose a transformation.
Keys: I = choose a new transformation, R = reset, Esc = quit.
"""

from math import ceil, cos, floor, log10, radians, sin

from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT, GL_LINES, GL_LINE_LOOP, GL_LINE_STRIP, GL_MODELVIEW, GL_POINTS, GL_QUADS,
    GL_PROJECTION, glBegin, glClear, glClearColor, glColor3f, glEnd,
    glLineWidth, glLoadIdentity, glMatrixMode, glOrtho, glPointSize,
    glRasterPos2f, glVertex2f, glViewport,
)
from OpenGL.GLUT import (
    GLUT_BITMAP_HELVETICA_18, GLUT_DOUBLE, GLUT_RGB, glutBitmapCharacter,
    glutCreateWindow, glutDisplayFunc, glutInit, glutInitDisplayMode,
    glutInitWindowSize, glutKeyboardFunc, glutMainLoop, glutPostRedisplay,
    glutReshapeFunc, glutSetWindowTitle, glutSwapBuffers, glutTimerFunc,
)

# Default object is used only if the program is extended without input dialogs.
OBJECT = [(-0.8, -0.7, 1), (0.8, -0.7, 1), (0.8, -0.2, 1),
          (-0.15, -0.2, 1), (-0.15, 0.75, 1), (-0.8, 0.75, 1)]
IDENTITY = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

active_name = "No transformation"
active_matrix = IDENTITY
display_matrix = IDENTITY
animation_step = 0
ANIMATION_FRAMES = 75
active_operation = ""
active_values = []
view_left, view_right, view_bottom, view_top = -2.0, 2.0, -2.0, 2.0
window_width, window_height = 800, 700
# In-window input state.  No separate Tkinter dialog windows are used.
input_stage = "vertex_count"
input_buffer = ""
input_vertices = []
input_vertex_count = 0
input_vertex_index = 0
input_coordinate = "x"
selected_operation = ""
parameter_values = []
input_error = ""


def matrix_vector_multiply(matrix, vector):
    return tuple(sum(matrix[row][col] * vector[col] for col in range(3)) for row in range(3))


def transform(points, matrix):
    result = []
    for point in points:
        x, y, w = matrix_vector_multiply(matrix, point)
        result.append((x / w, y / w))
    return result


def current_prompt():
    if input_stage == "vertex_count":
        return "Enter number of vertices"
    if input_stage == "coordinate":
        return f"Vertex {input_vertex_index + 1}: enter {input_coordinate}-coordinate"
    if input_stage == "operation":
        return "Choose operation:  1 Translation   2 Rotation   3 Scaling"
    if input_stage == "parameter":
        prompts = {
            "1": ("Enter translation along X (tx)", "Enter translation along Y (ty)"),
            "2": ("Enter rotation angle in degrees",),
            "3": ("Enter scale factor along X (sx)", "Enter scale factor along Y (sy)"),
            "4": ("Enter reflection axis: X or Y",),
            "5": ("Enter shear direction: X or Y", "Enter shearing factor"),
        }
        return prompts[selected_operation][len(parameter_values)]
    return ""


def draw_input_panel():
    """A compact form in the same window, with the graph visible behind it."""
    width, height = view_right - view_left, view_top - view_bottom
    left, right = view_left + 0.06 * width, view_left + 0.67 * width
    top, bottom = view_top - 0.10 * height, view_bottom + 0.22 * height

    # Form card and its blue entry box.
    glColor3f(0.10, 0.11, 0.17)
    glBegin(GL_QUADS)
    glVertex2f(left, bottom); glVertex2f(right, bottom)
    glVertex2f(right, top); glVertex2f(left, top)
    glEnd()
    box_top, box_bottom = top - 0.39 * height, top - 0.51 * height
    glColor3f(0.06, 0.20, 0.29)
    glBegin(GL_QUADS)
    glVertex2f(left + 0.04 * width, box_bottom); glVertex2f(right - 0.04 * width, box_bottom)
    glVertex2f(right - 0.04 * width, box_top); glVertex2f(left + 0.04 * width, box_top)
    glEnd()

    text_left = left + 0.045 * width
    draw_text(text_left, top - 0.10 * height, "2-D TRANSFORMATION", (1.0, 0.82, 0.25))
    draw_text(text_left, top - 0.24 * height, current_prompt(), (0.94, 0.94, 0.97))
    if input_stage == "operation":
        draw_text(text_left, top - 0.32 * height, "4 Reflection   5 Shearing", (0.94, 0.94, 0.97))
    draw_text(text_left, top - 0.47 * height, input_buffer + "|", (0.30, 0.85, 1.0))
    draw_text(text_left, bottom + 0.12 * height, "Enter = continue    Backspace = edit    Esc = exit", (0.72, 0.72, 0.78))
    if input_error:
        draw_text(text_left, bottom + 0.23 * height, input_error, (1.0, 0.35, 0.25))


def start_operation_input():
    global input_stage, input_buffer, selected_operation, parameter_values, input_error
    input_stage, input_buffer, selected_operation, parameter_values, input_error = "operation", "", "", [], ""


def finish_transformation():
    global active_name, active_matrix, display_matrix, animation_step, input_stage, active_operation, active_values
    values = parameter_values
    active_operation, active_values = selected_operation, list(values)
    if selected_operation == "1":
        tx, ty = values
        active_name, active_matrix = f"Translation: tx={tx:g}, ty={ty:g}", [[1, 0, tx], [0, 1, ty], [0, 0, 1]]
    elif selected_operation == "2":
        angle = values[0]; theta = radians(angle)
        active_name, active_matrix = f"Rotation: {angle:g} degrees", [[cos(theta), -sin(theta), 0], [sin(theta), cos(theta), 0], [0, 0, 1]]
    elif selected_operation == "3":
        sx, sy = values
        active_name, active_matrix = f"Scaling: sx={sx:g}, sy={sy:g}", [[sx, 0, 0], [0, sy, 0], [0, 0, 1]]
    elif selected_operation == "4":
        axis = values[0]
        active_name, active_matrix = ("Reflection about X-axis", [[1, 0, 0], [0, -1, 0], [0, 0, 1]]) if axis == "x" else ("Reflection about Y-axis", [[-1, 0, 0], [0, 1, 0], [0, 0, 1]])
    else:
        direction, factor = values
        active_name, active_matrix = (f"X-shear: shx={factor:g}", [[1, factor, 0], [0, 1, 0], [0, 0, 1]]) if direction == "x" else (f"Y-shear: shy={factor:g}", [[1, 0, 0], [factor, 1, 0], [0, 0, 1]])
    input_stage, display_matrix, animation_step = "ready", IDENTITY, 0
    update_view(); set_projection(); glutTimerFunc(16, animate, 0)
    glutSetWindowTitle(f"2-D Transformations - {active_name}".encode())


def submit_input():
    global OBJECT, input_stage, input_buffer, input_vertices, input_vertex_count, input_vertex_index, input_coordinate
    global selected_operation, parameter_values, input_error
    value = input_buffer.strip()
    input_error = ""
    try:
        if input_stage == "vertex_count":
            count = int(value)
            if count < 2 or str(count) != value:
                raise ValueError
            input_vertex_count, input_vertices, input_vertex_index, input_coordinate = count, [], 0, "x"
            input_stage = "coordinate"
        elif input_stage == "coordinate":
            number = float(value)
            if input_coordinate == "x":
                input_vertices.append([number])
                input_coordinate = "y"
            else:
                input_vertices[-1].append(number)
                input_vertex_index += 1
                input_coordinate = "x"
                if input_vertex_index == input_vertex_count:
                    OBJECT = [(x, y, 1) for x, y in input_vertices]
                    start_operation_input()
        elif input_stage == "operation":
            if value not in ("1", "2", "3", "4", "5"):
                raise ValueError
            selected_operation, parameter_values, input_stage = value, [], "parameter"
        elif input_stage == "parameter":
            if selected_operation in ("4", "5") and len(parameter_values) == 0:
                if value.lower() not in ("x", "y"):
                    raise ValueError
                parameter_values.append(value.lower())
            else:
                parameter_values.append(float(value))
            required = {"1": 2, "2": 1, "3": 2, "4": 1, "5": 2}[selected_operation]
            if len(parameter_values) == required:
                finish_transformation()
    except ValueError:
        input_error = "Please enter a valid value for this field."
        glutPostRedisplay()
        return
    input_buffer = ""
    glutPostRedisplay()


def update_view():
    """Automatically zoom to show all points, even for large input values."""
    global view_left, view_right, view_bottom, view_top
    points = [(x, y) for x, y, _ in OBJECT] + transform(OBJECT, active_matrix)
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    width, height = max(max(xs) - min(xs), 1.0), max(max(ys) - min(ys), 1.0)
    # Extra room keeps the vertex-coordinate labels inside the graph.
    padding = 0.48 * max(width, height)
    view_left, view_right = min(xs) - padding, max(xs) + padding
    view_bottom, view_top = min(ys) - padding, max(ys) + padding


def draw_axes():
    """Draw a light grid, axes, and legible numeric tick labels."""
    span = max(view_right - view_left, view_top - view_bottom)
    # A 1/2/5 step gives roughly 5--9 labelled divisions at every zoom level.
    base = 10 ** floor(log10(max(span / 7, 0.001)))
    step = next(multiplier * base for multiplier in (1, 2, 5, 10)
                if span / (multiplier * base) <= 9)

    glColor3f(0.16, 0.16, 0.22)
    glLineWidth(1)
    glBegin(GL_LINES)
    x = floor(view_left / step) * step
    while x <= view_right + step * 0.01:
        glVertex2f(x, view_bottom); glVertex2f(x, view_top)
        x += step
    y = floor(view_bottom / step) * step
    while y <= view_top + step * 0.01:
        glVertex2f(view_left, y); glVertex2f(view_right, y)
        y += step
    glEnd()

    glColor3f(0.5, 0.5, 0.55)
    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex2f(view_left, 0); glVertex2f(view_right, 0)
    glVertex2f(0, view_bottom); glVertex2f(0, view_top)
    glEnd()

    label_offset = 0.035 * (view_top - view_bottom)
    x = ceil(view_left / step) * step
    while x <= view_right:
        if abs(x) > step * 0.001:
            draw_text(x, min(max(0, view_bottom + label_offset), view_top - label_offset), f"{x:g}", (0.65, 0.65, 0.72))
        x += step
    y = ceil(view_bottom / step) * step
    while y <= view_top:
        if abs(y) > step * 0.001:
            draw_text(min(max(0, view_left + label_offset), view_right - label_offset), y, f"{y:g}", (0.65, 0.65, 0.72))
        y += step


def draw_polygon(points, color):
    glColor3f(*color)
    glLineWidth(3)
    # Two entered vertices represent a line segment; three or more form a closed polygon.
    glBegin(GL_LINE_STRIP if len(points) == 2 else GL_LINE_LOOP)
    for x, y in points:
        glVertex2f(x, y)
    glEnd()
    glPointSize(8)
    glBegin(GL_POINTS)
    for x, y in points:
        glVertex2f(x, y)
    glEnd()


def draw_text(x, y, value, color=(0.95, 0.95, 0.95)):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for character in value:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))


def draw_point_coordinates(points, color, y_direction=1):
    """Label each vertex using a scale-aware offset so labels stay readable."""
    dx = 0.025 * (view_right - view_left)
    dy = y_direction * 0.035 * (view_top - view_bottom)
    for x, y in points:
        draw_text(x + dx, y + dy, f"({x:.2g}, {y:.2g})", color)


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    if input_stage != "ready":
        draw_axes()
        draw_input_panel()
        glutSwapBuffers()
        return
    draw_axes()
    transformed = transform(OBJECT, display_matrix)
    original = [(x, y) for x, y, _ in OBJECT]
    draw_polygon(transformed, (1.0, 0.35, 0.05))
    draw_polygon(original, (0.15, 0.7, 1.0))
    draw_point_coordinates(original, (0.25, 0.78, 1.0), 1)
    # Avoid jittering labels while the orange shape is moving.
    if animation_step >= ANIMATION_FRAMES:
        draw_point_coordinates(transformed, (1.0, 0.55, 0.25), -1)
    draw_text(view_left + 0.03 * (view_right - view_left), view_top - 0.07 * (view_top - view_bottom), active_name)
    draw_text(view_left + 0.03 * (view_right - view_left), view_top - 0.12 * (view_top - view_bottom), "Blue: original   Orange: transformed   I: new transformation   R: reset", (0.75, 0.75, 0.8))
    glutSwapBuffers()


def animated_matrix(progress):
    """Interpolate transformation parameters, so rotations stay true rotations."""
    eased = progress * progress * (3 - 2 * progress)  # smooth start and finish
    if active_operation == "1":
        tx, ty = active_values
        return [[1, 0, tx * eased], [0, 1, ty * eased], [0, 0, 1]]
    if active_operation == "2":
        theta = radians(active_values[0] * eased)
        return [[cos(theta), -sin(theta), 0], [sin(theta), cos(theta), 0], [0, 0, 1]]
    if active_operation == "3":
        sx, sy = active_values
        return [[1 + (sx - 1) * eased, 0, 0], [0, 1 + (sy - 1) * eased, 0], [0, 0, 1]]
    if active_operation == "4":
        axis = active_values[0]
        return [[1, 0, 0], [0, 1 - 2 * eased, 0], [0, 0, 1]] if axis == "x" else [[1 - 2 * eased, 0, 0], [0, 1, 0], [0, 0, 1]]
    if active_operation == "5":
        direction, factor = active_values
        return [[1, factor * eased, 0], [0, 1, 0], [0, 0, 1]] if direction == "x" else [[1, 0, 0], [factor * eased, 1, 0], [0, 0, 1]]
    return IDENTITY


def animate(_value):
    global animation_step, display_matrix
    animation_step += 1
    display_matrix = animated_matrix(min(animation_step / ANIMATION_FRAMES, 1.0))
    glutPostRedisplay()
    if animation_step < ANIMATION_FRAMES:
        glutTimerFunc(16, animate, 0)


def set_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    world_width, world_height = view_right - view_left, view_top - view_bottom
    world_aspect, screen_aspect = world_width / world_height, window_width / window_height
    if screen_aspect > world_aspect:
        extra = (world_height * screen_aspect - world_width) / 2
        glOrtho(view_left - extra, view_right + extra, view_bottom, view_top, -1, 1)
    else:
        extra = (world_width / screen_aspect - world_height) / 2
        glOrtho(view_left, view_right, view_bottom - extra, view_top + extra, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def reshape(width, height):
    global window_width, window_height
    window_width, window_height = max(width, 1), max(height, 1)
    glViewport(0, 0, window_width, window_height)
    set_projection()


def keyboard(key, _x, _y):
    global active_name, active_matrix, display_matrix, animation_step, input_buffer
    if key == b"\x1b":
        raise SystemExit
    if input_stage != "ready":
        if key in (b"\r", b"\n"):
            submit_input()
        elif key == b"\x08":
            input_buffer = input_buffer[:-1]
            glutPostRedisplay()
        elif len(key) == 1 and key.decode("latin1").isprintable():
            input_buffer += key.decode("latin1")
            glutPostRedisplay()
        return
    if key in (b"i", b"I"):
        start_operation_input(); glutPostRedisplay()
    elif key in (b"r", b"R"):
        active_name, active_matrix = "No transformation", IDENTITY
        display_matrix, animation_step = IDENTITY, ANIMATION_FRAMES
        update_view(); set_projection(); glutPostRedisplay()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Experiment 3 - 2-D Transformations")
    glClearColor(0.07, 0.07, 0.11, 1.0)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    set_projection()
    glutMainLoop()


if __name__ == "__main__":
    main()
