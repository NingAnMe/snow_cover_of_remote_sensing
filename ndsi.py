#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/5/15
@Author  : AnNing
"""
from __future__ import print_function

import os
import sys

import numpy as np

from initialize import load_yaml_file
from load import ReadAhiL1


TEST = True


def ndsi():

    # -------------------------------------------------------------------------
    # SolarZenith_MAX : MAXIMUM SOLAR ZENITH ANGLE, *1.0 DEGREE
    solar_zenith_max = None

    # -------------------------------------------------------------------------
    # Date and Time
    i_year = None
    i_month = None
    i_day = None
    i_minute = None
    n_year = None
    n_month = None
    n_day = None
    n_hour = None
    n_minute = None
    n_second = None

    # -------------------------------------------------------------------------
    # out data
    r4_rt = np.array([])
    r4_info = np.array([])
    i2_cm = np.array([])
    r4_test = np.array([])

    # -------------------------------------------------------------------------
    # swath sum
    i_swath_valid = None
    i_sum_valid = None

    # -------------------------------------------------------------------------
    dim_x = None
    dim_y = None
    dim_z = None

    # -------------------------------------------------------------------------
    r_lats = None  # LATITUDE
    r_lons = None  # LONGITUDE
    a_satz = None  # SATELLITE ZENITH ANGLE
    a_sata = None  # SATELLITE AZIMUTH
    a_sunz = None  # SOLAR ZENITH ANGLE
    a_suna = None  # SOLAR AZIMUTH
    r_dems = None  # DEM MASK
    i_mask = None  # LANDCOVER MASK
    i_cm = None  # Cloud MASK

    # -------------------------------------------------------------------------
    cossl = None  # SOLAR-ZENITH-ANGLE-COSINE
    glint = None  # SUN GLINT
    lsm = None  # Mask For Water & Land
    i_avalible = None  # Mask For Data to be used

    # -------------------------------------------------------------------------
    ref_01 = None  # 0.645 um : Ref, NDVI
    ref_02 = None  # 0.865 um : Ref, NDVI
    ref_03 = None  # 0.470 um : Ref, NDVI
    ref_04 = None  # 0.555 um : Ref, NDVI
    ref_05 = None  # 1.640 um : Ref, NDVI
    ref_06 = None  # 1.640 um : Ref, NDSI
    ref_07 = None  # 2.130 um : Ref, NDSI
    ref_19 = None  # 0.940 um : Ref, Vapour
    ref_26 = None  # 1.375 um : Ref, Cirrus
    tbb_20 = None  # 3.750 um : TBB, Temperature
    tbb_31 = None  # 11.030 um : TBB, Temperature
    tbb_32 = None  # 12.020 um : TBB, Temperature

    # -------------------------------------------------------------------------
    ndvis = None  # R2-R1/R2+R1: R0.86,R0.65
    ndsi_6 = None  # R4-R6/R4+R6: R0.55,R1.64
    ndsi_7 = None  # R4-R7/R4+R7: R0.55,R2.13

    dr_16 = None  # R1-R6:       R0.86,R1.64
    dr_17 = None  # R1-0.5*R7:   R0.86,R2.13

    dt_01 = None  # T20-T31:     T3.75-T11.0
    dt_02 = None  # T20-T32:     T3.75-T12.0
    dt_12 = None  # T31-T32:     T11.0-T12.0

    rr_21 = None  # R2/R1:       R0.86,R0.65
    rr_46 = None  # R4/R6:       R0.55,R1.64
    rr_47 = None  # R4/R7:       R0.55,R2.13

    dt_34 = None  # T20-T23:     T3.75-T4.05
    dt_81 = None  # T29-T31:     T8.55-T11.0
    dt_38 = None  # T20-T29:     T3.75-T8.55

    # -------------------------------------------------------------------------
    # Used for Masking Over-Estimation for snow by monthly snow pack lines.
    # LookUpTable For Monthly CHN-SnowPackLine (ZhengZJ, 2006)
    # Line:   Longitude from 65.0 to 145.0 (Step is 0.1 deg.)
    # Column: Month from Jan to Dec (Step is month)
    # Value:  Latitude (Unit is deg.)
    r_mon_snow_line = np.array([])  # Monthly CHN-SnowPackLine

    # Used for judging low or water cloud by BT difference.
    # LookUpTable For T11-T12 (Saunders and Kriebel, 1988)
    # Line:   T11 from 250.0K to 310.0K (Step is 1.0K)
    # Column: Secant-SZA from 1.00 to 2.50 (Step is 0.01)
    # Value:  T11-T12 (Unit is K)
    delta_bt_lut = np.array([])  # LookUpTable for BT11-BT12

    # Used for judging snow in forest by NDSI and NDVI.
    # LookUpTable For Snow in Forest , by NDVI-NDSI (Klein et al., 1998)
    # Line:   NDVI from 0.010 to 1.000 (Step is 0.01)
    # Column: NDSI from 0.01000 to 1.00000 (Step is 0.00001)
    # Value:  NDSI (Unit is null)
    delta_bt_lut = np.array([])  # LookUpTable for NDSI-NDVI

    # !!!!! Four Variables below should be USED TOGETHER.
    # !! R138R164LUT,R164T11_LUT,R164R138LUT,T11mT12R164LUT
    # !!   LookUpTable For FreshSnow&WaterIceCloud (ZhengZJ, 2006)
    # !!     (1)Line-R164T11_LUT:      T11 from 225.0 to 280.0 (Step is 0.1K)
    # !!        Column--R164T11_LUT:   R164 from 0.00000 to 0.24000 (No Step)
    # !!     (2)Line-T11mT12R164LUT:   R164 from 0.100 to 0.250 (Step is 0.001)
    # !!        Column-T11mT12R164LUT: T11mT12 from -40 to 130 (No Step)
    # !!     (3)Line-R138R164LUT:      R164 from 0.010 to 0.260 (Step is 0.001)
    # !!        Column-R138R164LUT:    R138 from 0.0020 to 0.3000 (No Step)
    # !!     (4)Line-R164R138LUT:      R138 from 0.000 to 0.550 (Step is 0.001)
    # !!        Column-R164R138LUT:    R164 from 0.1500 to 0.3000 (No Step)
    y_r164xt11 = np.array([])  # LookUpTable For R164T11
    y_t11mt12xr164 = np.array([])  # LookUpTable For T11mT12R164
    y_r138xr164 = np.array([])  # LookUpTable For R138R164
    y_r164xr138 = np.array([])  # LookUpTable For R164R138

    # -------------------------------------------------------------------------
    # Used for Referrence of 11um Minimum Brightness Temperature.
    ref_bt11um = None
    ref_bt11um_slope_n = None
    ref_bt11um_slope_s = None
    ref_bt11um_offset_n = None
    ref_bt11um_offset_s = None

    a_low_t_lat = None  # Referential Latitude for BT11 LowThreshold
    a_low_bt11 = None  # Referential Temp for BT11 LowThreshold
    delta_t_low = None  # Referential Temporal Delta-Temp for BT11_Low
    b_hai_t_lat = None  # Referential Latitude for BT11 HaiThreshold
    b_hai_bt11 = None  # Referential Temp for BT11 HaiThreshold
    delta_t_hai = None  # Referential Temporal Delta-Temp for BT11_Hai

    a_low_bt11_n = None
    a_low_bt11_s = None
    b_hai_bt11_n = None
    b_hai_bt11_s = None

    # -------------------------------------------------------------------------
    # Used for Calculate and Store Xun number from 1 to 36 in a year.
    f_xun_n = None
    f_xun_s = None
    i2_xun_num = None

    # -------------------------------------------------------------------------
    i_step = np.array([])  # TEST-STEP
    i_mark = np.array([])  # SNOW MAP
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

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    print('Program : Make SNC')

    # -------------------------------------------------------------------------
    name_list_swath_snc = 'cfg.yaml'
    print('Config file : {}'.format(name_list_swath_snc))

    a = load_yaml_file(name_list_swath_snc)
    solar_zenith_max = float(a['SolarZenith_MAX'])
    inn_put_para_path = a['InnPut_ParaPath']

    inn_put_root_bmp = a['InnPut_Root_Bmp']
    inn_put_root_l01 = a['InnPut_Root_L01']
    inn_put_root_l02 = a['InnPut_Root_L02']
    inn_put_root_l03 = a['InnPut_Root_L03']
    inn_put_root_l11 = a['InnPut_Root_L11']
    inn_put_root_l12 = a['InnPut_Root_L12']
    inn_put_root_l13 = a['InnPut_Root_L13']
    inn_put_root_l14 = a['InnPut_Root_L14']

    # -------------------------------------------------------------------------
    # Set Date Information
    year_min = 2000
    year_max = 2048
    month_min = 1
    month_max = 12
    date_min = 1
    data_max = 31
    hour_min = 0
    hour_max = 23

    in_file_h8 = r'D:\KunYu\hangzhou_anning\H8_L1\AHI8_OBI_2000M_NOM_20190426_2200.hdf'
    read_ahi = ReadAhiL1(in_file_h8)
    ymd = read_ahi.ymd
    hms = read_ahi.hms
    j_year = int(ymd[0:4])
    j_month = int(ymd[4:6])
    j_date = int(ymd[6:8])
    j_hour = int(hms[0:2])

    if (not year_min <= j_year <= year_max) or (not month_min <= j_month <= month_max) or \
            (not date_min <= j_date <= data_max) or (not hour_min <= j_hour <= hour_max):
        raise ValueError('Wrongly Time Setting. Please Retry ......')

    # -------------------------------------------------------------------------
    # Calculating the Number of Xun (means ten day).
    if j_date <= 10:
        i2_xun_num = 3 * (j_month - 1) + 1
    elif j_date > 20:
        i2_xun_num = 3 * (j_month - 1) + 3
    else:
        i2_xun_num = 3 * (j_month - 1) + 2

    if i2_xun_num == 21:
        f_xun_n = 0.
    elif i2_xun_num < 21:
        f_xun_n = np.abs(np.sin(np.pi * (i2_xun_num - 21 + 36) / 36))
    else:
        f_xun_n = np.abs(np.sin(np.pi * (i2_xun_num - 21) / 36))

    f_xun_s = np.sqrt(1.0 - f_xun_n ** 2)

    if TEST:
        print(' f_xun_n= ', f_xun_n, ' f_xun_s= ', f_xun_s)

    # -------------------------------------------------------------------------
    # Calculate Parameters (Slope & Offset) for Ref_BT11um
    a_low_t_lat = 57.
    a_low_bt11 = 243.
    delta_t_low = 15.
    b_hai_t_lat = 17.
    b_hai_bt11 = 270.
    delta_t_hai = 10.

    a_low_bt11_n = a_low_bt11 - f_xun_n * delta_t_low
    a_low_bt11_s = a_low_bt11 - f_xun_s * delta_t_low

    b_hai_bt11_n = b_hai_bt11 - f_xun_n * delta_t_hai
    b_hai_bt11_s = b_hai_bt11 - f_xun_s * delta_t_hai

    if TEST:
        print(' a_low_bt11= ', a_low_bt11,' b_hai_bt11= ', b_hai_bt11)
        print(' a_low_bt11_n= ', a_low_bt11_n,' a_low_bt11_s= ', a_low_bt11_s)
        print(' b_hai_bt11_n= ', b_hai_bt11_n, ' b_hai_bt11_s= ', b_hai_bt11_s)

    ref_bt11um_slope_n = (b_hai_bt11_n - a_low_bt11_n) / (b_hai_t_lat - a_low_t_lat)
    ref_bt11um_slope_s = (b_hai_bt11_s - a_low_bt11_s) / (b_hai_t_lat - a_low_t_lat)

    ref_bt11um_offset_n = a_low_bt11_n - ref_bt11um_slope_n * a_low_t_lat
    ref_bt11um_offset_s = a_low_bt11_s - ref_bt11um_slope_s * a_low_t_lat

    if TEST:
        print('ref_bt11um_slope_n', ref_bt11um_slope_n)
        print('ref_bt11um_slope_s', ref_bt11um_slope_s)
        print('ref_bt11um_offset_n', ref_bt11um_offset_n)
        print('ref_bt11um_offset_s', ref_bt11um_offset_s)

    # -------------------------------------------------------------------------
    # load row and col
    data_shape = read_ahi.data_shape
    i_rows, i_cols = data_shape

    # -------------------------------------------------------------------------
    # Check Swath_Valid by Solar Zenith
    data_solar_zenith = read_ahi.get_solar_zenith()
    i_sum_valid = np.logical_and(data_solar_zenith > 0, data_solar_zenith < solar_zenith_max).sum()
    if i_sum_valid > i_cols * 30:
        i_swath_valid = 1
    else:
        raise ValueError('Valid data is not enough.')

    # -------------------------------------------------------------------------
    # Read  FILE_GEO

    #  GET SensorZenith
    data_sensor_zenith = read_ahi.get_sensor_zenith()
    index_valid = np.logical_and(data_sensor_zenith > 0, data_sensor_zenith < 90)
    data_sensor_zenith[index_valid] = data_sensor_zenith[index_valid] / 180 * np.pi
    data_sensor_zenith[~index_valid] = 8.0
    a_satz = data_sensor_zenith

    #  GET SensorAzimuth
    data_sensor_azimuth = read_ahi.get_sensor_azimuth()
    index_valid = np.logical_and(data_sensor_azimuth > -360, data_sensor_azimuth < 360)
    data_sensor_azimuth[index_valid] = data_sensor_azimuth[index_valid] / 180 * np.pi
    data_sensor_azimuth[~index_valid] = 8.0
    a_sata = data_sensor_azimuth

    #  GET SolarZenith
    data_solar_zenith = read_ahi.get_solar_zenith()
    index_valid = np.logical_and(data_solar_zenith > -360, data_solar_zenith < 360)
    data_solar_zenith[index_valid] = data_solar_zenith[index_valid] / 180 * np.pi
    data_solar_zenith[~index_valid] = 8.0
    a_sunz = data_solar_zenith

    #  GET SolarAzimuth
    data_solar_azimuth = read_ahi.get_solar_azimuth()
    index_valid = np.logical_and(data_solar_azimuth > -360, data_solar_azimuth < 360)
    data_solar_azimuth[index_valid] = data_solar_azimuth[index_valid] / 180 * np.pi
    data_solar_azimuth[~index_valid] = 8.0
    a_suna = data_solar_azimuth

    #  GET LATITUDE
    r_lats = read_ahi.get_latitude()

    #  GET LONGITUDE
    r_lons = read_ahi.get_longitude()

    #  GET Elevation
    r_dems = read_ahi.get_height()

    #  GET LandSea
    i_mask = read_ahi.get_land_sea_mask()

    # -------------------------------------------------------------------------
    # Read  FILE_CM

    # GET Cloud Mask
    i_cm = read_ahi.get_cloudmask()

    # -------------------------------------------------------------------------
    # Read  FILE_2KM

    # COMPUTE The CORRECTED REFLECTANCE OF BANDs used
    cossl = 1.0
    ref_01 = read_ahi.get_channel_data('VIS0064') * cossl
    ref_02 = read_ahi.get_channel_data('VIS0086') * cossl
    ref_03 = read_ahi.get_channel_data('VIS0046') * cossl
    ref_04 = read_ahi.get_channel_data('VIS0051') * cossl
    ref_06 = read_ahi.get_channel_data('VIS0160') * cossl
    ref_07 = read_ahi.get_channel_data('VIS0230') * cossl
    # ref_26 = read_ahi.get_channel_data('No') * cossl  # 不能做卷积云的判断

    ref_01[ref_01 < 0] = 0.
    ref_02[ref_01 < 0] = 0.
    ref_03[ref_01 < 0] = 0.
    ref_04[ref_01 < 0] = 0.
    ref_06[ref_01 < 0] = 0.
    ref_07[ref_01 < 0] = 0.

    # COMPUTE The CORRECTED REFLECTANCE OF BANDs used
    tbb_20 = read_ahi.get_channel_data('IRX0390')
    tbb_31 = read_ahi.get_channel_data('IRX1120')
    tbb_32 = read_ahi.get_channel_data('IRX1230')

    # -------------------------------------------------------------------------
    # COMPUTE The SUN GLINT EAGLE
    glint = np.full(data_shape, 8., dtype=np.float16)
    index = np.logical_and.reduce((np.abs(a_sunz - 8) < 0.0001, np.abs(a_satz - 8) < 0.0001,
                                   np.abs(a_suna - 8) < 0.0001, np.abs(a_sata - 8) < 0.0001))
    temp = np.sin(a_sunz) * np.sin(a_satz) * np.cos(a_suna - a_sata) + \
        np.cos(a_sunz) * np.cos(a_satz)
    temp[temp > 1] = 1
    temp[temp < -1] = -1
    glint[~index] = np.arccos(temp)[~index]

    # -------------------------------------------------------------------------
    # COMPUTE The SUN GLINT EAGLE
    ref_lon = r_lons
    ref_lat = r_lats

    ref_bt11um = np.full(data_shape, np.nan)

    index = np.logical_and(ref_lat >= 0, np.abs(ref_lat) < b_hai_t_lat)
    ref_bt11um[index] = ref_bt11um_slope_n * np.abs(b_hai_t_lat) + ref_bt11um_offset_n

    index = np.logical_and(ref_lat >= 0, np.abs(ref_lat) > a_low_t_lat)
    ref_bt11um[index] = ref_bt11um_slope_n * np.abs(a_low_t_lat) + ref_bt11um_offset_n

    index = np.logical_and.reduce((ref_lat >= 0, np.abs(ref_lat) >= b_hai_t_lat, np.abs(ref_lat) <= a_low_t_lat))
    ref_bt11um[index] = ref_bt11um_slope_n * np.abs(ref_lat) + ref_bt11um_offset_n

    index = np.logical_and(ref_lat < 0, np.abs(ref_lat) < b_hai_t_lat)
    ref_bt11um[index] = ref_bt11um_slope_s * np.abs(b_hai_t_lat) + ref_bt11um_offset_s

    index = np.logical_and(ref_lat < 0, np.abs(ref_lat) > a_low_t_lat)
    ref_bt11um[index] = ref_bt11um_slope_s * np.abs(a_low_t_lat) + ref_bt11um_offset_s

    index = np.logical_and.reduce((ref_lat < 0, np.abs(ref_lat) >= b_hai_t_lat, np.abs(ref_lat) <= a_low_t_lat))
    ref_bt11um[index] = ref_bt11um_slope_s * np.abs(ref_lat) + ref_bt11um_offset_s

    # -------------------------------------------------------------------------
    #  INITIALIZATION
    i_mark = np.zeros(data_shape)
    i_step = np.zeros(data_shape)
    i_avalible = np.ones(data_shape)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!   QUALITY CONTROLLING   !!!!!!!!!!!!!!!!!!!!!!!!!!!
    #           iAvalible=1     !!  iAvalible=0(1): Data IS(NOT) USABLE.  !!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!   QUALITY CONTROLLING   !!!!!!!!!!!!!!!!!!!!!!!!!!!

    # # SATURATION AFTER SOLAR ZENITH ANGLE CORRECTING.
    # index = np.logical_or.reduce((ref_01 > 100,
    #                               ref_02 > 100,
    #                               ref_03 > 100,
    #                               ref_04 > 100,
    #                               ref_06 > 100,
    #                               ref_07 > 100))
    # i_mark[index] = 254
    # i_step[index] = 2
    # i_avalible[index] = 0

    # CORRECT SATURATION VALUE AFTER SOLAR ZENITH ANGLE CORRECTING.
    ref_01[ref_01 > 100] = 100
    ref_02[ref_02 > 100] = 100
    ref_03[ref_03 > 100] = 100
    ref_04[ref_04 > 100] = 100
    ref_06[ref_06 > 100] = 100
    ref_07[ref_07 > 100] = 100

    # ref_26[ref_26 > 100] = 100
    # ref_26[ref_26 < 0.001] = 0.001

    # The SOLAR ZENITH ANGLE EXCEEDS MAXIMUM DEG THRESHOLD.
    index = np.abs(a_sunz - 8) < 0.0001
    i_mark[index] = 11
    i_step[index] = 3
    i_avalible[index] = 0

    # The Sensor ZENITH ANGLE EXCEEDS MAXIMUM DEG THRESHOLD.
    index = np.abs(a_satz - 8) < 0.0001
    i_mark[index] = 11
    i_step[index] = 4
    i_avalible[index] = 0

    # The SUN GLINT ANGLE EXCEEDS MAXIMUM DEG THRESHOLD.
    index = glint <= (15 * np.pi / 180)
    i_mark[index] = 240
    i_step[index] = 5
    i_avalible[index] = 0

    # Check status of Observation Angles.
    index = np.logical_or.reduce((r_lons < -180, r_lons > 180, r_lats < -90, r_lats > 90))
    i_mark[index] = 0
    i_step[index] = 6
    i_avalible[index] = 0

    # Check status of Location information.
    index = np.logical_or.reduce((np.abs(a_sunz - 8) < 0.001, np.abs(a_satz - 8) < 0.001,
                                  np.abs(a_suna - 8) < 0.001, np.abs(a_sata - 8) < 0.001,))
    i_mark[index] = 0
    i_step[index] = 7
    i_avalible[index] = 0

    # CHECK The Data QUALITY (ALL BANDS).
    index = np.logical_or.reduce((ref_01 <= 0.001, ref_01 >= 100.001,
                                  ref_02 <= 0.001, ref_02 >= 100.001,
                                  ref_03 <= 0.001, ref_03 >= 100.001,
                                  ref_04 <= 0.001, ref_04 >= 100.001,
                                  ref_06 <= 0.001, ref_06 >= 100.001,
                                  ref_07 <= 0.001, ref_07 >= 100.001,
                                  tbb_20 <= 170.0, tbb_20 >= 350.001,
                                  tbb_31 <= 170.0, tbb_31 >= 340.001,
                                  tbb_32 <= 170.0, tbb_32 >= 340.001,))
    i_mark[index] = 255
    i_step[index] = 8
    i_avalible[index] = 0

    # -------------------------------------------------------------------------
    # MAKE SEA-LAND MASK
    # !!!!   NATIONAL OR PROVINCIAL BOUNDARIES.
    #
    # !!!!!!!!!!!!!!!!!!  LSM=0(1): Data IS ON WATER-BODY(LAND).  !!!!!!!!!!!!!!!!!!
    # c. !  iMASK = 0:  SHALLOW_OCEAN         !
    # c. !  iMASK = 1:  LAND                  !
    # c. !  iMASK = 2:  COASTLINE             !
    # c. !  iMASK = 3:  SHALLOW_INLAND_WATER  !
    # c. !  iMASK = 4:  EPHEMERAL_WATER       !
    # c. !  iMASK = 5:  DEEP_INLAND_WATER     !
    # c. !  iMASK = 6:  MODERATE_OCEAN        !
    # c. !  iMASK = 7:  DEEP_OCEAN            !
    land_condition = np.logical_or.reduce((i_mask == 1, i_mask == 2, i_mask == 3))
    sea_condition = np.logical_or(i_mask == 0, np.logical_and(i_mask > 3, i_mask < 8))
    lsm = np.full(data_shape, np.nan)
    lsm[land_condition] = 1
    lsm[sea_condition] = 0

    # -------------------------------------------------------------------------
    # JUDGE & MARK  SNOW
    # !!!    iTAG For marking The case of Data
    # !!!!---- Notice ----!!!!    0: badData; 1: goodData unused; 2: goodData used.
    i_tag = np.zeros(data_shape)
    index = i_avalible == 1
    ndvis = (ref_02 - ref_01) / (ref_02 + ref_01)
    ndsi_6 = (ref_04 - ref_06) / (ref_04 + ref_06)
    ndsi_7 = (ref_04 - ref_07) / (ref_04 + ref_07)

    dr_16 = ref_01 - ref_06
    dr_17 = ref_01 - 0.5 * ref_07
    dt_01 = tbb_20 - tbb_31
    dt_02 = tbb_20 - tbb_32
    dt_12 = tbb_31 - tbb_32

    rr_21 = ref_02 - ref_01
    rr_46 = ref_04 - ref_06
    rr_47 = ref_04 - ref_07

    # dt_34 = tbb_20 - tbb_23
    # dt_81 = tbb_29 - tbb_31
    # dt_38 = tbb_20 - tbb_29

    i_tag[index] = 1
    


def main(in_file):
    ndsi()


# ######################## 程序全局入口 ##############################
if __name__ == "__main__":
    # 获取程序参数接口
    ARGS = sys.argv[1:]
    HELP_INFO = \
        u"""
        [arg1]：yaml_path
        [example]： python app.py arg1
        """
    if "-h" in ARGS:
        print(HELP_INFO)
        sys.exit(-1)

    if len(ARGS) != 1:
        print(HELP_INFO)
        sys.exit(-1)
    else:
        ARG1 = ARGS[0]
        main(ARG1)
