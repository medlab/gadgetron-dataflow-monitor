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
import sys
from pathlib import Path
import ismrmrd

from PySide6 import QtCore
from ismrmrd.xsd import ismrmrdHeader
from xsdata.formats.dataclass.parsers import XmlParser

from gadm import gadgetron_dataflow_monitor

def main(test_data_path):
    def pull_data(data_pulled_signal: QtCore.Signal(object)):
        ds=ismrmrd.Dataset(test_data_path)

        #get ismrmrdHeader object
        header_obj=ismrmrd.xsd.CreateFromDocument(ds.read_xml_header())

        # get user parameters collections
        params=header_obj.userParameters
        #get one collection(you have four collection, userParameterBase64/userParameterDouble/userParameterLong/userParameterString)
        if params!=None:
            long_params=params.userParameterLong
            #
            if long_params!=None:
                for long_param in long_params:
                    print(rf'key:{long_param.name}, value:{long_param.value}')
                    pass
            # ... some other collection

        for index in range(ds.number_of_acquisitions()):
            one_line=ds.read_acquisition(index)
            data_pulled_signal.emit(one_line)
        pass

    gadgetron_dataflow_monitor.start_viewer(pull_data)
    pass

if __name__ == '__main__':
    test_data_path=str(Path(__file__).parent/'test_datas'/'testdata.h5') if len(sys.argv)!=2 else sys.argv[1]
    main(test_data_path)