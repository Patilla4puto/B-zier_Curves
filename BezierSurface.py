import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib
from Colors import Colors
import scipy.special as s
from matplotlib.backend_bases import MouseButton

from PressablePoint import PressablePoint
from PolygonContainer import PolygonContainer

matplotlib.use('Qt5Agg')

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection='3d')
vertices = np.empty((0, 3))
triangles = np.empty((0, 3))


def addTriangle(points):
    global vertices
    global triangles
    vertices = np.append(vertices, points, axis=0)
    vertexCount = len(vertices)
    triangle = [vertexCount - 1, vertexCount - 2, vertexCount - 3]  # triangle consists of the indices last 3 vertices
    triangles = np.append(triangles, [triangle], axis=0)


tri = np.array([[0, 0, 0], [1, 0, 2], [2, 0, 1]])
addTriangle(tri)

x = vertices[:, 0]
y = vertices[:, 1]
z = vertices[:, 2]

ax.plot_trisurf(x, y, z, triangles=triangles, edgecolor=[[0, 0, 0]],
                linewidth=1.0,
                alpha=0.5, shade=True)

plt.show()
