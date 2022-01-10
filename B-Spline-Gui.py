import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from matplotlib.widgets import Slider
from matplotlib.widgets import Button

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

circle = None  # plt.Circle(currentPoint, 0.015, color="blue")


variableLabel = None  # plt.figtext(0.05, 0.90, 'L = 5 : |Control Points|\nK = 6 : |Knots|\nn = 2 : degree')
plt.figtext(0.35, 0.97, 'L =? K - n + 1')
eqLabel = None  # plt.figtext(0.35, 0.94, '0 = 0')
infoLabel = None

knots = np.linspace(0, 5, 6)
controlPoints = []
controlPointsCoordinates = []
u = 0.5
n = 2

tangentArrow = None

#Logic


def deBoor (n, ui, ri, di, u):
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
        final_d.append([0][:]*(n + 1 - j))
    for j in range(r, n+1):
        print(indexU - n + j + 1, u, ui)
        final_d[r][j - r] = di[indexU - n + j + 1]
    #np.insert(ui_final, indexU + 1, u)
    ui_final.insert(indexU + 1, u)
    for k in range(r + 1, n):
        for j in range(0, n - k + 1):
            alpha = (u - ui[indexU - n + k + j])/(ui[indexU + 1 + j] - ui[indexU - n + k + j])
            final_d[k][j] = (1-alpha)*final_d[k-1][j] + alpha*final_d[k-1][j+1]
    derivative = (n / (ui[indexU + 1] - ui[indexU]))*(final_d[n-1][1] - final_d[n-1][0])
    final_alpha = (u - ui[indexU]) / (ui[indexU + 1] - ui[indexU])
    final_d[n][0] = (1-final_alpha)*final_d[n-1][0] + final_alpha*final_d[n-1][1]
    return final_d, derivative, ui_final, ri_final


#print(deBoor(2, [-10, -6, -2, -2, 0, 4, 8, 12, 16, 18], {-10: 1, -6 : 1 , -2 : 2 , 0 : 1, 4 : 1 , 8 : 1 , 12: 1, 16: 1, 18: 1},[-6, -4, -2, 0, -8, 0, 8, 4, 2], 6))

def onRemoveControlPoint(p):
    p.disconnect()
    controlPoints.remove(p)
    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))
    redrawAll()


def onUpdate(p):
    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))
    redrawAll()


def onUpdateKnots(k):
    global knots
    knots = k
    min = knots[n - 1]
    max = knots[-(n)]
    t_slider.closedmin = min
    t_slider.closedmax = max
    t_slider.valmin = min
    t_slider.valmax = max

    global u
    if u < t_slider.valmin:
        t_slider.set_val(t_slider.valmin)
        u = t_slider.valmin

    if u > t_slider.valmax:
        t_slider.set_val(t_slider.valmax)
        u = t_slider.valmax

    redrawAll()


curveContainer = PolygonContainer(ax[0], 2)
controlPolygonContainer = PolygonContainer(ax[0])
scatterplot = KnotPlot(fig, ax[1], knots, onUpdateKnots)

degreeLabel = None


# axbox = plt.axes([0.3, 0.05, 0.4, 0.075])


def incrementDegree(p):
    global n, degreeLabel
    n += 1
    redrawAll()


def decrementDegree(p):
    global n, degreeLabel
    n = max(2, n - 1)
    redrawAll()


axdecr = plt.axes([0.1, 0.05, 0.2, 0.075])
axincr = plt.axes([0.7, 0.05, 0.2, 0.075])
bnext = Button(axdecr, '-')
bnext.on_clicked(decrementDegree)
bprev = Button(axincr, '+')
bprev.on_clicked(incrementDegree)

axTSlider = plt.axes([.1, 0.15, 0.8, 0.075])
t_slider = Slider(
    ax=axTSlider,
    label='u',
    valmin=0,
    valmax=10,
    valinit=u,
)


def updateU(val):
    global u
    u = val
    redrawAll()


t_slider.on_changed(updateU)


def b_spline(n, ui, di, u):  # ui: knots, di: control points
    """
    :param n: degree
    :param ui: knot sequence eg.  [0. 1. 2. 3. 4. 5.]
    :param di: control points eg. [[0.1 0.1] [0.1 0.2] [0.2 0.2] [0.2 0.1]]
    :param u:
    :return: point and derivative on bspline curve for the given u
    """
    # calculate multiplicities
    ri = dict()
    for i in ui:
        if not (i in ri.keys()):
            ri[i] = 1
        else:
            ri[i] += 1
    final_d, derivative, ui_final, ri_final = deBoor(n, ui.tolist(), ri, di, u)

    return np.array(final_d[-1][0]), derivative


def add_control_point(_ax, x, y):
    circle = PressablePoint(_ax, [x, y], onRemoveControlPoint, onUpdate, c.colors[len(controlPoints)])
    circle.connect()
    controlPoints.append(circle)
    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))


def draw_control_polygon(points):
    controlPolygonContainer.clearLines()
    controlPolygonContainer.addLine(points, 'green')
    controlPolygonContainer.redraw()


def drawPointAndTangent():
    su, tangent = b_spline(n, knots, controlPointsCoordinates, u)

    global tangentArrow, circle
    if tangentArrow is not None: tangentArrow.remove()
    vector = tangent * 0.2
    tangentArrow = ax[0].arrow(su[0], su[1], vector[0], vector[1], head_width=0.02, zorder=10)

    if circle is None:
        circle = plt.Circle(su, 0.015, color="blue")
        ax[0].add_patch(circle)
    else:
        circle.set_center(su)
        circle.figure.canvas.draw()


def draw_BSpline_Curve():
    min = knots[n - 1]
    max = knots[-(n)]
    bSplinePoints = []
    for _u in np.arange(min + 0.0000001, max, (max - min) / 50):
        p, _ = b_spline(n, knots, controlPointsCoordinates, _u)
        bSplinePoints.append(p)

    curveContainer.clearLines()
    curveContainer.addLine(bSplinePoints, 'red')
    curveContainer.redraw()


def updateTextAndCheckConfiguration():
    global variableLabel, eqLabel, infoLabel, degreeLabel
    if variableLabel is not None: variableLabel.remove()
    if eqLabel is not None: eqLabel.remove()
    if infoLabel is not None: infoLabel.remove()
    if degreeLabel is not None: degreeLabel.remove()

    degreeLabel = plt.figtext(0.45, 0.075, 'Degree %d' % n)

    L = len(controlPointsCoordinates)
    K = len(knots)

    valid = L == K - n + 1  # is valid configuration
    infoString = ''
    if L < K - n + 1:
        infoString = '%d ' % (K - L - n + 1) + 'more Control Point' \
                     + (' is needed' if K - n + 1 - L == 1 else 's are needed')
    elif L > K - n + 1:
        infoString = '%d ' % (L - (K - n + 1)) + 'more Knot' \
                     + (' is needed' if L - (K - n + 1) == 1 else 's are needed')

    variableLabel = plt.figtext(0.05, 0.90, 'L = %d : |Control Points|\nK = %d : |Knots|\nn = %d : degree' % (L, K, n))
    eqLabel = plt.figtext(0.35, 0.94, '%d =? %d - %d + 1 = %d -> %r' % (L, K, n, K - n + 1, valid))
    infoLabel = plt.figtext(0.35, 0.90, infoString, color='red')

    return valid


def redrawAll():
    global controlPointsCoordinates, tangentArrow, circle

    draw_control_polygon(controlPointsCoordinates)
    valid = updateTextAndCheckConfiguration()
    if not valid:
        curveContainer.clearLines()
        curveContainer.redraw()

        if tangentArrow is not None:
            tangentArrow.remove()
            tangentArrow = None

        if circle is not None:
            circle.remove()
            circle = None

        fig.canvas.draw()
        return

    draw_BSpline_Curve()
    plt.draw()
    drawPointAndTangent()
    print("redraw all")
    fig.canvas.draw()


def onCanvasClick(event):
    if event.inaxes != ax[0]:
        return

    if event.button is MouseButton.RIGHT and event.xdata and event.ydata:
        add_control_point(ax[0], event.xdata, event.ydata)
        redrawAll()


fig.canvas.mpl_connect('button_release_event', onCanvasClick)

add_control_point(ax[0], 0.1, 0.1)
add_control_point(ax[0], 0.1, 0.3)
add_control_point(ax[0], 0.5, 0.5)
add_control_point(ax[0], 0.9, 0.7)
add_control_point(ax[0], 0.9, 0.9)

onUpdateKnots(knots)
redrawAll()

plt.show()
