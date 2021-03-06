import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.widgets import Button

import matplotlib
from matplotlib.backend_bases import MouseButton

from helper.Colors import Colors
from helper.KnotPlot import KnotPlot
from helper.PressablePoint import PressablePoint
from helper.PolygonContainer import PolygonContainer

matplotlib.use('Qt5Agg')

c = Colors()

fig, ax = plt.subplots(1, 2)
plt.subplots_adjust(bottom=0.45)
ax[0].set_xlim(0, 1)
ax[0].set_ylim(0, 1)
ax[0].set_aspect('equal', adjustable='box', anchor='C')

t_slider = None
circle = None
circle_bspline_functions = []
variableLabel = None
plt.figtext(0.65, 0.97, 'L =? K - n + 1')
eqLabel = None
infoLabel = None
degreeLabel = None
tangentArrow = None

knots = np.linspace(1, 5, 5)
controlPoints = []
controlPointsCoordinates = []
u = 2.7
n = 2

curveContainer = PolygonContainer(ax[0], 2)
b_splines_functions_container = PolygonContainer(ax[1])
controlPolygonContainer = PolygonContainer(ax[0])

axdecr = plt.axes([0.1, 0.05, 0.2, 0.075])
axincr = plt.axes([0.7, 0.05, 0.2, 0.075])
knotAxis = plt.axes([0.4, 0.3, 0.5, 0.075])

plt.figtext(0.02, 0.9, 'left drag: move\nleft click on point: remove\nright click: add')
plt.figtext(0.1, 0.275, 'left click: move\nright click: add/remove')


# Logic
def deBoor(n, ui, ri, di, u):
    # ui_final -> final list of knots
    ui_final = ui[:]
    # ri_final -> new multiplicity dictionary
    ri_final = ri.copy()
    # indexU -> uppercase I in Boor Algorithm
    indexU = 0
    r = 0
    # Iteration to calculate the new multiplicities, also to get I
    for i in range(1, len(ui)):
        indexU = i - 1
        if ui[i - 1] <= u <= ui[i]:
            if u == ui[i - 1]:
                r = ri[u]
                ri_final[u] += 1
            else:
                ri_final[u] = 1
            break
    # final_d -> final list of Boor coordinates
    final_d = []
    # Initilization part of the deBoor algorithm
    for j in range(r, n + 1):
        final_d.append([0][:] * (n + 1 - j))
    for j in range(r, n + 1):
        if (indexU - n + j + 1 < 0):
            final_d[r][j - r] = di[0]
        else:
            final_d[r][j - r] = di[indexU - n + j + 1]
    ui_final.insert(indexU + 1, u)
    # Linear interpolation part of the deBoor algorithm
    for k in range(r + 1, n):
        for j in range(0, n - k + 1):
            alpha = (u - ui[indexU - n + k + j]) / (ui[indexU + 1 + j] - ui[indexU - n + k + j])
            final_d[k][j] = (1 - alpha) * final_d[k - 1][j] + alpha * final_d[k - 1][j + 1]
    # Last iteration, get the derivative(u), d_final(u), and the final value of alpha
    derivative = (n / (ui[indexU + 1] - ui[indexU])) * (final_d[n - 1][1] - final_d[n - 1][0])
    final_alpha = (u - ui[indexU]) / (ui[indexU + 1] - ui[indexU])
    final_d[n][0] = (1 - final_alpha) * final_d[n - 1][0] + final_alpha * final_d[n - 1][1]
    return final_d, derivative, ui_final, ri_final


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
    updateRange()
    redrawAll()


def updateRange():
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


def incrementDegree(p):
    global n, degreeLabel
    n += 1
    updateRange()
    redrawAll()


def decrementDegree(p):
    global n, degreeLabel
    n = max(2, n - 1)
    updateRange()
    redrawAll()


scatterplot = KnotPlot(fig, knotAxis, knots, onUpdateKnots)

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

    return np.array(final_d[-1][0]), derivative, final_d


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
    su, tangent, _ = b_spline(n, knots, controlPointsCoordinates, u)

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


def drawConstructionLines():
    _, _, dArray = b_spline(n, knots, controlPointsCoordinates, u)

    for i in range(len(dArray) - 1):
        curveContainer.addLine(dArray[i], c.getColor())

    curveContainer.redraw()


def draw_BSpline_Curve():
    min = knots[n - 1]
    max = knots[-(n)]
    bSplinePoints = []
    for _u in np.arange(min + 0.0000001, max, 0.01):
        p, _, _ = b_spline(n, knots, controlPointsCoordinates, _u)
        bSplinePoints.append(p)

    curveContainer.clearLines()
    curveContainer.addLine(bSplinePoints, 'red')
    curveContainer.redraw()


def drawB_Spline_Functions():
    # In this function we calculated all the points of the b-spline functions and draw then in the 3 plot(the left-botton one)
    ax[1].set_xlim(0, knots[-1])
    ax[1].set_ylim(0, 1)
    b_splines_functions_container.clearLines()
    lines = []
    # Here we calculate the generate the containers of the lines for each function
    for i in range(len(controlPoints) - 1):
        lines.append([])
        b_splines_functions_container.addLine(lines[i], c.colors[i])
    # Here we get the points of each function at each knot value and store in it respective line-container
    for _t in np.arange(knots[0] + 0.0000001, knots[-1], 0.01):
        result = b_splines_functions(_t, knots)
        for i in range(len(result)):
            lines[i].append(result[i])
    # Finally we calculate the point of each function at the value of the slider to mark it with a point
    points = b_splines_functions(u, knots)

    for i in range(len(circle_bspline_functions)):
        circle_bspline_functions[i].remove()
    circle_bspline_functions.clear()

    for i in range(len(points)):
        circle_bspline_functions.insert(0, plt.Circle(points[i], 0.03, color=c.colors[i]))
        ax[1].add_patch(circle_bspline_functions[0])
    b_splines_functions_container.redraw()


def b_splines_functions(t, knots):
    # This function returns the points of each b-spline function in a given knot or value between two knots
    global n
    global controlPoints
    sol = []
    N1 = []
    # here we get the point of the function for the degree 1 because it is an special case
    for j in range(1, len(knots) + 1):
        if (knots[j - 1] <= t < knots[j]):
            N1.append(1)
        else:
            N1.append(0)
    N = [N1]
    # Then with the values of the degree 1 stored we iterate until the degre we have to obtain the points of the required functions
    for m in range(1, n):
        aux = []
        for j in range(0, len(knots) - m - 1):
            value = N[m - 1][j] * (t - knots[j]) / (knots[j + m] - knots[j]) + N[m - 1][j + 1] * (
                    knots[j + m + 1] - t) / (
                            knots[j + m + 1] - knots[j + 1])
            aux.append(value)
        N.append(aux)
    # we return the points(knot-value,result of the last iteration) to show then as a grafic
    for a in N[-1]:
        sol.append(np.array([t, a]))
    return (sol)


def updateTextAndCheckConfiguration():
    global variableLabel, eqLabel, infoLabel, degreeLabel
    if variableLabel is not None: variableLabel.remove()
    if eqLabel is not None: eqLabel.remove()
    if infoLabel is not None: infoLabel.remove()
    if degreeLabel is not None: degreeLabel.remove()

    degreeLabel = plt.figtext(0.45, 0.075, 'Degree %d' % n)

    L = len(controlPointsCoordinates)
    K = len(knots)

    valid = L == K - n + 1 and L >= n + 1  # is valid configuration
    infoString = ''
    if L < K - n + 1:
        infoString = '%d ' % (K - L - n + 1) + 'more Control Point' \
                     + (' is needed' if K - n + 1 - L == 1 else 's are needed')
    elif L > K - n + 1:
        infoString = '%d ' % (L - (K - n + 1)) + 'more Knot' \
                     + (' is needed' if L - (K - n + 1) == 1 else 's are needed')
    elif L < n + 1:
        infoString = '%d ' % (n + 1 - L) + 'more Control Point' \
                     + (' is needed' if n + 1 - L == 1 else 's are needed')

    variableLabel = plt.figtext(0.35, 0.90, 'L = %d : |Control Points|\nK = %d : |Knots|\nn = %d : degree' % (L, K, n))
    eqLabel = plt.figtext(0.65, 0.94, '%d =? %d - %d + 1 = %d -> %r' % (L, K, n, K - n + 1, valid))
    infoLabel = plt.figtext(0.65, 0.90, infoString, color='red')

    return valid


def redrawAll():
    global controlPointsCoordinates, tangentArrow, circle

    c.resetIndex()
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
    drawB_Spline_Functions()
    plt.draw()
    drawPointAndTangent()
    drawConstructionLines()

    fig.canvas.draw()


def onCanvasClick(event):
    if event.inaxes != ax[0]:
        return

    if event.button is MouseButton.RIGHT and event.xdata and event.ydata:
        add_control_point(ax[0], event.xdata, event.ydata)
        redrawAll()


fig.canvas.mpl_connect('button_release_event', onCanvasClick)

add_control_point(ax[0], 0.1, 0.1)
add_control_point(ax[0], 0.1, 0.9)
add_control_point(ax[0], 0.9, 0.1)
add_control_point(ax[0], 0.9, 0.9)

onUpdateKnots(knots)
redrawAll()

plt.show()
