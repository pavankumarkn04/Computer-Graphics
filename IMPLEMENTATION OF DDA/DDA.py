import tkinter as tk


WIDTH = 1000
HEIGHT = 800
SCALE = 30
ORIGIN_X = WIDTH // 2
ORIGIN_Y = HEIGHT // 2


def graph_x(x):
    return ORIGIN_X + x * SCALE


def graph_y(y):
    return ORIGIN_Y - y * SCALE


def draw_graph(canvas):
    # Draw grid
    for x in range(-ORIGIN_X, WIDTH - ORIGIN_X, SCALE):
        canvas.create_line(
            ORIGIN_X + x, 0, ORIGIN_X + x, HEIGHT, fill="#e0e0e0", width=1
        )

    for y in range(-ORIGIN_Y, HEIGHT - ORIGIN_Y, SCALE):
        canvas.create_line(
            0, ORIGIN_Y + y, WIDTH, ORIGIN_Y + y, fill="#e0e0e0", width=1
        )

    # Draw axes
    canvas.create_line(0, ORIGIN_Y, WIDTH, ORIGIN_Y, fill="black", width=2)
    canvas.create_line(ORIGIN_X, 0, ORIGIN_X, HEIGHT, fill="black", width=2)

    # Draw axis labels
    canvas.create_text(WIDTH - 20, ORIGIN_Y - 15, text="X", fill="black", font=("Arial", 12, "bold"))
    canvas.create_text(ORIGIN_X + 15, 15, text="Y", fill="black", font=("Arial", 12, "bold"))

    # Draw tick marks and numbers
    for i in range(-15, 16):
        if i == 0:
            continue
        x_pos = graph_x(i)
        y_pos = graph_y(i)
        
        # X-axis ticks
        canvas.create_line(x_pos, ORIGIN_Y - 3, x_pos, ORIGIN_Y + 3, fill="black")
        if i % 2 == 0:
            canvas.create_text(x_pos, ORIGIN_Y + 15, text=str(i), fill="black", font=("Arial", 8))
        
        # Y-axis ticks
        canvas.create_line(ORIGIN_X - 3, y_pos, ORIGIN_X + 3, y_pos, fill="black")
        if i % 2 == 0:
            canvas.create_text(ORIGIN_X - 20, y_pos, text=str(i), fill="black", font=("Arial", 8))


def plot_point(canvas, x, y, color="red", size=4, show_label=False):
    screen_x = graph_x(x)
    screen_y = graph_y(y)
    canvas.create_oval(
        screen_x - size,
        screen_y - size,
        screen_x + size,
        screen_y + size,
        fill=color,
        outline=color,
    )
    # Add coordinate label on the point
    if show_label:
        canvas.create_text(
            screen_x + 10,
            screen_y - 12,
            text=f"({x}, {y})",
            fill=color,
            font=("Arial", 9, "bold"),
            anchor="w"
        )


def dda_line(canvas, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1

    steps = int(max(abs(dx), abs(dy)))

    if steps == 0:
        plot_point(canvas, x1, y1, "red", 8, show_label=True)
        print(f"Point: ({x1}, {y1})")
        return

    x_increment = dx / steps
    y_increment = dy / steps

    x = float(x1)
    y = float(y1)

    points = []
    print("\nDDA Line Points:")
    print("-" * 40)

    for i in range(steps + 1):
        px = round(x)
        py = round(y)
        points.append((px, py))
        print(f"Step {i}: ({px}, {py})")
        x += x_increment
        y += y_increment

    # Draw line connecting all points FIRST (so it's behind the points)
    if len(points) > 1:
        for i in range(len(points) - 1):
            x1_screen = graph_x(points[i][0])
            y1_screen = graph_y(points[i][1])
            x2_screen = graph_x(points[i + 1][0])
            y2_screen = graph_y(points[i + 1][1])
            canvas.create_line(
                x1_screen, y1_screen, x2_screen, y2_screen, fill="red", width=3
            )

    # Plot points on top of the line
    for px, py in points:
        plot_point(canvas, px, py, "blue", 6, show_label=True)

    # Mark start and end points with larger markers
    plot_point(canvas, points[0][0], points[0][1], "darkgreen", 8, show_label=False)
    plot_point(canvas, points[-1][0], points[-1][1], "darkred", 8, show_label=False)

    print("-" * 40)
    print(f"Total points: {len(points)}")
    print(f"Start point: ({points[0][0]}, {points[0][1]}) - GREEN")
    print(f"End point: ({points[-1][0]}, {points[-1][1]}) - RED")


print("=" * 50)
print("DDA LINE DRAWING ALGORITHM")
print("=" * 50)
x1 = int(input("\nEnter x1: "))
y1 = int(input("Enter y1: "))
x2 = int(input("Enter x2: "))
y2 = int(input("Enter y2: "))

window = tk.Tk()
window.title("DDA Line Drawing Algorithm - Visualization")
window.geometry(f"{WIDTH}x{HEIGHT+50}")

canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="white", highlightthickness=1, highlightbackground="gray")
canvas.pack(pady=10)

draw_graph(canvas)
dda_line(canvas, x1, y1, x2, y2)

window.mainloop()