import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from Colors import Colors

matplotlib.use('Qt5Agg')

fig = plt.figure()
vertices = np.empty((0, 3))
triangles = np.empty((0, 3))

colors = Colors()


def deCasteljauCurves(t, points):
    a = points
    for r in range(1, len(points)):
        lenght = (len(a) - 1)
        aux = [0] * lenght
        for j in range(lenght):
            aux[j] = ((1 - t) * a[j] + t * a[j + 1])
        a = aux
    return a[0]


def deCasteljauSurface(j, t, points):
    list = []
    for e in points:
        list.append(deCasteljauCurves(t, e))
        print(list)
    return (deCasteljauCurves(j, list))


def addTriangle(points):
    global vertices
    global triangles
    vertices = np.append(vertices, points, axis=0)
    vertexCount = len(vertices)
    # a triangle consists of indices of the last 3 vertices
    triangle = [vertexCount - 1, vertexCount - 2, vertexCount - 3]
    triangles = np.append(triangles, [triangle], axis=0)


def drawTriangles(axis):
    x = vertices[:, 0]
    y = vertices[:, 1]
    z = vertices[:, 2]
    axis.plot_trisurf(x, y, z, triangles=triangles, edgecolor=[[0, 0, 0]], linewidth=1.0, alpha=0.5, shade=True);


def drawPoints(axis, points):
    for array in points:
        xhs = []
        yhs = []
        zhs = []
        for e in array:
            xhs.append(e[0])
            yhs.append(e[1])
            zhs.append(e[2])
        axis.plot(xhs, yhs, zhs, color="Black")
    for i in range(len(points[0])):
        xvs = []
        yvs = []
        zvs = []
        for array in points:
            xvs.append(array[i][0])
            yvs.append(array[i][1])
            zvs.append(array[i][2])
            axis.plot(xvs, yvs, zvs, color="Black")


def createBezierSurface(points, jSteps, tSteps):
    grid = np.empty((jSteps, tSteps, 3))
    for j in np.arange(0, 1.0, 1 / jSteps):
        for t in np.arange(0, 1.0, 1 / tSteps):
            p = deCasteljauSurface(j, t, points)
            grid[int(j * jSteps), int(t * tSteps)] = p
    return grid


tri = np.array([[0, 0, 0], [1, 0, 2], [2, 0, 1]])
addTriangle(tri)

points = np.array(
    [[[1, 1, 1], [1, 2, 0], [1, 4, 1]],
     [[2.5, 1, 1], [2.5, 2, 1], [2.5, 4, 1]],
     [[4, 1, 1], [4, 2, 2], [4, 4, 1]]])

ax = fig.add_subplot(1, 1, 1, projection='3d')

grid = createBezierSurface(points, 10, 10)

drawPoints(ax,points)
drawTriangles(ax)

plt.show()
