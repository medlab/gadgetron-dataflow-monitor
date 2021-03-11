"""
    Credit:
        Most of the basic idea from,
            1. https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html
            2. https://github.com/gadgetron/GadgetronOnlineClass/blob/master/Courses/Day1/Lecture2/visualization/visualization.py

    TODO:
        when to do figure.canvas.draw()?

"""

import logging
import multiprocessing
import os
import queue
from threading import Thread

import ismrmrd

os.environ['QT_API'] = 'pyside6'

import sys

import numpy as np

from PySide6 import QtCore, QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

#pyplot.title()

import gadgetron

from gadgetron.external.connection import Connection

from multimethod import multimethod

from matplotlib.axes._subplots import Axes



class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.figure=self.canvas.figure
        self.ax=self.figure.subplots() # type: Axes

        layout.addWidget(self.canvas)

        self.addToolBar(NavigationToolbar(self.canvas, self))

        self.data_index=0

    def visualize(self, data, index):
        logging.info(rf'data type is {type(data)}, index is {index}')
        
        if isinstance(data, ismrmrd.Acquisition):
            self.ax.title.set_text(f"Acquisition {index} [Magnitude; Channel 0]")
            self.ax.plot(np.abs(data.data[0, :]))
        elif isinstance(data, gadgetron.types.AcquisitionBucket):
            for acquisition in data.data:
                self.ax.plot(np.abs(acquisition.data[0, :]))
        elif isinstance(data, gadgetron.types.ReconData):
            data = data.bits[0].data.data
            self.ax.set_title(f"ReconData {index} [Magnitude; Channel 0]")
            self.ax.imshow(np.log(np.abs(np.squeeze(data[:, :, 0, 0]))))
        elif isinstance(data, gadgetron.types.ImageArray):
            
            self.ax.set_title(f"ImageArray {index}")
            self.ax.imshow(np.abs(np.squeeze(data.data)))
            pass
        elif isinstance(data, ismrmrd.Image):
            
            self.ax.set_title(f"Image {index}")
            self.ax.imshow(np.abs(np.squeeze(data.data)))
            pass
        else:
            print(rf'unknow type')
            pass

    @QtCore.Signal
    def DrawNext(self):
        pass

    def start_handle_data_flow(self, connection:Connection):
        logging.info("Connection established; visualizing.")
        #canvas=self.canvas

        #canvas.draw()  # ?

        '''
            1. data pull will in the worker thread
            2. drawer will in the ui thread
        '''
        datas=queue.Queue()

        @QtCore.Slot()
        def draw_next_impl():
            self.data_index=self.data_index+1
            data=datas.get()
            #TODO fix next release
            #self.ax.clear()
            #default to turn off axis
            self.ax.axis('off')

            self.visualize(data, self.data_index)

            #TODO rofce draw will very very slow!
            self.canvas.draw_idle()

            #TODO should we care?
            #self.canvas.flush_events()
            pass

        self.DrawNext.connect(draw_next_impl)

        def pull_data():
            for item in connection:
                datas.put(item)
                self.DrawNext.emit()
            pass

        Thread(target=pull_data).start() # TODO daemon?
        # how about connection.config
        # how about connection.header

        #connection.consume(draw_next)
        # app.exit()

        logging.info("finish install Visualization hook!")


def start_monitor(connection):
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()

    #canvas=app.canvas

    app.show()
    app.activateWindow()
    
    app.start_handle_data_flow(connection)
    app.raise_()

    qapp.exec_()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    def spawn_process(*args):
        child = multiprocessing.Process(target=start_monitor, args=args)
        child.start()

    while True:
        gadgetron.external.listen(18000, spawn_process)
        