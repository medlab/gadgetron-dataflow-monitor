A Gadgetron Dataflow Monitor

A Gadgetron debugger tools by Python with QT plus matplotlib, with love by Cong Zhang

# 你好

![](你好.jpg)

# Quick Start

## server side

```bash
#export PYTHONPATH=other_python_path_if_needed
gadgetron
```

## tester side

```bash
gadgetron_ismrmrd_client -f test_datas/testdata.h5  -C use_in_gadgetron_sample/python_monitor_start_automate.xml
```

# TODO

1. fix the speed problem of realtime update
2. fix the initial focus problem(can not receive key event unless user click on canvas)?
3. add a sample to read data from testdata and show directly?
4. prepare publish to pypi, project structure may need to adjust
5. CD by github action 

# References

1. https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html
2. https://github.com/gadgetron/GadgetronOnlineClass/blob/master/Courses/Day1/Lecture2/visualization/visualization.py
3. https://github.com/matplotlib/matplotlib/pull/19255
4. https://github.com/anntzer/matplotlib/tree/qt6

# Warning

This depend on new released Python with Qt 6, and unpublished mathplotlib with QT6 support!

