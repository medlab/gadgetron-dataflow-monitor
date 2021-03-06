A Gadgetron Dataflow Monitor

A Gadgetron debugger tools by Python with QT plus matplotlib, with love by Cong Zhang

[![Publish Python 🐍 distributions 📦 to PyPI and TestPyPI](https://github.com/medlab/gadgetron-dataflow-monitor/actions/workflows/python-publish.yml/badge.svg)](https://github.com/medlab/gadgetron-dataflow-monitor/actions/workflows/python-publish.yml)

# 你好

![](https://raw.githubusercontent.com/medlab/gadgetron-dataflow-monitor/main/你好.jpg)

![](https://raw.githubusercontent.com/medlab/gadgetron-dataflow-monitor/main/gadm_run_as_standalone_python.gif)

![](https://raw.githubusercontent.com/medlab/gadgetron-dataflow-monitor/main/gadm_start_as_gadget_by_gadgetron.gif)

![](https://raw.githubusercontent.com/medlab/gadgetron-dataflow-monitor/main/gadm_start_as_external_stream_handler.gif)

# Quick Start

## Server side

```bash
## --begin-- step just need when developing in loop, no need for end user after install 
cd src
## --end-- step just need when developing in loop, no need for end user after install 

gadgetron
```

## 1. Tester side(gadget start by gadgetron)

```bash
## --begin-- step just need when developing in loop, no need for end user after install 
cd src
## --end-- step just need when developing in loop, no need for end user after install 

gadgetron_ismrmrd_client -f gadm/test_datas/testdata.h5  -C gadm/use_in_gadgetron_sample/python_monitor_start_automate.xml
```

## 2. Tester side(gadget start by hand)

```bash
## --begin-- step just need when developing in loop, no need for end user after install 
cd src
export PYTHONPATH=$PWD 
## --end-- step just need when developing in loop, no need for end user after install 
python -m gadm.gadgetron_dataflow_monitor
```

```bash
## --begin-- step just need when developing in loop, no need for end user after install 
cd src
## --end-- step just need when developing in loop, no need for end user after install 

gadgetron_ismrmrd_client -f gadm/test_datas/testdata.h5  -C gadm/use_in_gadgetron_sample/python_monitor_start_automate.xml
```

## Internal

1. [Core]A QT+Matplotlib UI application to show data
2. Data Producer run in a standalone Thread to produce data and send to UI by trigger signal
3. The core Application can be use under three ways:
    1. As a start by hand external application which listen to gadgetron stream data
    2. Use as data process gadget which start by gadgetron
    3. Use as normal Python UI application which read data from ismrmrd file
    
# TODO

1. fix the speed problem of realtime update
2. fix the initial focus problem(can not receive key event unless user click on canvas)?
3. add a sample to read data from testdata and show directly? [done]
4. rename and publish to pypi, project structure may need to adjust [wip]
5. add a screen gif to demo how to use ( use peek software )
6. CD by github action 

# References

1. https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html
2. https://github.com/gadgetron/GadgetronOnlineClass/blob/master/Courses/Day1/Lecture2/visualization/visualization.py
3. https://github.com/matplotlib/matplotlib/pull/19255
4. https://github.com/anntzer/matplotlib/tree/qt6

# Warning

This depend on new released Python with Qt 6, and unpublished mathplotlib with QT6 support!

