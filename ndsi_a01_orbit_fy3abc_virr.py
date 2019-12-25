#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/23 14:11
# @Author  : AnNing
import os
import sys
import yaml
import warnings
import numpy as np
from lib.load_virr import ReadVirrL1
from lib.hdf5 import write_out_file
from lib.ndsi import ndsi
from lib import utils
from lib.plot import ndsi_plot_map
from config import *
from datetime import datetime

# !!!!   VALUE = 255 : Fill Data--no Data expected For pixel
# !!!!   VALUE = 254 : Saturated MODIS sensor detector
# !!!!   VALUE = 240 : NATIONAL OR PROVINCIAL BOUNDARIES
# !!!!   VALUE = 200 : Snow
# !!!!   VALUE = 100 : Snow-Covered Lake Ice
# !!!!   VALUE =  50 : Cloud Obscured
# !!!!   VALUE =  39 : Ocean
# !!!!   VALUE =  37 : Inland Water
# !!!!   VALUE =  25 : Land--no snow detected
# !!!!   VALUE =  11 : Darkness, terminator or polar
# !!!!   VALUE =   1 : No Decision
# !!!!   VALUE =   0 : Sensor Data Missing


class ReadInYaml:

    def __init__(self, in_file):
        """
        读取yaml格式配置文件
        """
        if not os.path.isfile(in_file):
            sys.exit(-1)

        with open(in_file, 'r') as stream:
            cfg = yaml.load(stream)

        self.jobname = cfg['INFO']['JOBNAME']
        self.ymd = cfg['INFO']['ymd']
        self.hms = cfg['INFO']['hms']

        self.ipath_l1b = cfg['PATH']['ipath_l1b']
        self.ipath_geo = cfg['PATH']['ipath_geo']
        self.ipath_clm = cfg['PATH']['ipath_clm']
        self.opath = cfg['PATH']['opath']


warnings.filterwarnings("ignore")


def nsdi_orbit_fy3abc_virr(job_name, l1_1000m, l1_cloudmask, l1_geo, yyyymmddhhmmss, out_dir):
    print("<<< function      : {}".format(utils.get_function_name()))
    print("<<< l1_1000m      : {}".format(l1_1000m))
    print("<<< l1_cloudmask  : {}".format(l1_cloudmask))
    print("<<< l1_geo        : {}".format(l1_geo))
    print("<<< yyyymmddhhmmss: {}".format(yyyymmddhhmmss))
    print("<<< out_dir       : {}".format(out_dir))

    data_loader = ReadVirrL1(l1_1000m, l1_geo, l1_cloudmask)
    ymd = data_loader.ymd
    hms = data_loader.hms
    i_datetime = datetime.strptime(ymd + hms, '%Y%m%d%H%M%S')
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
    ref_01 = refs.get('CH_01') * 100 / scale
    ref_02 = refs.get('CH_02') * 100 / scale
    ref_03 = refs.get('CH_07') * 100 / scale
    ref_04 = refs.get('CH_09') * 100 / scale
    ref_06 = refs.get('CH_06') * 100 / scale
    ref_07 = refs.get('CH_06') * 100 / scale
    ref_26 = refs.get('CH_10') * 100 / scale
    tbb_20 = tbbs.get('CH_03')
    tbb_31 = tbbs.get('CH_04')
    tbb_32 = tbbs.get('CH_05')

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
                                tbb_32=tbb_32, )

    # 写HDF5文件
    result = {'SNC': (ndsi_data, np.uint8),
              'Flag': (ndsi_flag, np.uint8),
              'Longitude': (longitude, np.float),
              'Latitude': (latitude, np.float)
              }

    out_filename = '{}_GBAL_L2_{}_{}_1000M_MS.HDF'.format(job_name, yyyymmddhhmmss[0:8], yyyymmddhhmmss[8:12])
    out_file = os.path.join(out_dir, out_filename)

    write_out_file(out_file, result, full_value=0)
    return {
        "data": {"out_file": [out_file],
                 "data": ndsi_data},
        "status": SUCCESS,
        "statusInfo": {
            "message": "完成",
            "detail": "结果目录:{}".format(out_dir)
        }
    }


def main(in_file):
    # 01 ICFG = 输入配置文件类 ##########
    in_cfg = ReadInYaml(in_file)

    job_name = in_cfg.jobname
    l1b_file = in_cfg.ipath_l1b
    clm_file = in_cfg.ipath_clm
    geo_file = in_cfg.ipath_geo
    ymdhms = in_cfg.ymd + in_cfg.hms
    outpath = in_cfg.opath
    print(l1b_file)
    print(clm_file)
    print(geo_file)
    result = nsdi_orbit_fy3abc_virr(job_name, l1b_file, clm_file, geo_file, ymdhms, outpath)
    if result["status"] == SUCCESS:
        ndsi_data = result["data"]["data"]
        filename = result["data"]["out_file"][0]
        out_img = filename + ".png"
        ndsi_plot_map(ndsi_data, out_img)


if __name__ == '__main__':

    # 获取python输入参数，进行处理
    args = sys.argv[1:]
    if len(args) == 1:  # 跟参数，则处理输入的时段数据
        IN_FILE = args[0]
    else:
        print('input args error exit')
        sys.exit(-1)
    main(IN_FILE)
