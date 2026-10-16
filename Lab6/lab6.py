"""Experiment 6: Interactive Z-buffer hidden-surface removal demo.
Controls: arrow keys orbit, +/- zoom, Z toggle depth testing, P toggle panel, Esc quit.
Run with: python lab6.py
"""

import math
import tkinter as tk

BG = "#000000"
CYAN = "#54d9e8"
WHITE = "#dddddd"
YELLOW = "#ffe735"

# (name, RGB color, center x/y/z). Red is nearest; purple is farthest.
QUADS = [
    ("Red", "#ff303e", (-0.15, 0.18, 0.00)),
    ("Blue", "#3388ff", (0.22, -0.08, -0.35)),
    ("Green", "#00e84f", (-0.08, -0.25, -0.70)),
    ("Yellow", "#ffe000", (0.20, 0.13, -1.05)),
    ("Purple", "#d52dff", (-0.10, 0.00, -1.40)),
]


def edge(a, b, x, y):
    return (x - a[0]) * (b[1] - a[1]) - (y - a[1]) * (b[0] - a[0])


def transformed_quads(angle_x, angle_y, zoom, width, height):
    """Rotate and project the five 3D quads into the viewing window."""
    rx, ry = math.radians(angle_x), math.radians(angle_y)
    sx, cx = math.sin(rx), math.cos(rx)
    sy, cy = math.sin(ry), math.cos(ry)
    quads = []
    for name, color, center in QUADS:
        verts = []
        for lx, ly in ((-1.05, -1.30), (1.05, -1.30), (1.05, 1.30), (-1.05, 1.30)):
            x, y, z = lx + center[0], ly + center[1], center[2]
            # Orbit around the X and Y axes.
            x1, y1, z1 = x, y * cx - z * sx, y * sx + z * cx
            x2, y2, z2 = x1 * cy + z1 * sy, y1, -x1 * sy + z1 * cy
            perspective = 2.8 / (2.8 + z2)
            px = width * 0.52 + x2 * 130 * zoom * perspective
            py = height * 0.53 + y2 * 130 * zoom * perspective
            verts.append((px, py, -z2))  # smaller depth is closer
        quads.append((name, color, verts))
    return quads


def render(width, height, angle_x, angle_y, zoom, z_enabled):
    colors = [[BG] * width for _ in range(height)]
    depths = [[float("inf")] * width for _ in range(height)]
    quads = transformed_quads(angle_x, angle_y, zoom, width, height)

    for _name, color, quad in quads:
        for indices in ((0, 1, 2), (0, 2, 3)):
            a, b, c = (quad[i] for i in indices)
            area = edge(a, b, c[0], c[1])
            if abs(area) < 1e-9:
                continue
            min_x = max(0, int(min(a[0], b[0], c[0])))
            max_x = min(width - 1, int(max(a[0], b[0], c[0])) + 1)
            min_y = max(0, int(min(a[1], b[1], c[1])))
            max_y = min(height - 1, int(max(a[1], b[1], c[1])) + 1)
            for py in range(min_y, max_y + 1):
                for px in range(min_x, max_x + 1):
                    x, y = px + 0.5, py + 0.5
                    wa = edge(b, c, x, y) / area
                    wb = edge(c, a, x, y) / area
                    wc = edge(a, b, x, y) / area
                    if wa >= 0 and wb >= 0 and wc >= 0:
                        z = wa * a[2] + wb * b[2] + wc * c[2]
                        if not z_enabled or z < depths[py][px]:
                            colors[py][px] = color
                            depths[py][px] = z
    return colors, quads


class ZBufferDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Z-Buffer Hidden Surface Removal")
        self.root.configure(bg=BG)
        self.root.geometry("1300x760")
        self.root.minsize(1050, 650)
        self.angle_x, self.angle_y, self.zoom = 8, -12, 1.0
        self.z_enabled = True
        self.panel_visible = True

        self.canvas = tk.Canvas(root, width=650, height=600, bg=BG, highlightthickness=0)
        self.canvas.pack(side="right", padx=(5, 25), pady=25)
        self.panel = tk.Frame(root, bg=BG)
        self.panel.pack(side="left", anchor="nw", padx=24, pady=15, fill="both", expand=True)

        self.title = tk.Label(self.panel, text="Z-Buffer Hidden Surface Removal", bg=BG,
                              fg=YELLOW, font=("Consolas", 23, "bold"), anchor="w")
        self.title.pack(anchor="w", pady=(0, 14))
        self.status = tk.Label(self.panel, bg=BG, font=("Consolas", 15), anchor="w")
        self.status.pack(anchor="w", pady=(0, 8))
        tk.Label(self.panel, text="Arrow keys: orbit   +/-: zoom   z: toggle Z-buffer\np: toggle panel   Esc: quit",
                 bg=BG, fg=WHITE, font=("Consolas", 13), justify="left", anchor="w").pack(anchor="w", pady=(0, 23))

        tk.Label(self.panel, text="Algorithm:", bg=BG, fg=CYAN, font=("Consolas", 14), anchor="w").pack(anchor="w")
        algorithm = (
            "  init depthBuffer[x][y] = INF\n"
            "  for each polygon:\n"
            "    for each fragment (x, y, z):\n"
            "      if z < depthBuffer[x][y]:\n"
            "        colorBuffer[x][y] = fragment.color\n"
            "        depthBuffer[x][y] = z"
        )
        tk.Label(self.panel, text=algorithm, bg=BG, fg=WHITE, font=("Consolas", 13),
                 justify="left", anchor="w").pack(anchor="w", pady=(7, 19))
        tk.Label(self.panel, text="Quads (front to back):", bg=BG, fg=CYAN,
                 font=("Consolas", 14), anchor="w").pack(anchor="w", pady=(0, 5))
        self.legend = tk.Frame(self.panel, bg=BG)
        self.legend.pack(anchor="w")
        for name, color, center in QUADS:
            tk.Label(self.legend, text=f"  {name:<7} z={center[2]:>5.1f}", bg=BG, fg=color,
                     font=("Consolas", 13), anchor="w").pack(anchor="w", pady=2)
        self.off_note = tk.Label(self.panel, text="Z-buffer OFF: last drawn surface wins.", bg=BG,
                                 fg="#ff9d32", font=("Consolas", 12), anchor="w")
        self.off_note.pack(anchor="w", pady=(10, 0))

        root.bind("<Left>", lambda e: self.change_orbit(dy=-6))
        root.bind("<Right>", lambda e: self.change_orbit(dy=6))
        root.bind("<Up>", lambda e: self.change_orbit(dx=-6))
        root.bind("<Down>", lambda e: self.change_orbit(dx=6))
        root.bind("z", lambda e: self.toggle_z())
        root.bind("Z", lambda e: self.toggle_z())
        root.bind("p", lambda e: self.toggle_panel())
        root.bind("P", lambda e: self.toggle_panel())
        root.bind("+", lambda e: self.change_zoom(0.1))
        root.bind("=", lambda e: self.change_zoom(0.1))
        root.bind("-", lambda e: self.change_zoom(-0.1))
        root.bind("<Escape>", lambda e: root.destroy())
        self.redraw()

    def change_orbit(self, dx=0, dy=0):
        self.angle_x += dx
        self.angle_y += dy
        self.redraw()

    def change_zoom(self, amount):
        self.zoom = max(0.55, min(1.5, self.zoom + amount))
        self.redraw()

    def toggle_z(self):
        self.z_enabled = not self.z_enabled
        self.redraw()

    def toggle_panel(self):
        self.panel_visible = not self.panel_visible
        (self.panel.pack if self.panel_visible else self.panel.pack_forget)()

    def redraw(self):
        self.status.configure(text=f"Z-Buffer: {'ENABLED' if self.z_enabled else 'DISABLED'} (press z to toggle)",
                              fg="#00ef75" if self.z_enabled else "#ff5363")
        self.off_note.configure(text="" if self.z_enabled else "Z-Buffer OFF: last drawn surface wins.")
        width, height = 650, 600
        pixels, quads = render(width, height, self.angle_x, self.angle_y, self.zoom, self.z_enabled)
        self.canvas.delete("all")
        for y, row in enumerate(pixels):
            x = 0
            while x < width:
                color = row[x]
                end = x + 1
                while end < width and row[end] == color:
                    end += 1
                if color != BG:
                    self.canvas.create_rectangle(x, y, end, y + 1, fill=color, outline=color)
                x = end


if __name__ == "__main__":
    app = tk.Tk()
    ZBufferDemo(app)
    app.mainloop()

