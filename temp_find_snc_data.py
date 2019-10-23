#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/10/23 15:48
# @Author  : AnNing
import os
import h5py
import numpy as np

in_dir = '/FY3D/MERSI/L2L3/SNC/ORBIT/2019/20191022'
filenames = os.listdir(in_dir)

for filename in filenames:
    in_file = os.path.join(in_dir, filename)
    with h5py.File(in_file, 'r') as hdf:
        snc = hdf.get('SNC_SWATH')[:]
        index = np.where(snc == 200)
        if len(index[0]) > 0:
            print(len(index[0]))
            print(in_file)
