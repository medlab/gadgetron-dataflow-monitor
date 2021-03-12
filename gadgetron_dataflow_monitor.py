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

from matplotlib.backend_bases import KeyEvent, MouseEvent, MouseButton

#pyplot.title()

import gadgetron

from gadgetron.external.connection import Connection

from multimethod import multimethod

from matplotlib.axes import Axes
#from matplotlib.axes._subplots import Axes



class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.figure=self.canvas.figure
        self.ax=self.figure.subplots() # type: Axes
        self.ax.axis('off')
        self.ax.set_title('Use LeftButton/RightButton/Double To Interactive')

        def onclick(event):
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                  ('double' if event.dblclick else 'single', event.button,
                   event.x, event.y, event.xdata, event.ydata))

        #cid1 = self.canvas.mpl_connect('key_release_event', self.on_key_press)

        cid2 = self.canvas.mpl_connect('button_press_event', self.on_click)

        layout.addWidget(self.canvas)

        self.nav_toolbar=NavigationToolbar(self.canvas, self)
        self.addToolBar(self.nav_toolbar)
        #?

        self.data_index=-1 # at the point befor start?
        self.received_datas=[]
        #TODO how about False
        self.pause=True


    def visualize(self, data, index):
        logging.info(rf'data type is {type(data)}, index is {index}')

        #self.ax.axis('off')
        self.ax.clear()
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

        # TODO force draw will very very slow!
        self.canvas.draw_idle() #?

        #self.canvas.draw()  # ? Deadlock here

        # t=self.canvas.new_timer(interval=0)
        # t.add_callback(self.canvas.draw)
        # t.single_shot=True
        # t.start()

    def on_data_index_changed(self, new_index):
        if( not new_index==self.data_index):
            logging.info(rf'index will be change from {self.data_index} to { new_index }')
            self.data_index=new_index

            self.visualize(self.received_datas[self.data_index], self.data_index)
        pass

    def on_key_press(self, event: KeyEvent):
        if(event.key=='p'):
            self.pause=not self.pause
            logging.info('[keyevent] pause')
        elif(event.key=='['):
            logging.info('[keyevent] move left')
            if self.data_index>0:
                self.on_data_index_changed(self.data_index-1)
        elif(event.key==']'):
            logging.info('[keyevent] move right')
            if self.data_index< len(self.received_datas)-1:
                self.on_data_index_changed(self.data_index+1)
        pass

    def on_click(self, event: MouseEvent):

        button=event.button # type: MouseButton
        logging.info(rf'you press {button} {button.name}, {type(event.button)}')

        if(event.dblclick==True):
            self.pause=not self.pause
            logging.info(rf'[mouse event]  double click to pause or unpause, current {self.pause}')
        elif(event.button==MouseButton.LEFT): # left button
            logging.info('[mouse event]  move left')
            if self.data_index>0:
                self.on_data_index_changed(self.data_index-1)
        elif(event.button==MouseButton.RIGHT): # right button
            logging.info('[mouse event]  move right')
            if self.data_index< len(self.received_datas)-1:
                self.on_data_index_changed(self.data_index+1)
        pass


    DrawNext=QtCore.Signal(object)


    def start_handle_data_flow(self, connection:Connection):
        logging.info("Connection established; visualizing.")
        #canvas=self.canvas

        #canvas.draw()  # ?

        '''
            1. data pull will in the worker thread
            2. drawer will in the ui thread
        '''
        #datas=queue.Queue()
        @QtCore.Slot(object)
        def draw_next_impl(data:object):
            #self.data_index=self.data_index+1
            #data=datas.get()
            #TODO fix next release
            #self.ax.clear()
            #default to turn off axis
            #self.ax.axis('off')

            #self.visualize(data, self.data_index)
            self.received_datas.append(data)

            if not self.pause:
                self.on_data_index_changed(len(self.received_datas)-1)
            #TODO rofce draw will very very slow!
            #self.canvas.draw_idle()

            #TODO should we care?
            #self.canvas.flush_events()
            pass

        self.DrawNext.connect(draw_next_impl,QtCore.Qt.QueuedConnection)

        def pull_data():
            for item in connection:
                #datas.put(item)
                self.DrawNext.emit(item)
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
        