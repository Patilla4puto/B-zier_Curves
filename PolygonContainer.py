from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np

class PolygonContainer:
    def __init__(self, ax, lineWidth = 1):
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
            #line = np.append(line,line[-1])
            #line.append(line[-1])  # last line segment has to be duplicated, otherwise it will not be drawn
            #print(line)
            path = Path(line, closed=False)
            patch = patches.PathPatch(path, facecolor='none', edgecolor=color, lw=self.lineWidth)
            self.patches.append(self.ax.add_patch(patch))
