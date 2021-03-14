#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

depend_packages=[
       'PySide6',
       'matplotlib',
        'gadgetron',
]

setup(
    name='gadgetron-dataflow-monitor-CongZhang',
    version='0.90',
    description='Gadgetron Dataflow Monitor',
    long_description=open('readme.md').read(),
    install_requires=depend_packages,
    author='Cong Zhang',
    author_email='congzhangzh@gmail.com',
    maintainer='Cong Zhang',
    maintainer_email='congzhangzh@gmail.com',
    url='https://github.com/medlab/gadgetron-dataflow-monitor',
    packages=['gadm'],
    package_dir={'':'src'},
    package_data={'':['**/*.h5']},
    #data_files=['gadm/test_datas/testdata.h5'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)