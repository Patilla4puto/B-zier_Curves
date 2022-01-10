import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton


class PressablePoint:
    def __init__(self, ax, coord, onRemove, onMove, color):
        self.onRemove = onRemove
        self.onMove = onMove
        self.press = False
        self.moved = False
        self.circle = plt.Circle(coord, 0.01, color=color)
        ax.add_patch(self.circle)

    def connect(self):
        """Connect to all the events we need."""
        self.cidpress = self.circle.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.circle.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.circle.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.circle.axes:
            return

        contains, attrd = self.circle.contains(event)
        if not contains:
            return

        if event.button is MouseButton.LEFT:
            self.press = True

    def on_release(self, event):
        contains, attrd = self.circle.contains(event)
        if not contains:
            return

        if event.button is MouseButton.LEFT and not self.moved:
            self.onRemove(self)
            canvas = self.circle.figure.canvas
            self.circle.remove()
            canvas.draw()


        self.press = False
        self.moved = False

    def on_motion(self, event):
        if event.button is MouseButton.LEFT and self.press and event.xdata and event.ydata:
            self.circle.center = (event.xdata, event.ydata)
            self.circle.figure.canvas.draw()
            self.onMove(self)
            self.moved = True

    def get_coordinates(self):
        return self.circle.center

    def disconnect(self):
        """Disconnect all callbacks."""
        self.circle.figure.canvas.mpl_disconnect(self.cidpress)
