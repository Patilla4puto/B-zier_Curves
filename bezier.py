import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

def drawPolygon(points, ax, showCircle=False, color="k"):
    path = Path(points, closed=False)
    patch = patches.PathPatch(path, facecolor='none', edgecolor=color, lw=2)
    ax.add_patch(patch)

    if showCircle:
        # Add green circles on controlpoints
        for p in points:
            ax.add_patch(plt.Circle(p, 0.05, color="green"))


def b_curve(t, points):
    a = points.copy()
    n = len(a)
    for r in range(1, n):
        for j in range(0, n - r):
            a[j] = (1 - t) * a[j] + t * a[j + 1]
    return a[0]


def print_curve(points, ax):
    drawPolygon(controlPoints, ax, True, color="lightgray")

    segments = []
    for t in np.arange(0, 1, 0.001):
        result = b_curve(t, points)
        segments.append(result)
    drawPolygon(segments, ax)


fig, ax = plt.subplots()
ax.set_xlim(0, 5)
ax.set_ylim(0, 4)

controlPoints = np.array([[1, 2], [2, 3], [3, 1.5], [4, 3]])
print_curve(controlPoints, ax)

plt.show()
