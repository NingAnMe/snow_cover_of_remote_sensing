#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/5/8
@Author  : AnNing
"""
import h5py


class LoadH8Ndvi:
    def __init__(self, in_file, res=2000):
        self.in_file = in_file
        self.res = res

    def get_ndvi(self):
        with h5py.File(self.in_file, 'r') as h5r:
            name = 'NDVI'
            dataset = h5r.get(name)
            data = dataset[:]
            return data

    def get_flag(self):
        with h5py.File(self.in_file, 'r') as h5r:
            name = 'Flag'
            dataset = h5r.get(name)
            data = dataset[:]
            return data
