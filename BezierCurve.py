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
c = Colors()
curves = []
arrow = None
polinoms = []
t = .5

fig, ax = plt.subplots(1, 2)
plt.subplots_adjust(bottom=0.25)
ax[0].set_xlim(0, 1)
ax[0].set_ylim(0, 1)
ax[0].set_aspect('equal', adjustable='box', anchor='C')
ax[1].set_xlim(0, 1)
ax[1].set_ylim(0, 1)
ax[1].set_aspect('equal', adjustable='box', anchor='C')

curveContainer = PolygonContainer(ax[0], 2)
controlPolygonContainer = PolygonContainer(ax[0])
bernsteinContainer = PolygonContainer(ax[1])


def bernstein_Polynomi(_t, points):
    n = len(points) - 1
    polinoms = []
    for i in range(n + 1):
        aux = s.binom(n, i) * (_t ** i) * ((1 - _t) ** (n - i))
        polinoms.append([_t, aux])
    return polinoms


def deCasteljau(t, points):
    a = [points]
    print(a)
    for r in range(1, len(points)):
        lenght = (len(a[0]) - 1)
        a.insert(0, [0] * lenght)
        for j in range(lenght):
            a[0][j] = ((1 - t) * a[1][j] + t * a[1][j + 1])
    return a

def deBoorgit (n, ui, ri, di, u):
    #ui_final -> final list of knots
    #indexU -> uppercase I in Boor Algorithm
    ui_final = ui[:]
    #ri_final -> new multiplicity
    ri_final = ri.copy()
    indexU = 0
    r = 0
    for i in range(1,len(ui)):
        indexU = i - 1
        if  ui[i-1] <= u <= ui[i]:
            if u == ui[i -1]:
                r = ri[u]
                ri_final[u] += 1
            else:
                ri_final[u] = 1
            break
    #final_d -> final list of Boor coordinates
    final_d = []
    #final_e -> final list of Greville abcises
    for j in range(r, n+1):
        final_d.append([0][:]*(n + 1  -j))
    for j in range(r, n + 1):
        final_d[r][j - r] = di[indexU - n + 1 + j]
    ui_final.insert(indexU + 1, u)
    for k in range(r + 1, n):
        for j in range(0, n - k + 1):
            alpha = (u - ui[indexU - n + k + j])/(ui[indexU + 1 + j] - ui[indexU - n + k + j])
            final_d[k][j] = (1-alpha)*final_d[k-1][j] + alpha*final_d[k-1][j+1]
    derivative = (n / (ui[indexU + 1] - ui[indexU]))*(final_d[n-1][1] - final_d[n-1][0])
    final_alpha = (u - ui[indexU]) / (ui[indexU + 1] - ui[indexU])
    final_d[n][0] = (1-final_alpha)*final_d[n-1][0] + final_alpha*final_d[n-1][1]
    return final_d, derivative, ui_final, ri_final




def drawBersteinpolinoms(points):
    bernsteinContainer.clearLines()

    lines = []
    for i in range(len(points)):
        lines.append([])
        bernsteinContainer.addLine(lines[i], c.colors[i])

    for _t in np.arange(0, 1.02, 0.01):
        result = bernstein_Polynomi(_t, points)
        for i in range(len(result)):
            lines[i].append(result[i])

    bernsteinContainer.redraw()


def draw_curve(points):
    global curves
    for e in curves:
        e.remove()

    curves.clear()
    line = []

    for t in [*np.arange(0, 1.0, 0.1 / len(points)), 1.0]:
        result = deCasteljau(t, points)[0][0]
        line.append(result)
    # curves.append(drawPolygon(lines, ax))
    curveContainer.clearLines()
    curveContainer.addLine(line, 'green')
    curveContainer.redraw()


def drawLines(points, t):
    iterations = deCasteljau(t, points)
    controlPolygonContainer.clearLines()
    for i in range(1, len(iterations) + 1):
        controlPolygonContainer.addLine(iterations[-i], c.getColor())

    vector = (iterations[1][1] - iterations[1][0])*0.2
    global arrow
    if arrow != None: arrow.remove()

    arrow = ax[0].arrow(iterations[0][0][0], iterations[0][0][1], vector[0], vector[1], head_width=0.02,zorder=10)
    controlPolygonContainer.redraw()


axTSlider = plt.axes([0.15, 0.1, 0.65, 0.03])
global t_slider
t_slider = Slider(
    ax=axTSlider,
    label='t',
    valmin=0.0,
    valmax=1.0,
    valinit=t,
)

controlPoints = []
controlPointsCoordinates = np.array([])


def on_remove(p):
    p.disconnect()
    controlPoints.remove(p)
    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))
    redrawAll()


def on_move(o):
    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))
    redrawAll()


def add_control_point(_ax, x, y):
    circle = PressablePoint(_ax, [x, y], on_remove, on_move, c.colors[len(controlPoints)])
    circle.connect()
    controlPoints.append(circle)
    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))


add_control_point(ax[0], 0.1, 0.1)
add_control_point(ax[0], 0.1, 0.8)
add_control_point(ax[0], 0.8, 0.8)
add_control_point(ax[0], 0.8, 0.1)

currentPoint = deCasteljau(t, controlPointsCoordinates)[0][0]

circle = plt.Circle(currentPoint, 0.015, color="blue")
ax[0].add_patch(circle)
circle_b = []


def redraw():
    c.resetIndex()
    drawLines(controlPointsCoordinates, t)
    p = deCasteljau(t, controlPointsCoordinates)[0][0]
    pts_bernstein = bernstein_Polynomi(t, controlPointsCoordinates)
    circle.set_center(p)
    circle.figure.canvas.draw()
    for i in range(len(circle_b)):
        circle_b[i].remove()
    circle_b.clear()

    for i in range(len(pts_bernstein)):
        circle_b.insert(0, plt.Circle(pts_bernstein[i], 0.01, color=c.colors[i]))
        ax[1].add_patch(circle_b[0])


def redrawAll():
    redraw()
    global controlPointsCoordinates
    draw_curve(controlPointsCoordinates)
    drawBersteinpolinoms(controlPointsCoordinates)
    plt.draw()
    print("redraw all")


def updateT(val):
    global t
    t = val
    redraw()


def onCanvasClick(event):
    if event.button is MouseButton.RIGHT and event.xdata and event.ydata:
        add_control_point(ax[0], event.xdata, event.ydata)
        redrawAll()


fig.canvas.mpl_connect('button_release_event', onCanvasClick)

redrawAll()
t_slider.on_changed(updateT)
plt.show()

