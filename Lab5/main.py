import matplotlib.pyplot as plt

INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8

xmin = float(input("Enter xmin: "))
ymin = float(input("Enter ymin: "))
xmax = float(input("Enter xmax: "))
ymax = float(input("Enter ymax: "))

x1 = float(input("Enter x1: "))
y1 = float(input("Enter y1: "))
x2 = float(input("Enter x2: "))
y2 = float(input("Enter y2: "))


def get_code(x, y):
    code = INSIDE

    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT

    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP

    return code


def cohen_sutherland(x1, y1, x2, y2):
    code1 = get_code(x1, y1)
    code2 = get_code(x2, y2)

    while True:

        if (code1 | code2) == 0:
            return True, x1, y1, x2, y2

        if (code1 & code2) != 0:
            return False, None, None, None, None

        if code1 != 0:
            code_out = code1
        else:
            code_out = code2

        if code_out & TOP:
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y = ymax

        elif code_out & BOTTOM:
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y = ymin

        elif code_out & RIGHT:
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x = xmax

        else:
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x = xmin

        if code_out == code1:
            x1 = x
            y1 = y
            code1 = get_code(x1, y1)
        else:
            x2 = x
            y2 = y
            code2 = get_code(x2, y2)


code1 = get_code(x1, y1)
code2 = get_code(x2, y2)

print("\nRegion Code of P1:", code1)
print("Region Code of P2:", code2)

accepted, cx1, cy1, cx2, cy2 = cohen_sutherland(x1, y1, x2, y2)

if accepted:
    print("\nLine accepted/clipped")
    print("Clipped P1:", (cx1, cy1))
    print("Clipped P2:", (cx2, cy2))
else:
    print("\nLine rejected")


plt.figure(figsize=(8, 6))

plt.plot(
    [xmin, xmax, xmax, xmin, xmin],
    [ymin, ymin, ymax, ymax, ymin],
    'b-',
    label="Clipping Window"
)

plt.plot(
    [x1, x2],
    [y1, y2],
    'r--',
    label="Original Line"
)

if accepted:
    plt.plot(
        [cx1, cx2],
        [cy1, cy2],
        'g-',
        linewidth=3,
        label="Clipped Line"
    )

plt.xlabel("X")
plt.ylabel("Y")
plt.title("Cohen-Sutherland Line Clipping")
plt.legend()
plt.grid(True)
plt.axis("equal")
plt.show()