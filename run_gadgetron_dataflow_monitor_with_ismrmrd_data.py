"""
idea test from a jupyter console application

import ismrmrd
from matplotlib import pyplot

ds=ismrmrd.Dataset('test_datas/testdata.h5')

ds.number_of_acquisitions()

a1=ds.read_acquisition(1)

a2=ds.read_acquisition(2)

pyplot.plot(a1.data[0,:])

pyplot.plot([1,2,3,4])

pyplot.show()

"""

import ismrmrd

import gadgetron_dataflow_monitor
from pathlib import Path
from PySide6 import QtCore

def main():
    test_data_path=Path(__file__).parent/'test_datas'/'testdata.h5'

    def pull_data(data_pulled_signal: QtCore.Signal(object)):
        ds=ismrmrd.Dataset(test_data_path)
        for index in range(ds.number_of_acquisitions()):
            one_line=ds.read_acquisition(index)
            data_pulled_signal.emit(one_line)
        pass

    gadgetron_dataflow_monitor.start_viewer(pull_data)
    pass

if __name__ == '__main__':
    main()