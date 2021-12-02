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
    """a = points
    for r in range(1, len(points)):
        lenght = (len(a) - 1)
        aux = [0] * lenght
        for j in range(lenght):
            aux[j] = ((1 - t) * a[j] + t * a[j + 1])
        a = aux
    print(aux)
    return a"""
    a = [points]

    for r in range(1, len(points)):
        lenght = (len(a[0]) - 1)
        a.insert( 0,lenght *[0] )


        for j in range(lenght):
            a[0][j] = ((1 - t) * a[1][j] + t * a[1][j + 1])

    return a[0],a[1]


def deCasteljauSurface(s, t, points):
    list = []
    for e in points:
        list.append(deCasteljauCurves(t, e)[0][0])
        #print(list)
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


def createBezierSurface(points, sSteps, tSteps):
    grid = np.empty((sSteps + 1, tSteps + 1, 3))
    for j in np.arange(0, 1.0+1/(sSteps), 1 / sSteps):
        for t in np.arange(0, 1.0 +1 / (tSteps), 1 / tSteps):

            p = deCasteljauSurface(j, t, points)[0]

            grid[int(j * (sSteps)), int(t * (tSteps))] = p[0]

    return grid
def drawSurface( grid):
    for i in range(len(grid)-1):
        for j in range(len(grid[i])-1):
            addTriangle([grid[i][j],grid[i+1][j],grid[i][j+1]])
            addTriangle([grid[i][j+1],grid[i+1][j],grid[i+1][j+1]])
def drawVectorsPoint(points, s, t,ax):
    p0,va0= deCasteljauSurface(s, t, points)
    v = va0[1]-va0[0]
    print(p0,v)
    ax.quiver(p0[0][0], p0[0][1], p0[0][2], v[0], v[1], v[2], length=0.5, normalize=True, color="red")
    aux =points[:].transpose(1,0,2)
    q = deCasteljauSurface(s, t, aux)[1]
"""def drawVectors(points,t,k):
    print(deCasteljauCurves(points,t))
    print(deCasteljauCurves(points.transpose(),k))"""
points = np.array([np.array([[1, 1, 1], [1, 2, 0], [1, 4, 1]]),
     np.array([[2.5, 1, 1], [2.5, 2, 1], [2.5, 4, 1]]),
     np.array([[4, 1, 1], [4, 2, 2], [4, 4, 1]])])
#deCasteljauSurface(0.5, 0.5, points)

ax = fig.add_subplot(1, 1, 1, projection='3d')

# Make the grid
x = [1]
y = [1]
z = [1]
# Make the direction data for the arrows
u = [2]
v = [3]
w = [2]

ax.quiver(x, y, z, u, v, w, length=0.5, normalize=True,color="red")

grid = createBezierSurface(points, 10, 10)
drawVectorsPoint(points, 0.1, 0.1,ax)
drawPoints(ax,points)
drawSurface(grid)
drawTriangles(ax)

plt.show()
