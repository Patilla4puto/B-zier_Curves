import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from helper.Colors import Colors

matplotlib.use('Qt5Agg')

fig = plt.figure()
vertices = np.empty((0, 3))
triangles = np.empty((0, 3))

colors = Colors()


def deCasteljauCurves(t, points):
    # Initialization of the control points matrix
    a = [points]
    # Linear interpolation algorithm
    for r in range(1, len(points)):
        lenght = (len(a[0]) - 1)
        a.insert(0, lenght * [0])
        for j in range(lenght):
            a[0][j] = ((1 - t) * a[1][j] + t * a[1][j + 1])
    return a[0], a[1]


def deCasteljauSurface(s, t, points):
    list = []
    # We do the deCasteljauCurve for each point of each calculated curve ("doing deCasteljau in the other direction")
    for e in points:
        # we store the points of each curve in a array
        list.append(deCasteljauCurves(t, e)[0][0])
    # we return the reult of appliying the casteljau for curves to the points of each curve
    return (deCasteljauCurves(s, list))


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
    axis.plot_trisurf(x, y, z, triangles=triangles, edgecolor=[[0, 0, 0, 0.2]], linewidth=0.2, alpha=0.35, shade=True);


def drawPoints(axis, points):
    for array in points:
        xhs = []
        yhs = []
        zhs = []
        for e in array:
            xhs.append(e[0])
            yhs.append(e[1])
            zhs.append(e[2])
        axis.plot(xhs, yhs, zhs, color="slateblue")
    for i in range(len(points[0])):
        xvs = []
        yvs = []
        zvs = []
        for array in points:
            xvs.append(array[i][0])
            yvs.append(array[i][1])
            zvs.append(array[i][2])
            axis.plot(xvs, yvs, zvs, color="slateblue")


def createBezierSurface(points, sSteps, tSteps):
    # This function returns the calculated points of the surface when we divide the s interval [0,1] in sSteps equidistan segments and the t interval in tSteps equidistan segments
    # We initialices a matrix where we would store each calculated point of the surface
    grid = np.empty((sSteps + 1, tSteps + 1, 3))
    for j in np.arange(0, 1.0 + 1 / (sSteps), 1 / sSteps):
        for t in np.arange(0, 1.0 + 1 / (tSteps), 1 / tSteps):
            # for each value s and t we applies the casteljau algorithm for surfaces
            p = deCasteljauSurface(j, t, points)[0]

            grid[int(j * (sSteps)), int(t * (tSteps))] = p[0]

    return grid


def drawSurface(grid):
    for i in range(len(grid) - 1):
        for j in range(len(grid[i]) - 1):
            addTriangle([grid[i][j], grid[i + 1][j], grid[i][j + 1]])
            addTriangle([grid[i][j + 1], grid[i + 1][j], grid[i + 1][j + 1]])


def drawVectorsPoint(points, s, t, ax):
    p0, va0 = deCasteljauSurface(s, t, points)
    v0 = va0[1] - va0[0]
    #print(p0)
    ax.quiver(p0[0][0], p0[0][1], p0[0][2], v0[0], v0[1], v0[2], length=0.5, normalize=False, color="green",
              linewidth=2)
    aux = points[:].transpose(1, 0, 2)
    p1, va1 = deCasteljauSurface(t, s, aux)
    v1 = va1[1] - va1[0]
    ax.quiver(p1[0][0], p1[0][1], p1[0][2], v1[0], v1[1], v1[2], length=0.5, normalize=False, color="red", linewidth=2)
    v2 = np.cross(v0, v1)
    ax.quiver(p1[0][0], p1[0][1], p1[0][2], v2[0], v2[1], v2[2], length=0.5, normalize=True, color="blue", linewidth=2)


points = np.array([np.array([[1, 1, 1], [1, 2, 0], [1, 4, 1]]),
                   np.array([[2.5, 1, 2], [2.5, 3, 4], [2.5, 4, 2]]),
                   np.array([[4, 1, 0], [4, 2, 1], [4, 4, 0]])])

ax = fig.add_subplot(1, 1, 1, projection='3d')

grid = createBezierSurface(points, 10, 10)
drawPoints(ax, points)
drawSurface(grid)
drawTriangles(ax)
drawVectorsPoint(points, 0.5, 0.4, ax)

plt.show()
