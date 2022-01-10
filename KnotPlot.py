from matplotlib.backend_bases import MouseButton
import numpy as np
import matplotlib.pyplot as plt


class KnotPlot:

    def __init__(self, fig, ax, knots, onUpdate):
        self.onUpdate = onUpdate
        self.press = False
        self.moved = False
        self.selectedKnot = None

        self.fig = fig
        self.ax = ax
        self.knots = knots
        # self.circle = plt.Circle(coord, 0.01, color=color)
        # ax.add_patch(self.circle)

        ax.set_ylim(-0.4, 3)
        ax.set_xlim(-0.5, 10.5)
        ax.get_yaxis().set_visible(False)
        #ax.set_aspect('equal', adjustable='box', anchor='C')
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

        self.tooltip = ax.annotate("", xy=(0, 0), xytext=(-10, -18), textcoords="offset points",
                                   bbox=dict(boxstyle="round", fc="w"), )




        self.tooltip.set_visible(False)
        self.plot, = self.ax.plot([], [], 'v')
        self.redraw()

        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def redraw(self):
        y = np.zeros(len(self.knots))  # np.linspace(0, 9, 20)

        if self.selectedKnot is None:
            self.knots[:] = np.sort(self.knots)
        else:
            currValue = self.knots[self.selectedKnot]
            self.knots[:] = np.sort(self.knots)

            self.selectedKnot = 0
            for i in range(len(self.knots)):
                if self.knots[i] == currValue:
                    self.selectedKnot = i

        for i in range(len(self.knots)):
            if i + 1 < len(self.knots) and self.knots[i] == self.knots[i + 1]:
                y[i + 1] = y[i] + 0.5  # 0.5

        self.plot.set_data(self.knots, y)
        self.fig.canvas.draw()

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        closestDist = float("inf")
        x = round(event.xdata, 1)

        if event.button is MouseButton.LEFT and event.xdata:  # move knots with left mouse button
            self.press = True
            # print(event.xdata)

            for i in range(len(self.knots)):
                dist = abs(x - self.knots[i])
                if dist < closestDist and dist < 0.1:
                    self.selectedKnot = i
                    closestDist = dist
        elif event.button is MouseButton.RIGHT:  # add or delete knot with right mouse button
            for i in range(len(self.knots)):
                dist = abs(x - self.knots[i])
                if dist < closestDist and dist < 0.1:
                    self.selectedKnot = i
                    closestDist = dist

            if self.selectedKnot is None:  # add knot
                self.knots = np.append(self.knots, x)
                print("add knot at {}".format(x))
            else:  # delete knot
                self.knots = np.delete(self.knots, self.selectedKnot)
                print("remove knot at {} at index {}".format(x, self.selectedKnot))
                self.selectedKnot = None

            self.redraw()
            self.onUpdate(self.knots)

    def on_release(self, event):
        if event.button is MouseButton.LEFT and self.selectedKnot is not None:  # and not self.moved:
            self.selectedKnot = None
            self.tooltip.set_visible(False)
            self.fig.canvas.draw_idle()

        self.press = False
        self.moved = False

    def on_motion(self, event):
        if event.button is MouseButton.LEFT \
                and self.press \
                and event.xdata \
                and event.ydata \
                and self.selectedKnot is not None:
            x = round(event.xdata, 1)
            self.knots[self.selectedKnot] = x

            text = "{}".format(x)
            self.tooltip.set_text(text)
            self.tooltip.xy = [x, 0]
            self.tooltip.set_visible(True)
            self.redraw()
            self.onUpdate(self.knots)

        self.moved = True

    def disconnect(self):
        """Disconnect all callbacks."""
        self.fig.canvas.mpl_disconnect(self.cidpress)
