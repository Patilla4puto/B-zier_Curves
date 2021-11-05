import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib.widgets import Slider, Button
import matplotlib
from Colors import Colors

matplotlib.use('Qt5Agg')
c = Colors()

t = .5


def drawPolygon(points, ax, color="k"):
    path = Path(points, closed=False)
    patch = patches.PathPatch(path, facecolor='none', edgecolor=color, lw=2)
    ax.add_patch(patch)

    return patch


def b_curve(t, points):
    a = [points]
    for r in range(1, len(points)):
        lenght = (len(a[0]) - 1)
        a.insert(0, [0] * lenght)
        for j in range(lenght):
            a[0][j] = ((1 - t) * a[1][j] + t * a[1][j + 1])
    return a


def print_curve(points, ax):
    # drawPolygon(controlPoints, ax, True, color="lightgray")

    segments = []
    for t in np.arange(0, 1, 0.01):
        result = b_curve(t, points)[0][0]
        segments.append(result)
    drawPolygon(segments, ax)


lines = []


def print_lines(points, ax, t):
    for l in range(len(lines)):
        lines[l].remove()

    lines.clear()

    iterations = b_curve(t, points)

    for i in range(1, len(iterations) + 1):
        lines.append(drawPolygon(iterations[-i], ax, color=c.getColor()))


fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)
ax.set_xlim(0, 5)
ax.set_ylim(0, 4)

axTSlider = plt.axes([0.15, 0.1, 0.65, 0.03])
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


add_control_point(ax, 1, 1)
add_control_point(ax, 1, 2)
add_control_point(ax, 2, 2)
add_control_point(ax, 2, 1)

currentPoint = b_curve(t, controlPointsCoordinates)[0][0]
circle = plt.Circle(currentPoint, 0.05, color="blue")
ax.add_patch(circle)


def redraw():
    c.resetIndex()
    print_lines(controlPointsCoordinates, ax, t)
    p = b_curve(t, controlPointsCoordinates)[0][0]
    circle.set_center(p)
    circle.figure.canvas.draw()


def redrawAll():
    redraw()
    print_curve(controlPointsCoordinates, ax)
    plt.show()


redrawAll()


def updateT(val):
    global t
    t = val
    redraw()


t_slider.on_changed(updateT)

plt.show()
