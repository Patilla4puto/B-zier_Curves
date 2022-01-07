import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from matplotlib.widgets import Slider
import matplotlib
import scipy.special as s
from matplotlib.backend_bases import MouseButton

from Colors import Colors
from KnotPlot import KnotPlot
from PressablePoint import PressablePoint
from PolygonContainer import PolygonContainer

matplotlib.use('Qt5Agg')

c = Colors()

t_slider = None

fig, ax = plt.subplots(1, 2)
plt.subplots_adjust(bottom=0.25)
ax[0].set_xlim(0, 1)
ax[0].set_ylim(0, 1)
ax[0].set_aspect('equal', adjustable='box', anchor='C')

knots = np.linspace(0, 5, 6)
controlPoints = []
controlPointsCoordinates = []
u = 0.5
n = 2

tangentArrow = None


def on_remove(p):
    print("remove")


def onUpdate():
    t_slider.closedmin = knots.min()
    t_slider.closedmax = knots.max()
    t_slider.valmin = knots.min()
    t_slider.valmax = knots.max()

    global u
    if u < t_slider.valmin:
        t_slider.set_val(t_slider.valmin)
        u = t_slider.valmin

    if u > t_slider.valmax:
        t_slider.set_val(t_slider.valmax)
        u = t_slider.valmax

    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))
    redrawAll()


curveContainer = PolygonContainer(ax[0], 2)
controlPolygonContainer = PolygonContainer(ax[0])
scatterplot = KnotPlot(fig, ax[1], knots, on_remove, onUpdate)


def submit(text):
    degree = eval(text)
    print(degree)
    global n
    n = degree


axbox = plt.axes([0.1, 0.05, 0.8, 0.075])
text_box = TextBox(axbox, 'Degree', initial="2")
text_box.on_submit(submit)

axTSlider = plt.axes([.1, 0.15, 0.8, 0.075])
t_slider = Slider(
    ax=axTSlider,
    label='u',
    valmin=knots.min(),
    valmax=knots.max(),
    valinit=u,
)


def b_spline(n, ui, di, u):  # ui: knots, di: control points
    """
    :param n: degree
    :param ui: knot sequence eg.  [0. 1. 2. 3. 4. 5.]
    :param di: control points eg. [[0.1 0.1] [0.1 0.2] [0.2 0.2] [0.2 0.1]]
    :param u:
    :return: point on bspline curve for the given u, and derivative
    """
    d = np.array([u, 0.5 * u])  # TODO implement bspline
    derivative = np.array([1, 1])  # TODO implement bspline
    return d, derivative


def add_control_point(_ax, x, y):
    circle = PressablePoint(_ax, [x, y], on_remove, onUpdate, c.colors[len(controlPoints)])
    circle.connect()
    controlPoints.append(circle)
    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))


def draw_control_polygon(points):
    controlPolygonContainer.clearLines()
    controlPolygonContainer.addLine(points, 'green')
    controlPolygonContainer.redraw()


def drawTangentArrow():
    su, tangent = b_spline(n, knots, controlPointsCoordinates, u)

    global tangentArrow
    if tangentArrow is not None: tangentArrow.remove()
    vector = tangent * 0.2
    tangentArrow = ax[0].arrow(su[0], su[1], vector[0], vector[1], head_width=0.02, zorder=10)


def draw_BSpline_Curve():
    min = knots.min()
    max = knots.max()
    bSplinePoints = []
    for _u in np.arange(min, max, (max - min) / 20):
        p, _ = b_spline(n, knots, controlPointsCoordinates, _u)
        bSplinePoints.append(p)

    curveContainer.clearLines()
    curveContainer.addLine(bSplinePoints, 'red')
    curveContainer.redraw()


def redrawAll():
    global controlPointsCoordinates
    draw_control_polygon(controlPointsCoordinates)
    draw_BSpline_Curve()
    plt.draw()
    drawTangentArrow()
    print("redraw all")
    fig.canvas.draw()


add_control_point(ax[0], 0.1, 0.1)
add_control_point(ax[0], 0.1, 0.2)
add_control_point(ax[0], 0.2, 0.2)
add_control_point(ax[0], 0.2, 0.1)

redrawAll()

plt.show()
