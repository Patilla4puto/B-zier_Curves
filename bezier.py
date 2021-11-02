import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib.widgets import Slider, Button
import matplotlib

matplotlib.use('Qt5Agg')


t = .5

def drawPolygon(points, ax, showCircle=False, color="k"):
    path = Path(points, closed=False)
    patch = patches.PathPatch(path, facecolor='none', edgecolor=color, lw=2)
    ax.add_patch(patch)

    # patch.figure.canvas.draw()

    if showCircle:
        # Add green circles on controlpoints
        for p in points:
            ax.add_patch(plt.Circle(p, 0.05, color="green"))
    return patch


def b_curve(t, points):
    a = [points]
    for r in range(1, len(points)):
        lenght = (len(a[0]) - 1)
        a.insert(0, [0] * lenght)
        for j in range(lenght):
            a[0][j] = ((1 - t) * a[1][j] + t * a[1][j + 1])
    return a


def print_curve(points, ax):
    # drawPolygon(controlPoints, ax, True, color="lightgray")

    segments = []
    for t in np.arange(0, 1, 0.01):
        result = b_curve(t, points)[0][0]
        segments.append(result)
    drawPolygon(segments, ax)


lines = []


def print_lines(points, ax, t):
    for l in range(len(lines)):
        lines[l].remove();

    lines.clear()

    iterations = b_curve(t, points)

    for i in range(len(iterations)):
        lines.append(drawPolygon(iterations[i], ax, color="lightcoral"))


fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)
ax.set_xlim(0, 5)
ax.set_ylim(0, 4)

axTSlider = plt.axes([0.15, 0.1, 0.65, 0.03])
t_slider = Slider(
    ax=axTSlider,
    label='t',
    valmin=0.0,
    valmax=1.0,
    valinit=t,
)

controlPoints = np.array([[1, 2], [2, 3], [3, 1.5], [4, 3]])



currentPoint = b_curve(t, controlPoints)[0][0]
circle = plt.Circle(currentPoint, 0.05, color="blue")
ax.add_patch(circle)


def redraw():
    print_lines(controlPoints, ax, t)
    p = b_curve(t, controlPoints)[0][0]
    circle.set_center(p)
    circle.figure.canvas.draw()

def redrawAll():
    redraw()
    print_curve(controlPoints, ax)

redrawAll()

def updateT(val):
    global t
    t = val
    redraw()


t_slider.on_changed(updateT)

plt.show()
