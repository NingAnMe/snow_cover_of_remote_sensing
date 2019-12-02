#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2019/10/23 14:11
# @Author  : AnNing
import os
from datetime import datetime

import warnings

import numpy as np


from lib.load_mersi import ReadMersiL1
from lib.hdf5 import write_out_file
from lib.ndsi import ndsi
from .config import *

warnings.filterwarnings("ignore")


def nsdi_orbit_fy3d(l1_1000m, l1_cloudmask, l1_geo, yyyymmddhhmmss, out_dir):
    print("<<< l1_1000m      : {}".format(l1_1000m))
    print("<<< l1_cloudmask  : {}".format(l1_cloudmask))
    print("<<< l1_geo        : {}".format(l1_geo))
    print("<<< yyyymmddhhmmss: {}".format(yyyymmddhhmmss))
    print("<<< out_dir       : {}".format(out_dir))

    data_loader = ReadMersiL1(l1_1000m)
    ymd = data_loader.ymd
    hms = data_loader.hms
    i_datetime = datetime.strptime(ymd+hms, '%Y%m%d%H%M%S')
    longitude = data_loader.get_longitude()
    latitude = data_loader.get_latitude()
    dems = data_loader.get_height()
    sea_land_mask = data_loader.get_land_sea_mask()
    cloud_mask = data_loader.get_cloudmask()

    # 日地距离校正
    refs = data_loader.get_ref()
    tbbs = data_loader.get_tbb()
    sensor_zenith = data_loader.get_sensor_zenith()
    sensor_azimuth = data_loader.get_sensor_zenith()
    solar_zenith = data_loader.get_solar_zenith()
    solar_azimuth = data_loader.get_solar_azimuth()

    index = solar_zenith < 87
    scale = np.ones((2000, 2048))
    scale[index] = np.cos(np.deg2rad(solar_zenith[index]))
    ref_01 = refs.get('CH_03') * 100 / scale
    ref_02 = refs.get('CH_04') * 100 / scale
    ref_03 = refs.get('CH_01') * 100 / scale
    ref_04 = refs.get('CH_02') * 100 / scale
    ref_06 = refs.get('CH_06') * 100 / scale
    ref_07 = refs.get('CH_07') * 100 / scale
    ref_26 = refs.get('CH_19') * 100 / scale
    tbb_20 = tbbs.get('CH_20')
    tbb_31 = tbbs.get('CH_24')
    tbb_32 = tbbs.get('CH_25')

    ndsi_data, ndsi_flag = ndsi(i_datetime=i_datetime,
                                longitude=longitude,
                                latitude=latitude,
                                sensor_zenith=sensor_zenith,
                                sensor_azimuth=sensor_azimuth,
                                solar_zenith=solar_zenith,
                                solar_azimuth=solar_azimuth,
                                dems=dems,
                                sea_land_mask=sea_land_mask,
                                cloud_mask=cloud_mask,
                                ref_01=ref_01,
                                ref_02=ref_02,
                                ref_03=ref_03,
                                ref_04=ref_04,
                                ref_06=ref_06,
                                ref_07=ref_07,
                                ref_26=ref_26,
                                tbb_20=tbb_20,
                                tbb_31=tbb_31,
                                tbb_32=tbb_32,)

    # 写HDF5文件
    result = {'SNC': (ndsi_data, np.uint8),
              'Flag': (ndsi_flag, np.uint8),
              }

    out_filename = 'FY3D_MERSI_GBAL_L2_{}_{}_1000M_MS.HDF'.format(yyyymmddhhmmss[:0:8], yyyymmddhhmmss[8:12])
    out_file = os.path.join(out_dir, out_filename)

    write_out_file(out_file, result, full_value=0)
    return {
                "data": {"out_file": [out_file]},
                "status": SUCCESS,
                "statusInfo": {
                    "message": "完成",
                    "detail": "结果目录:{}".format(out_dir)
                }
            }
