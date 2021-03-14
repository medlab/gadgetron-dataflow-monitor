"""
    Credit:
        Most of the basic idea from,
            1. https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html
            2. https://github.com/gadgetron/GadgetronOnlineClass/blob/master/Courses/Day1/Lecture2/visualization/visualization.py

    TODO:
        when to do figure.canvas.draw()?

"""

import typing
import logging
import multiprocessing
import os
import queue
from threading import Thread

import ismrmrd

os.environ['QT_API'] = 'pyside6'

import sys

print(rf'''
python is run by {sys.executable}
''')

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

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.canvas = FigureCanvas(Figure(figsize=(6,4)))

        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        #TODO not work here!
        #self.canvas.setFocus()

        self.figure=self.canvas.figure
        self.ax=self.figure.subplots() # type: Axes
        self.ax.axis('off')
        self.ax.set_title('Use Left/Right/Double or ← ↑ → ↓ ([bug]click first) To Interactive')

        def onclick(event):
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                  ('double' if event.dblclick else 'single', event.button,
                   event.x, event.y, event.xdata, event.ydata))

        cid1 = self.canvas.mpl_connect('key_release_event', self.on_key_press)

        cid2 = self.canvas.mpl_connect('button_press_event', self.on_click)

        layout.addWidget(self.canvas)

        self.nav_toolbar=NavigationToolbar(self.canvas, self)
        self.addToolBar(self.nav_toolbar)
        #?

        self.data_index=-1 # at the point befor start?
        self.channel_index=0
        self.received_datas=[]
        #TODO how about False
        self.pause=True


    def visualize(self, data, index, channel):
        logging.info(rf'data type is {type(data)}, index is {index}, channel is {channel}')

        #self.ax.axis('off')
        self.ax.clear()
        if isinstance(data, ismrmrd.Acquisition):
            self.ax.title.set_text(f"Acquisition {index} [Magnitude; Channel {channel}]")
            self.ax.plot(np.abs(data.data[channel, :]))
        elif isinstance(data, gadgetron.types.AcquisitionBucket):
            for acquisition in data.data:
                self.ax.plot(np.abs(acquisition.data[0, :]))
        elif isinstance(data, gadgetron.types.ReconData):
            data = data.bits[0].data.data
            self.ax.set_title(f"ReconData {index} [Magnitude; Channel {channel}]")
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

    def on_data_index_changed(self, new_index, new_channel_index):
        if not (new_index==self.data_index and new_channel_index==self.channel_index):
            logging.info(rf'''
            index will be change from {self.data_index} to { new_index }, 
            channel from {self.channel_index} to {new_channel_index}''')
            self.data_index=new_index
            self.channel_index=new_channel_index
            self.visualize(self.received_datas[self.data_index], self.data_index,new_channel_index)
        pass

    def on_key_press(self, event: KeyEvent):
        logging.info(rf'the key press event {event}')
        if(event.key=='space'):
            self.switch_pause()
            logging.info('[keyevent] pause')
        elif(event.key=='lelt'):
            logging.info('[keyevent] move left')
            self.show_old_data()
        elif(event.key=='right'):
            logging.info('[keyevent] move right')
            self.show_newer_data()
        elif(event.key=='up'):
            logging.info('[keyevent] move up')
            self.show_upper_channel_data()
            pass
        elif(event.key=='down'):
            logging.info('[keyevent] move down')
            self.show_lower_channel_data()
            pass
        pass

    def show_old_data(self):
        if self.data_index > 0:
            self.on_data_index_changed(self.data_index - 1, 0)

    def on_click(self, event: MouseEvent):

        button=event.button # type: MouseButton
        logging.info(rf'you press {button} {button.name}, {type(event.button)}')

        if(event.dblclick==True):
            self.switch_pause()
            logging.info(rf'[mouse event]  double click to pause or unpause, current {self.pause}')
        elif(event.button==MouseButton.LEFT): # left button
            logging.info('[mouse event]  move left')
            self.show_old_data()
        elif(event.button==MouseButton.RIGHT): # right button
            logging.info('[mouse event]  move right')
            self.show_newer_data()
        pass

    def show_newer_data(self):
        if self.data_index < len(self.received_datas) - 1:
            self.on_data_index_changed(self.data_index + 1,0)

    def show_lower_channel_data(self):
        if 0<=self.data_index< len(self.received_datas):
            data=self.received_datas[self.data_index] # type: ismrmrd.Acquisition
            if(isinstance(data, ismrmrd.Acquisition)):
                new_channel_index=self.channel_index-1
                if new_channel_index>=0:
                    #self.channel_index=self.channel_index+1
                    self.on_data_index_changed(self.data_index, new_channel_index)
        pass

    def show_upper_channel_data(self):
        if 0<=self.data_index< len(self.received_datas):
            data=self.received_datas[self.data_index] # type: ismrmrd.Acquisition
            if(isinstance(data, ismrmrd.Acquisition)):
                new_channel_index=self.channel_index+1
                if new_channel_index<data.data.shape[0]:
                    #self.channel_index=self.channel_index+1
                    self.on_data_index_changed(self.data_index, new_channel_index)
        pass

    def switch_pause(self):
        self.pause = not self.pause

    DrawNext=QtCore.Signal(object)


    def start_handle_data_flow(self, pull_data_work:typing.Callable[QtCore.Signal(object), None]):
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

        #TODO this does not solve the problem, which is slow!!! the real slow source maybe the canvas draw?

        self.DrawNext.connect(draw_next_impl,QtCore.Qt.QueuedConnection)

        # def pull_data():
        #     for item in connection:
        #         #datas.put(item)
        #         self.DrawNext.emit(item)
        #     pass

        Thread(target=pull_data_work,args=(self.DrawNext,), daemon=True).start() # TODO daemon?
        # how about connection.config
        # how about connection.header

        #connection.consume(draw_next)
        # app.exit()

        logging.info("finish install Visualization hook!")


def start_monitor(connection):
    def pull_data(data_pulled_signal:QtCore.Signal(object)):
        for item in connection:
            # datas.put(item)
            data_pulled_signal.emit(item)
        pass
    start_viewer(pull_data)
    pass

def start_viewer(pull_data_work:typing.Callable[QtCore.Signal(object), None]):
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()

    #canvas=app.canvas

    app.show()
    app.activateWindow()
    
    app.start_handle_data_flow(pull_data_work)
    app.raise_()

    qapp.exec_()

def EmptyPythonGadget(connection):
    try:
        index=0
        for item in connection:
            acq=item # type: ismrmrd.Acquisition
            print(rf'acq index {index}')
            index=index+1
    except:
        pass
    pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    def spawn_process(*args):
        child = multiprocessing.Process(target=start_monitor, args=args)
        child.start()

    while True:
        gadgetron.external.listen(18000, spawn_process)
        