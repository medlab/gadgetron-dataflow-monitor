"""
    Minimum PySide6 plus Matplotlib to digger Matplotlib related problem
"""

import os

os.environ['QT_API'] = 'pyside6'

import sys

from PySide6 import QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.canvas)

        self.ax = self.canvas.figure.subplots()
        self.ax2, =self.canvas.figure.get_axes()
        assert self.ax is self.ax2
        self.ax.plot([1, 2, 3], [1, 2, 3])

        self.addToolBar(NavigationToolbar(self.canvas, self))

def main():
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()

    app.show()
    app.activateWindow()

    app.raise_()

    qapp.exec_()


if __name__ == "__main__":
    main()

