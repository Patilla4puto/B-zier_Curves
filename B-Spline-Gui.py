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
from matplotlib.gridspec import GridSpec
matplotlib.use('Qt5Agg')

c = Colors()

t_slider = None
fig = plt.figure(figsize=(10, 10))
gs = GridSpec(nrows=2, ncols=2)
ax =[]
ax.append(fig.add_subplot(gs[:,0]))
ax.append(fig.add_subplot(gs[0,1]))
ax.append(fig.add_subplot(gs[1,1]))
plt.subplots_adjust(bottom=0.27)
ax[0].set_xlim(0, 1)
ax[0].set_ylim(0, 1)
ax[0].set_aspect('equal', adjustable='box', anchor='C')

knots = np.linspace(0, 6, 7)
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
        #print(indexU - n + j + 1, u, ui)
        final_d[r][j - r] = di[indexU - n + j + 1]
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

def on_remove(p):
    p.disconnect()
    controlPoints.remove(p)
    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))
    redrawAll()


def onUpdate(p):
    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))
    redrawAll()


def onUpdateKnots():
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

    redrawAll()


curveContainer = PolygonContainer(ax[0], 2)
b_splines_functions_container = PolygonContainer(ax[2])
controlPolygonContainer = PolygonContainer(ax[0])
scatterplot = KnotPlot(fig, ax[1], knots, on_remove, onUpdateKnots)

axbox = plt.axes([0.3, 0.05, 0.4, 0.075])
text_box = TextBox(axbox, '', initial="Degree 2")

def incrementDegree(p):
    global n
    n += 1
    text_box.set_val("Degree %d" % n)
    redrawAll()


def decrementDegree(p):
    global n
    n = max(2, n - 1)
    text_box.set_val("Degree %d" % n)
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
    #calculate multiplicities
    ri = dict()
    for i in ui:
        if not(i in ri.keys()):
            ri[i] = 1
        else:
            ri[i] += 1
    final_d, derivative, ui_final, ri_final = deBoor(n, ui.tolist(), ri, di, u)

    return np.array(final_d[-1]), derivative


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
    min = knots[n-1]
    max = knots[-(n)]
    bSplinePoints = []
    for _u in np.arange(min + 0.0000001, max, (max - min) / 20):
        p, _ = b_spline(n, knots, controlPointsCoordinates, _u)
        bSplinePoints.append(p[0])

    curveContainer.clearLines()
    curveContainer.addLine(bSplinePoints, 'red')
    curveContainer.redraw()
def drawB_Spline_Functions():
    ax[2].set_xlim(0, knots[-1])
    ax[2].set_ylim(0, 1)
    b_splines_functions_container.clearLines()
    lines = []
    for i in range(len(controlPoints)-1):
        lines.append([])
        b_splines_functions_container.addLine(lines[i], c.colors[i])

    for _t in np.arange(knots[0]+0.0000001, knots[-1], 0.01):
        result = b_splines_functions(_t, knots)
        for i in range(len(result)):
            lines[i].append(result[i])
    b_splines_functions_container.redraw()
def b_splines_functions(t,knots):
    global n
    global controlPoints
    sol =[]
    N1 =[]
    for j in range(1,len(knots)+1):
        if(knots[j-1]< t < knots[j]):
            N1.append(1)
        else:
            N1.append(0)
    N = [N1]
    for m in range(1, n):
        aux=[]
        for j in range(0, len(knots)-m-1):
            aux.append(N[m-1][j]*(t-knots[j])/(knots[j+m]-knots[j])+N[m-1][j+1]*(knots[j+m+1]-t)/(knots[j+m+1]-knots[j+1]))
        N.append(aux)
    for a in N[-1]:
        sol.append(np.array([t,a]))
    return(sol)

def redrawAll():
    global controlPointsCoordinates
    draw_control_polygon(controlPointsCoordinates)
    draw_BSpline_Curve()
    drawB_Spline_Functions()
    plt.draw()
    #drawTangentArrow()

    print("redraw all")
    fig.canvas.draw()


def onCanvasClick(event):
    if event.button is MouseButton.RIGHT and event.xdata and event.ydata:
        add_control_point(ax[0], event.xdata, event.ydata)
        redrawAll()


fig.canvas.mpl_connect('button_release_event', onCanvasClick)

add_control_point(ax[0], 0.1, 0.1)
add_control_point(ax[0], 0.1, 0.2)
add_control_point(ax[0], 0.2, 0.2)
add_control_point(ax[0], 0.2, 0.15)
add_control_point(ax[0], 0.2, 0.1)
add_control_point(ax[0], 0.3, 0.1)

redrawAll()

plt.show()
