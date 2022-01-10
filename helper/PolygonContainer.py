from matplotlib.path import Path
import matplotlib.patches as patches


class PolygonContainer:
    """
    This class serves as a container to draw one or more lines on an matplotlib axis.
    The line list can be cleared and redrawn.
    """

    def __init__(self, ax, lineWidth=1):
        self.lineWidth = lineWidth
        self.ax = ax
        self.lines = []
        self.patches = []

    def clearLines(self):
        self.lines.clear()

    def addLine(self, line, color='black'):
        self.lines.append((line, color))

    def redraw(self):
        for p in self.patches:
            p.remove()
        self.patches.clear()

        for line, color in self.lines:
            path = Path(line, closed=False)
            patch = patches.PathPatch(path, facecolor='none', edgecolor=color, lw=self.lineWidth)
            self.patches.append(self.ax.add_patch(patch))
