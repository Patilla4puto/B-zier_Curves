import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib.widgets import Slider, Button
import matplotlib
from Colors import Colors
import scipy.special as s
matplotlib.use('Qt5Agg')
c = Colors()
curve = []
polinoms = []
t = .5


def drawPolygon(points, ax, color="k"):
    path = Path(points, closed=False)
    patch = patches.PathPatch(path, facecolor='none', edgecolor=color, lw=2)
    ax.add_patch(patch)

    return patch

def bernstein_Polynomi(t,points):
    n=len(points)-1
    polinoms=np.empty((n+1,2), dtype=float)

    for i in range(n+1):
        aux = s.binom(n,i)*(t**i)*((1-t)**(n-i))
        polinoms[i]=[t,aux]
    return(polinoms)

def b_curve(t, points):
    a = [points]
    for r in range(1, len(points)):
        lenght = (len(a[0]) - 1)
        a.insert(0, [0] * lenght)
        for j in range(lenght):
            a[0][j] = ((1 - t) * a[1][j] + t * a[1][j + 1])
    return a

def print_bersteinpolinoms(points,ax):
    global polinoms
    for e in polinoms:
        e.remove()
    polinoms.clear()
    lines=[]
    for i in range(len(points)):
        lines.append([])
    for t in np.arange(0, 1.02, 0.01):
        result = bernstein_Polynomi(t, points)
        for i in range(len(result)):
            lines[i].append(result[i])
    for e in lines:
        polinoms.append(drawPolygon(e, ax))

def print_curve(points, ax):
    # drawPolygon(controlPoints, ax, True, color="lightgray")
    global curve
    #curve[0].remove()
    lines=[]
    for t in np.arange(0, 1.02, 0.01):
        result = b_curve(t, points)[0][0]
        lines.append(result)
    curve.append(drawPolygon(lines, ax))


lines = []


def print_lines(points, ax, t):
    for l in range(len(lines)):
        lines[l].remove()

    lines.clear()

    iterations = b_curve(t, points)

    for i in range(1, len(iterations) + 1):
        lines.append(drawPolygon(iterations[-i], ax, color=c.getColor()))


fig, ax = plt.subplots(2)
plt.subplots_adjust(bottom=0.25)
ax[0].set_xlim(0, 5)
ax[0].set_ylim(0, 4)
ax[1].set_xlim(0,1)
ax[1].set_ylim(0,1)
ax[1].set_aspect('equal', adjustable='box', anchor='C')

axTSlider = plt.axes([0.15, 0.1, 0.65, 0.03])
global t_slider
t_slider = Slider(
    ax=axTSlider,
    label='t',
    valmin=0.0,
    valmax=1.0,
    valinit=t,
)


class PressablePoint:
    def __init__(self, ax, coord, onRemove):
        self.onRemove = onRemove
        self.coord = coord
        self.circle = plt.Circle(coord, 0.05, color="green")
        ax.add_patch(self.circle)

    def connect(self):
        """Connect to all the events we need."""
        self.cidpress = self.circle.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)

    def on_press(self, event):
        """
        if event.xdata == self.point[0] and event.ydata == self.point[1]:
            for i in range(controlPoints):
                if controlPoints[i][0] == self.point[0] and controlPoints[i][1] == self.point[1]:
                    controlPoints.remove(i)"""
        if event.inaxes != self.circle.axes:
            return

        contains, attrd = self.circle.contains(event)
        if not contains:
            return
        self.onRemove(self)
        self.circle.remove()

    def get_coordinates(self):
        return self.coord

    def disconnect(self):
        """Disconnect all callbacks."""
        self.circle.figure.canvas.mpl_disconnect(self.cidpress)


controlPoints = []
controlPointsCoordinates = np.array([])


def on_remove(p):
    p.disconnect()
    controlPoints.remove(p)
    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))
    redrawAll()


def add_control_point(_ax, x, y):
    circle = PressablePoint(_ax, [x, y], on_remove)
    circle.connect()
    controlPoints.append(circle)
    global controlPointsCoordinates
    controlPointsCoordinates = np.array(list(map(lambda p: p.get_coordinates(), controlPoints)))


add_control_point(ax[0], 1, 1)
add_control_point(ax[0], 1, 2)
add_control_point(ax[0], 2, 2)
add_control_point(ax[0], 2, 1)

currentPoint = b_curve(t, controlPointsCoordinates)[0][0]

circle = plt.Circle(currentPoint, 0.05, color="blue")
ax[0].add_patch(circle)
currentPoint_b = bernstein_Polynomi(t,controlPointsCoordinates)
circle_b=[]
for p in currentPoint_b:
    circle_b.insert(0,plt.Circle(p ,0.05, color=c.getColor()))
    ax[1].add_patch(circle_b[0])

def redraw():
    c.resetIndex()
    print_lines(controlPointsCoordinates, ax[0], t)
    p = b_curve(t, controlPointsCoordinates)[0][0]
    pts_bernstein=bernstein_Polynomi(t,controlPointsCoordinates)
    circle.set_center(p)
    circle.figure.canvas.draw()
    for i in range(len(circle_b)):
        circle_b[i].remove()
    circle_b.clear()
    for e in pts_bernstein:
        circle_b.insert(0, plt.Circle(e, 0.05, color=c.getColor()))
        ax[1].add_patch(circle_b[0])


def redrawAll():
    redraw()
    print_curve(controlPointsCoordinates, ax[0])
    print_bersteinpolinoms(controlPointsCoordinates,ax[1])
    plt.draw()


redrawAll()


def updateT(val):
    global t
    t = val
    redraw()


t_slider.on_changed(updateT)
plt.show()