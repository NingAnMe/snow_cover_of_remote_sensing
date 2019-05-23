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


def ndsi(in_file_l1, in_file_geo):
    # -------------------------------------------------------------------------
    # SolarZenith_MAX : MAXIMUM SOLAR ZENITH ANGLE, *1.0 DEGREE
    # solar_zenith_max = None

    # -------------------------------------------------------------------------
    # Date and Time
    # i_year = None
    # i_month = None
    # i_day = None
    # i_minute = None
    # n_year = None
    # n_month = None
    # n_day = None
    # n_hour = None
    # n_minute = None
    # n_second = None

    # -------------------------------------------------------------------------
    # out data
    # r4_rt = np.array([])
    # r4_info = np.array([])
    # i2_cm = np.array([])
    # r4_test = np.array([])

    # -------------------------------------------------------------------------
    # swath sum
    # i_swath_valid = None
    # i_sum_valid = None

    # -------------------------------------------------------------------------
    # dim_x = None
    # dim_y = None
    # dim_z = None

    # -------------------------------------------------------------------------
    # r_lats = None  # LATITUDE
    # r_lons = None  # LONGITUDE
    # a_satz = None  # SATELLITE ZENITH ANGLE
    # a_sata = None  # SATELLITE AZIMUTH
    # a_sunz = None  # SOLAR ZENITH ANGLE
    # a_suna = None  # SOLAR AZIMUTH
    # r_dems = None  # DEM MASK
    # i_mask = None  # LANDCOVER MASK
    # i_cm = None  # Cloud MASK

    # -------------------------------------------------------------------------
    # cossl = None  # SOLAR-ZENITH-ANGLE-COSINE
    # glint = None  # SUN GLINT
    # lsm = None  # Mask For Water & Land
    # i_avalible = None  # Mask For Data to be used

    # -------------------------------------------------------------------------
    # ref_01 = None  # 0.645 um : Ref, NDVI
    # ref_02 = None  # 0.865 um : Ref, NDVI
    # ref_03 = None  # 0.470 um : Ref, NDVI
    # ref_04 = None  # 0.555 um : Ref, NDVI
    # ref_05 = None  # 1.640 um : Ref, NDVI
    # ref_06 = None  # 1.640 um : Ref, NDSI
    # ref_07 = None  # 2.130 um : Ref, NDSI
    # ref_19 = None  # 0.940 um : Ref, Vapour
    # ref_26 = None  # 1.375 um : Ref, Cirrus
    # tbb_20 = None  # 3.750 um : TBB, Temperature
    # tbb_31 = None  # 11.030 um : TBB, Temperature
    # tbb_32 = None  # 12.020 um : TBB, Temperature

    # -------------------------------------------------------------------------
    # ndvis = None  # R2-R1/R2+R1: R0.86,R0.65
    # ndsi_6 = None  # R4-R6/R4+R6: R0.55,R1.64
    # ndsi_7 = None  # R4-R7/R4+R7: R0.55,R2.13
    #
    # dr_16 = None  # R1-R6:       R0.86,R1.64
    # dr_17 = None  # R1-0.5*R7:   R0.86,R2.13
    #
    # dt_01 = None  # T20-T31:     T3.75-T11.0
    # dt_02 = None  # T20-T32:     T3.75-T12.0
    # dt_12 = None  # T31-T32:     T11.0-T12.0
    #
    # rr_21 = None  # R2/R1:       R0.86,R0.65
    # rr_46 = None  # R4/R6:       R0.55,R1.64
    # rr_47 = None  # R4/R7:       R0.55,R2.13
    #
    # dt_34 = None  # T20-T23:     T3.75-T4.05
    # dt_81 = None  # T29-T31:     T8.55-T11.0
    # dt_38 = None  # T20-T29:     T3.75-T8.55

    # -------------------------------------------------------------------------
    # Used for Masking Over-Estimation for snow by monthly snow pack lines.
    # LookUpTable For Monthly CHN-SnowPackLine (ZhengZJ, 2006)
    # Line:   Longitude from 65.0 to 145.0 (Step is 0.1 deg.)
    # Column: Month from Jan to Dec (Step is month)
    # Value:  Latitude (Unit is deg.)
    # r_mon_snow_line = np.array([])  # Monthly CHN-SnowPackLine

    # Used for judging low or water cloud by BT difference.
    # LookUpTable For T11-T12 (Saunders and Kriebel, 1988)
    # Line:   T11 from 250.0K to 310.0K (Step is 1.0K)
    # Column: Secant-SZA from 1.00 to 2.50 (Step is 0.01)
    # Value:  T11-T12 (Unit is K)
    # delta_bt_lut = np.array([])  # LookUpTable for BT11-BT12

    # Used for judging snow in forest by NDSI and NDVI.
    # LookUpTable For Snow in Forest , by NDVI-NDSI (Klein et al., 1998)
    # Line:   NDVI from 0.010 to 1.000 (Step is 0.01)
    # Column: NDSI from 0.01000 to 1.00000 (Step is 0.00001)
    # Value:  NDSI (Unit is null)
    # y_ndsi_x_ndvi = np.array([])  # LookUpTable for NDSI-NDVI

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
    # y_r164_x_t11 = np.array([])  # LookUpTable For R164T11
    # y_t11_m_t12_x_r164 = np.array([])  # LookUpTable For T11mT12R164
    # y_r138_x_r164 = np.array([])  # LookUpTable For R138R164
    # y_r164_x_r138 = np.array([])  # LookUpTable For R164R138

    # -------------------------------------------------------------------------
    # Used for Reference of 11um Minimum Brightness Temperature.
    # ref_bt11um = None
    # ref_bt11um_slope_n = None
    # ref_bt11um_slope_s = None
    # ref_bt11um_offset_n = None
    # ref_bt11um_offset_s = None

    # a_low_t_lat = None  # Referential Latitude for BT11 LowThreshold
    # a_low_bt11 = None  # Referential Temp for BT11 LowThreshold
    # delta_t_low = None  # Referential Temporal Delta-Temp for BT11_Low
    # b_hai_t_lat = None  # Referential Latitude for BT11 HaiThreshold
    # b_hai_bt11 = None  # Referential Temp for BT11 HaiThreshold
    # delta_t_hai = None  # Referential Temporal Delta-Temp for BT11_Hai
    #
    # a_low_bt11_n = None
    # a_low_bt11_s = None
    # b_hai_bt11_n = None
    # b_hai_bt11_s = None

    # -------------------------------------------------------------------------
    # Used for Calculate and Store Xun number from 1 to 36 in a year.
    # f_xun_n = None
    # f_xun_s = None
    # i2_xun_num = None

    # -------------------------------------------------------------------------
    # i_step = np.array([])  # TEST-STEP
    # i_mark = np.array([])  # SNOW MAP

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

    inn_put_root_l01 = a['InnPut_Root_L01']
    inn_put_root_l02 = a['InnPut_Root_L02']
    inn_put_root_l03 = a['InnPut_Root_L03']
    # inn_put_root_l11 = a['InnPut_Root_L11']
    # inn_put_root_l12 = a['InnPut_Root_L12']
    # inn_put_root_l13 = a['InnPut_Root_L13']
    # inn_put_root_l14 = a['InnPut_Root_L14']

    inn_put_file_l01 = os.path.join(inn_put_para_path, inn_put_root_l01)
    inn_put_file_l02 = os.path.join(inn_put_para_path, inn_put_root_l02)
    inn_put_file_l03 = os.path.join(inn_put_para_path, inn_put_root_l03)
    # inn_put_file_l11 = os.path.join(inn_put_para_path, inn_put_root_l11)
    # inn_put_file_l12 = os.path.join(inn_put_para_path, inn_put_root_l12)
    # inn_put_file_l13 = os.path.join(inn_put_para_path, inn_put_root_l13)
    # inn_put_file_l14 = os.path.join(inn_put_para_path, inn_put_root_l14)

    delta_bt_lut = np.loadtxt(inn_put_file_l01, skiprows=1)[:, 1:]

    r_mon_snow_line_temp = np.loadtxt(inn_put_file_l02, skiprows=1)[:, 1:]
    r_mon_snow_line = np.zeros((3601, 12, 2))
    r_mon_snow_line[:, :, 0] = r_mon_snow_line_temp[:, 0:24:2]
    r_mon_snow_line[:, :, 1] = r_mon_snow_line_temp[:, 1:24:2]

    y_ndsi_x_ndvi = np.loadtxt(inn_put_file_l03, skiprows=1)[:]

    # y_r138_x_r164 = np.loadtxt(inn_put_file_l11, skiprows=1)[:]
    # y_r164_x_t11 = np.loadtxt(inn_put_file_l12, skiprows=1)[:]
    # y_r164_x_r138 = np.loadtxt(inn_put_file_l13, skiprows=1)[:]
    # y_t11_m_t12_x_r164 = np.loadtxt(inn_put_file_l14, skiprows=1)[:]

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

    read_ahi = ReadAhiL1(in_file_l1, geo_file=in_file_geo)
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
        print(' a_low_bt11= ', a_low_bt11, ' b_hai_bt11= ', b_hai_bt11)
        print(' a_low_bt11_n= ', a_low_bt11_n, ' a_low_bt11_s= ', a_low_bt11_s)
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
    d_solar_zenith = read_ahi.get_solar_zenith()
    i_sum_valid = np.logical_and(d_solar_zenith > 0, d_solar_zenith < solar_zenith_max).sum()
    if i_sum_valid < i_cols * 30:
        raise ValueError('Valid data is not enough.')

    # -------------------------------------------------------------------------
    # Read  FILE_GEO

    #  GET SensorZenith
    d_sensor_zenith = read_ahi.get_sensor_zenith()
    index_valid = np.logical_and(d_sensor_zenith > 0, d_sensor_zenith < 90)
    d_sensor_zenith[index_valid] = d_sensor_zenith[index_valid] / 180 * np.pi
    d_sensor_zenith[~index_valid] = np.nan

    #  GET SensorAzimuth
    d_sensor_azimuth = read_ahi.get_sensor_azimuth()
    index_valid = np.logical_and(d_sensor_azimuth > -180, d_sensor_azimuth < 180)
    d_sensor_azimuth[index_valid] = d_sensor_azimuth[index_valid] / 180 * np.pi
    d_sensor_azimuth[~index_valid] = np.nan

    #  GET SolarZenith
    d_solar_zenith = read_ahi.get_solar_zenith()
    index_valid = np.logical_and(d_solar_zenith > 0, d_solar_zenith < 90)
    d_solar_zenith[index_valid] = d_solar_zenith[index_valid] / 180 * np.pi
    d_solar_zenith[~index_valid] = np.nan

    #  GET SolarAzimuth
    d_solar_azimuth = read_ahi.get_solar_azimuth()
    index_valid = np.logical_and(d_solar_azimuth > -180, d_solar_azimuth < 180)
    d_solar_azimuth[index_valid] = d_solar_azimuth[index_valid] / 180 * np.pi
    d_solar_azimuth[~index_valid] = np.nan

    #  GET LATITUDE
    r_lats = read_ahi.get_latitude()

    #  GET LONGITUDE
    r_lons = read_ahi.get_longitude()

    #  GET Elevation
    r_dems = read_ahi.get_height()

    #  GET LandSea
    i_mask = read_ahi.get_land_sea_mask()
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
    i_lsm = np.full(data_shape, np.nan)
    i_lsm[land_condition] = 1
    i_lsm[sea_condition] = 0

    # -------------------------------------------------------------------------
    # Read  FILE_CM

    # GET Cloud Mask
    i_cm = read_ahi.get_cloudmask()

    # -------------------------------------------------------------------------
    # Read  FILE_2KM

    # COMPUTE The CORRECTED REFLECTANCE OF BANDs used
    i_ref_01 = read_ahi.get_channel_data('VIS0064')
    i_ref_02 = read_ahi.get_channel_data('VIS0086')
    i_ref_03 = read_ahi.get_channel_data('VIS0046')
    i_ref_04 = read_ahi.get_channel_data('VIS0051')
    i_ref_06 = read_ahi.get_channel_data('VIS0160')
    i_ref_07 = read_ahi.get_channel_data('VIS0230')
    # i_ref_26 = read_ahi.get_channel_data('No')  # 不能做卷积云的判断

    # COMPUTE The CORRECTED REFLECTANCE OF BANDs used
    i_tbb_20 = read_ahi.get_channel_data('IRX0390')
    i_tbb_31 = read_ahi.get_channel_data('IRX1120')
    i_tbb_32 = read_ahi.get_channel_data('IRX1230')

    # -------------------------------------------------------------------------
    #  INITIALIZATION
    i_mark = np.zeros(data_shape)
    i_step = np.zeros(data_shape)

    for row in range(i_rows):
        for col in range(i_cols):
            ref_lon = r_lons[row, col]
            ref_lat = r_lats[row, col]
            ref_dem = r_dems[row, col]

            a_satz = d_sensor_zenith[row, col]
            a_sata = d_sensor_azimuth[row, col]
            a_sunz = d_solar_zenith[row, col]
            a_suna = d_solar_azimuth[row, col]

            # -------------------------------------------------------------------------
            # COMPUTE The SUN GLINT EAGLE
            temp = np.sin(a_sunz) * np.sin(a_satz) * np.cos(a_suna - a_sata) + np.cos(a_sunz) * np.cos(a_satz)
            if temp > 1:
                temp = 1
            elif temp < -1:
                temp = -1
            glint = np.arccos(temp)

            # -------------------------------------------------------------------------
            lsm = i_lsm[row, col]
            cm = i_cm[row, col]
            i_avalible = 1

            if np.isnan(ref_lon) or np.isnan(ref_lat) or np.isnan(ref_dem) or \
                    np.isnan(a_satz) or np.isnan(a_sata) or np.isnan(a_sunz) or np.isnan(a_suna) or \
                    np.isnan(lsm) or np.isnan(cm):
                i_mark[row, col] = 11
                i_step[row, col] = 1
                i_avalible = 0
            if glint < 15 * np.pi / 180:
                i_mark[row, col] = 240
                i_step[row, col] = 5
                i_avalible = 0

            # -------------------------------------------------------------------------
            # COMPUTE The SUN GLINT EAGLE
            if ref_lat >= 0:
                if np.abs(ref_lat) < b_hai_t_lat:
                    ref_bt11um = ref_bt11um_slope_n * np.abs(b_hai_t_lat) + ref_bt11um_offset_n
                elif np.abs(ref_lat) > a_low_t_lat:
                    ref_bt11um = ref_bt11um_slope_n * np.abs(a_low_t_lat) + ref_bt11um_offset_n
                else:
                    ref_bt11um = ref_bt11um_slope_n * np.abs(ref_lat) + ref_bt11um_offset_n
            else:
                if np.abs(ref_lat) < b_hai_t_lat:
                    ref_bt11um = ref_bt11um_slope_s * np.abs(b_hai_t_lat) + ref_bt11um_offset_s
                elif np.abs(ref_lat) > a_low_t_lat:
                    ref_bt11um = ref_bt11um_slope_s * np.abs(a_low_t_lat) + ref_bt11um_offset_s
                else:
                    ref_bt11um = ref_bt11um_slope_s * np.abs(ref_lat) + ref_bt11um_offset_s

            # !!!!!!!!!!!!!!!!!!!!!!!!!!   QUALITY CONTROLLING   !!!!!!!!!!!!!!!!!!!!!!!!!!!
            #           iAvalible=1     !!  iAvalible=0(1): Data IS(NOT) USABLE.  !!
            # !!!!!!!!!!!!!!!!!!!!!!!!!!   QUALITY CONTROLLING   !!!!!!!!!!!!!!!!!!!!!!!!!!!
            ref_01 = i_ref_01[row, col]
            ref_02 = i_ref_02[row, col]
            ref_03 = i_ref_03[row, col]
            ref_04 = i_ref_04[row, col]
            ref_06 = i_ref_06[row, col]
            ref_07 = i_ref_07[row, col]
            # ref_26 = i_ref_26[row, col]

            tbb_20 = i_tbb_20[row, col]
            tbb_31 = i_tbb_31[row, col]
            tbb_32 = i_tbb_32[row, col]

            if np.isnan(ref_01) or np.isnan(ref_02) or np.isnan(ref_03) or \
                    np.isnan(ref_04) or np.isnan(ref_06) or np.isnan(ref_07) \
                    or np.isnan(tbb_20) or np.isnan(tbb_31) or np.isnan(tbb_32):
                i_mark[row, col] = 255
                i_step[row, col] = 2
                i_avalible = 0

            # CORRECT SATURATION VALUE AFTER SOLAR ZENITH ANGLE CORRECTING.
            cossl = 1.0
            ref_01 = ref_01 * cossl
            ref_02 = ref_01 * cossl
            ref_03 = ref_01 * cossl
            ref_04 = ref_01 * cossl
            ref_06 = ref_01 * cossl
            ref_07 = ref_01 * cossl

            # CHECK The Data QUALITY (ALL BANDS).
            if ref_01 <= 0 or ref_01 >= 100.0 or \
                    ref_02 <= 0 or ref_02 >= 100.0 or \
                    ref_03 <= 0 or ref_03 >= 100.0 or \
                    ref_04 <= 0 or ref_04 >= 100.0 or \
                    ref_06 <= 0 or ref_06 >= 100.0 or \
                    ref_07 <= 0 or ref_07 >= 100.0 or \
                    tbb_20 <= 170.0 or tbb_20 >= 350.0 or \
                    tbb_31 <= 170.0 or tbb_31 >= 340.0 or \
                    tbb_32 <= 170.0 or tbb_32 >= 340.0:
                i_mark[row, col] = 255
                i_step[row, col] = 3
                i_avalible = 0

            # -------------------------------------------------------------------------
            # JUDGE & MARK  SNOW
            # !!!    iTAG For marking The case of Data
            # !!!!---- Notice ----!!!!    0: badData; 1: goodData unused; 2: goodData used.
            i_tag = 0
            judge = True
            if i_avalible == 1:
                ndvis = (ref_02 - ref_01) / (ref_02 + ref_01)
                ndsi_6 = (ref_04 - ref_06) / (ref_04 + ref_06)
                ndsi_7 = (ref_04 - ref_07) / (ref_04 + ref_07)

                dr_16 = ref_01 - ref_06
                dr_17 = ref_01 - 0.5 * ref_07
                dt_01 = tbb_20 - tbb_31
                dt_02 = tbb_20 - tbb_32
                dt_12 = tbb_31 - tbb_32

                rr_21 = ref_02 / ref_01
                if rr_21 > 100.:
                    rr_21 = 100
                rr_46 = ref_04 / ref_06
                if rr_46 > 100.:
                    rr_46 = 100

                # rr_47 = ref_04 / ref_07
                # if rr_47 > 100.:
                #     rr_47 = 100

                # dt_34 = tbb_20 - tbb_23
                # dt_81 = tbb_29 - tbb_31
                # dt_38 = tbb_20 - tbb_29

                i_tag = 1

                # !!! WHEN LAND-WATER MASK IS WRONG  !!!
                if ndvis > 0.9:
                    lsm = 1
                elif ndvis < -0.9:
                    lsm = 0
                # !!!========================================================================!!!
                # !!!========================================================================!!!
                # !!!!                TESTING For WATER-BODY-PIXEL  LSM = 0                 !!!!
                # !!!========================================================================!!!
                # !!!========================================================================!!!
                # !!!---!!!---!!!   Notice  :  Test on Water Body ( LSM = 0 )    !!!---!!!---!!!
                # !!!!   TESTING For WATER-BODY ( INNER LAND, Except Glint Area )
                # !!!!!   TESTING For WATER-BODY ( OCEAN, Except Glint Area )
                if lsm == 0:
                    # !!!!   TESTING For WATER-BODY ( INNER LAND, Except Glint Area )
                    # !!!!!   TESTING For WATER-BODY ( OCEAN, Except Glint Area )
                    if judge:
                        if rr_46 > 2.0 or ndsi_6 > 0.38 or tbb_31 > 274.5:
                            i_mark[row, col] = 39
                            i_step[row, col] = 20
                            i_tag = 2
                            if ref_dem > 0:
                                i_mark[row, col] = 37
                            judge = False
                    # !!!!   TESTING For WATER-BODY ( INNER LAND, Except Glint Area )
                    # !!!!!   TESTING For WATER-BODY ( OCEAN, Except Glint Area )
                    if judge:
                        if ref_01 < 7.5 or ref_02 < 6. or ref_02 < 11. and ref_06 > 4. and tbb_31 > 274.5:
                            i_mark[row, col] = 39
                            i_step[row, col] = 21
                            i_tag = 2
                            if ref_dem > 0:
                                i_mark[row, col] = 37
                            judge = False
                    # !!!!   CERTAIN CLOUD-1 (High Cloud ; Ice Cloud ; Cold Cloud)
                    # !!!!   Temperature_Test by Referential BT11 Threshold
                    # !!!!   Cirrus_Test by Referential R1.38 Threshold

                    # if judge:
                    #     if ref_26 > 7.5 or np.abs(ref_lat) > 42. and ref_lat < 60 and \
                    #               tbb_31 < np.min([ref_bt11um + 5., 245.15]):
                    #         i_mark[row, col] = 50
                    #         i_step[row, col] = 22
                    #         i_tag = 2

                    # !!!!   CERTAIN CLOUD-2 (Middle or Low Level Cloud, Except Glint Area)
                    if judge:
                        if (ref_06 > 8.5 and tbb_20 > 278.5) or (dt_02 > 9.5 and rr_46 < 8.) or \
                                  ndsi_6 < 0.5:
                            i_mark[row, col] = 50
                            i_step[row, col] = 23
                            i_tag = 2
                            judge = False
                    if judge:
                        if ndsi_6 > 0.6 and ndvis > -0.15 and tbb_31 < 273.5 and dr_16 > 20. and \
                                  ref_01 > 25. and (4. < ref_06 < 20.):
                            i_mark[row, col] = 200
                            i_step[row, col] = 24
                            i_tag = 2
                    if judge:
                        if ndsi_6 > 0.6 and ndvis < -0.03 and tbb_31 < 274.5 and (9.0 < dr_16 < 60.) and \
                                  (10. < ref_01 < 60.) and (ref_06 < 10. < rr_46):
                            i_mark[row, col] = 100
                            i_step[row, col] = 25
                            i_tag = 2
                    # !!!------------------------------------------------------------------------!!!
                    # !!!!    Monthly_SnowPackLine_LUT CLOUD-TEST For The REHANDLED DOT
                    # !!!------------------------------------------------------------------------!!!
                    # 监测雪线
                    # !
                    # !     Eliminate Snow by Monthly_SnowPackLine_LUT Cloud-Test for rehandled pixel
                    # !
                    if judge:
                        if ref_lat > 0:
                            i_nor_s = 0
                        else:
                            i_nor_s = 1
                        # !!!---!!!---!!!      Notice  :  Test on Land ( LSM = 1 )       !!!---!!!---!!!
                        # !!!!   TESTING For SNOW ON LAND
                        # !!!!   Eliminate_Snow-3
                        if judge:
                            if (np.abs(r_mon_snow_line[round((ref_lon + 180) * 10), int(j_month), i_nor_s]) >
                                    abs(ref_lat) and (i_mark[row, col] == 200 or i_mark[row, col] == 100)):
                                i_mark[row, col] = 50
                                i_step[row, col] = 26
                                i_tag = 2
                                judge = False
                        if judge:
                            if np.abs(ref_lat) < 30. and (i_mark[row, col] == 200 or i_mark[row, col] == 100):
                                i_mark[row, col] = 50
                                i_step[row, col] = 27
                                i_tag = 2
                                judge = False
                        if judge:
                            if i_mark[row, col] == 200 or i_mark[row, col] == 100:
                                judge = False

                    # !!!!   TESTING For WATER-BODY FROM UNKOWN PIXELS( INNER LAND, Except Glint Area )
                    # !!!!   TESTING For WATER-BODY FROM UNKOWN PIXELS ( OCEAN, Except Glint Area )
                    if judge:
                        if ref_06 < 6. and dt_02 < 5. and rr_46 > 3.:
                            i_mark[row, col] = 39
                            i_step[row, col] = 28
                            i_tag = 2
                            judge = False
                    if judge:
                        i_mark[row, col] = 1
                        i_step[row, col] = 30
                        i_tag = 2
                # !!!========================================================================!!!
                # !!!========================================================================!!!
                # !!!!                   TESTING For LAND-PIXEL  LSM = 1                    !!!!
                # !!!========================================================================!!!
                # !!!========================================================================!!!
                elif lsm == 1:
                    # !!!!   TESTING For Clear Land ( For Forest )
                    # !!!!   CERTAIN
                    if judge and (tbb_31 > 278. and ndvis > 0.2):
                        i_mark[row, col] = 25
                        i_step[row, col] = 31
                        i_tag = 2
                        judge = False
                    # !!!!   TESTING For Clear Land ( Including some Dust Storm above Desert )
                    # !!!!   CERTAIN
                    if judge and (ndsi_6 < -0.2):
                        i_mark[row, col] = 25
                        i_step[row, col] = 32
                        i_tag = 2
                        judge = False

                    if judge and (dt_12 < -0.1 and ndsi_6 < 0.08):
                        # !!!---!!!---!!!      Notice  :  Test on Land ( LSM = 1 )       !!!---!!!---!!!
                        # !!!!   TESTING For Cloud ( Including some Dust Storm above Desert )
                        # if ref_26 is not None and ref_26 > 5.:
                        #     i_mark[row, col] = 50
                        #     i_step[row, col] = 33
                        #     i_tag = 2
                        #     judge = False

                        # !!!!   TESTING For Clear Land ( Including some Dust Storm above Desert )
                        if judge:
                            # !!!!   TESTING For Clear Land ( Including some Dust Storm above Desert )
                            if judge and (dt_01 < 28.):
                                i_mark[row, col] = 25
                                i_step[row, col] = 34
                                i_tag = 2
                                judge = False
                            # !!!!   TESTING For Cloud ( Including some Dust Storm above Desert )
                            if judge and (dt_01 >= 28.):
                                i_mark[row, col] = 50
                                i_step[row, col] = 35
                                i_tag = 2
                                judge = False
                    # !!!!   TESTING For Clear Land ( Including Desert and Non-High-LAT Vegetation )
                    # !!!!   CERTAIN
                    if judge and (dr_16 < -7.5):
                        i_mark[row, col] = 25
                        i_step[row, col] = 36
                        i_tag = 2
                        judge = False
                    # !!!!   TESTING For Snow on Land ( Certainly Snow by  )
                    # !!!!   CERTAIN
                    if judge and (rr_46 > 5.5 and ref_01 > 65. and 240.5 < tbb_31 < 276.5):
                        i_mark[row, col] = 200
                        i_step[row, col] = 37
                        i_tag = 2
                        judge = False
                    # !!!!   TESTING For Cloud ( mid-lower Cloud AFTER Desert is marked )
                    if judge:
                        if ref_dem < 1800.:
                            if judge and (ref_06 > 28. and ref_01 > 34. and ref_02 > 44.):
                                i_mark[row, col] = 50
                                i_step[row, col] = 38
                                i_tag = 2
                                judge = False
                            if judge and (dt_01 > 20.5):
                                i_mark[row, col] = 50
                                i_step[row, col] = 39
                                i_tag = 2
                                judge = False
                        else:
                            if judge and (ref_06 > (28. + (ref_dem - 1800.) * 0.004) and ref_01 > 34. and ref_02 > 44.):
                                i_mark[row, col] = 50
                                i_step[row, col] = 40
                                i_tag = 2
                                judge = False
                            if judge and (dt_01 > (20.5 + (ref_dem - 1800.) * 0.002)):
                                i_mark[row, col] = 50
                                i_step[row, col] = 41
                                i_tag = 2
                                judge = False
                    if judge:
                        if tbb_31 < 170 or tbb_31 > 335. or tbb_32 < 170. or tbb_32 > 335. or \
                                a_satz > 8. or ndsi_6 > 0.5:
                            pass
                        else:
                            test_dtb = tbb_31 - tbb_32
                            i_test_t11 = round(tbb_31)
                            if i_test_t11 <= 250:
                                i_test_t11 = 250
                            if i_test_t11 >= 310:
                                i_test_t11 = 310
                            sec_sza = 100. / np.cos(a_satz)
                            i_sec_sza = round(sec_sza)
                            if i_sec_sza >= 250:
                                i_sec_sza = 250
                            if test_dtb > delta_bt_lut[round(i_test_t11 - 250), i_sec_sza]:
                                i_mark[row, col] = 50
                                i_step[row, col] = 42
                                i_tag = 2
                                judge = False

                    # !!!!   CERTAIN CLOUD-1 (High Cloud ; Ice Cloud ; Cold Cloud)
                    # !!!!   Temperature_Test by Referential BT11 Threshold
                    # !!!!   Cirrus_Test by Referential R1.38 Threshold
                    if judge:
                        compared_t11_hai_lat_a = ref_bt11um + 8. - ref_dem / 1000.
                        compared_t11_hai_lat_b = 250. - ref_dem / 1000.
                        compared_t11_hai_lat = min(compared_t11_hai_lat_a, compared_t11_hai_lat_b)
                        compared_t11_low_lat_a = ref_bt11um + 12. - ref_dem / 400.
                        compared_t11_low_lat_b = 260. - ref_dem / 400.
                        compared_t11_low_lat = max(compared_t11_low_lat_a, compared_t11_low_lat_b)
                        if (40. <= np.abs(ref_lat) <= 57. and tbb_31 < compared_t11_hai_lat) or \
                                (17. <= np.abs(ref_lat) <= 40. and tbb_31 < compared_t11_low_lat):
                            i_mark[row, col] = 50
                            i_step[row, col] = 43
                            i_tag = 2
                            judge = False

                    # !!!!   CLOUD-1 (High Cloud ; Ice Cloud ; Cold Cloud)
                    # if judge:
                    #     compared_ref26 = 14.5 + ref_dem / 500.
                    #     if (ref_26 > compared_ref26 and dt_01 > 21.) or \
                    #             (ref_26 > compared_ref26 - 7. and tbb_31 < ref_bt11um + 8. and ndsi_6 > -0.11):
                    #         i_mark[row, col] = 50
                    #         i_step[row, col] = 44
                    #         i_tag = 2
                    #         judge = False

                    # !!!!!   TESTING For LAND WITH CLEAR SKY
                    # !!!!!   CERTAIN
                    if judge:
                        if (ndvis > 0.24 and ndsi_6 < 0.14) or \
                                ndsi_6 < -0.21 or \
                                ndsi_7 < -0.08 or \
                                (rr_21 > 1.42 and ndsi_6 < 0.145) or \
                                (dr_17 < 14. and ndsi_6 < 0.135) or \
                                dr_16 < -9.8:
                            i_mark[row, col] = 25
                            i_step[row, col] = 45
                            i_tag = 2

                    # !!!!   TESTING For Clear Land ( For Forest , small number )
                    # !!!!   CERTAIN
                    if judge:
                        if (ndvis > 0.24 and ndsi_6 < 0.15) or \
                                ndsi_6 < -0.21 or \
                                (rr_21 > 1.4 and ndsi_6 < 0.15) or \
                                dr_16 < -9.5:
                            i_mark[row, col] = 25
                            i_step[row, col] = 46
                            i_tag = 2
                            judge = False

                    # !!!!   TESTING For Snow in Forest by NDVI-NDSI6-T11
                    # !!!------------------------------------------------------------------------!!!
                    # !!!!    NDVI_NDSI_LUT SNOW-TEST
                    # !!!------------------------------------------------------------------------!!!
                    if judge:
                        if ndvis > 0.1:
                            if ndsi_6 > y_ndsi_x_ndvi[round(ndvis * 100), 1] and \
                                    tbb_31 < 277.:
                                i_mark[row, col] = 200
                                i_step[row, col] = 47
                                i_tag = 2
                                judge = False
                    # !!!!   TESTING For SNOW ON LAND ( For FOREST-SNOW )
                    # !!!!   SNOW-0
                    if judge:
                        if ndsi_6 > 0.18 and np.abs(ref_lat) > 36. and \
                                240.15 < tbb_31 < 272.15 and \
                                ndvis > 0.16 and ref_02 > 20. and ref_06 < 17.:
                            i_mark[row, col] = 200
                            i_step[row, col] = 48
                            i_tag = 2
                            judge = False

                    if judge:
                        if i_mark[row, col] == 25:
                            judge = False

                    # !!!!   TESTING For SNOW ON LAND ( For Thawy Snow )
                    # !!!!   SNOW-1
                    # if judge:
                    #     if ref_dem > 2000. and ndsi_6 > 0.33 and \
                    #             266.15 < tbb_20 < 285.15 and \
                    #             264.15 < tbb_31 < 275.15 and \
                    #             6.5 < dt_01 < 21. and \
                    #             41. < ref_01 < 79. and \
                    #             12.5 < ref_06 < 24.5 and \
                    #             9.5 < ref_26 < 17.:
                    #         i_mark[row, col] = 200
                    #         i_step[row, col] = 49
                    #         i_tag = 2
                    #         judge = False

                    # !!!!    TESTING For Thin-Snow by Using R01-R06-NDSI6
                    # !!!!   SNOW-2
                    if judge:
                        if ref_dem > 750. and \
                                min(ref_bt11um + 25., 265.15) < tbb_31 < 282. and \
                                20. < ref_01 < 55. and \
                                10. < ref_06 < 24.:
                            if ndsi_6 > 0.68 - 0.0262 * ref_06 and \
                                    ndsi_6 > -0.33 + 0.0164 * ref_01:
                                i_mark[row, col] = 200
                                i_step[row, col] = 50
                                i_tag = 2
                                judge = False

                    # !!!!   TESTING For SNOW ON LAND
                    # !!!!   SNOW-3
                    if judge:
                        if np.abs(ref_lat > 40.):
                            snow_ref_bt11um = ref_bt11um + 5.
                        elif 20. < np.abs(ref_lat) < 40.:
                            snow_ref_bt11um = ref_bt11um + 18. - ref_dem / 800.
                        else:
                            snow_ref_bt11um = 268.
                        if rr_46 > 3.1 and snow_ref_bt11um < tbb_31 < 278.:
                            if np.abs(ref_lat) > 20.:
                                i_mark[row, col] = 200
                                i_step[row, col] = 51
                                i_tag = 2
                                judge = False
                            else:
                                i_mark[row, col] = 200
                                i_step[row, col] = 52
                                i_tag = 2
                                judge = False

                    # !!!!   TESTING For SNOW ON LAND
                    # !!!!   SNOW-4
                    if judge:
                        if dr_16 > 10. and 19.5 > ref_06 < tbb_31 < 276.15 and \
                                1.5 < rr_46 < dt_02 < 15. and ref_02 > 26.:
                            i_mark[row, col] = 200
                            i_step[row, col] = 53
                            i_tag = 2

                    # !!!!   TESTING For SNOW ON LAND
                    # !!!!   SNOW-5
                    if judge:
                        if ndsi_6 > 0.52 and ref_bt11um + 2. < tbb_31 < 278.:
                            i_mark[row, col] = 200
                            i_step[row, col] = 54
                            i_tag = 2
                        elif 0.12 < ndsi_6 < 0.52 and ref_bt11um < tbb_31 < 276.15 and \
                                ndvis > 0.16 and ref_02 > 26.:
                            i_mark[row, col] = 200
                            i_step[row, col] = 55
                            i_tag = 2
                        else:
                            pass

                    # !!!!   TESTING For SNOW ON LAND
                    # !!!!   Eliminate_Snow-1
                    # !!!------------------------------------------------------------------------!!!
                    # !!!!    IceCloud_Overlay_WaterCloud_LUT CLOUD-TEST For The REHANDLED DOT
                    # !!!------------------------------------------------------------------------!!!
                    # if judge:
                    #     if i_mark[row, col] == 200. and ref_dem < 3000 and \
                    #             0.38 < ndsi_6 < ref_06 < 25. and \
                    #             0.01 < ref_26 < 55. and \
                    #             235. < tbb_31 < 275.:
                    #         ice_cloud_sums = 0
                    #         if ref_26 * 100 > y_r138_x_r164[round(ref_06 * 10), 1]:
                    #             ice_cloud_sums += 1
                    #         if ref_06 * 100. > y_r164_x_t11[round(tbb_31 * 10), 1]:
                    #             ice_cloud_sums += 1
                    #         if ref_06 * 100. > y_r164_x_r138[round(ref_26 * 10), 1]:
                    #             ice_cloud_sums += 1
                    #         if dt_12 * 100. > y_t11_m_t12_x_r164[round(ref_06 * 10.), 1]:
                    #             ice_cloud_sums += 1
                    #         if ice_cloud_sums > 2:
                    #             i_mark[row, col] = 50
                    #             i_step[row, col] = 56
                    #             i_tag = 2
                    #             judge = False

                    # !!!!   TESTING For SNOW ON LAND
                    # !!!!   Eliminate_Snow-2
                    # !!!------------------------------------------------------------------------!!!
                    # !!!!    Monthly_SnowPackLine_LUT CLOUD-TEST For The REHANDLED DOT
                    # !!!------------------------------------------------------------------------!!!
                    if judge:
                        if ref_lat > 0:
                            i_nor_s = 0
                        else:
                            i_nor_s = 1
                        if np.abs(r_mon_snow_line[round((ref_lon + 180) * 10), j_month, i_nor_s]) > np.abs(ref_lat) \
                                and (i_mark[row, col] == 200. or i_mark[row, col] == 100):
                            i_mark[row, col] = 50
                            i_step[row, col] = 57
                            i_tag = 2
                            judge = False
                    if judge:
                        if i_mark[row, col] == 200:
                            judge = False

                    # !!!!   TESTING For CLOUD
                    # if judge:
                    #     if ref_06 > 29. and \
                    #             (ref_26 > 13.5 or (ref_26 > 7.5 and tbb_31 < ref_bt11um + 8)) and \
                    #             ref_01 > 24.:
                    #         i_mark[row, col] = 50
                    #         i_step[row, col] = 58
                    #         i_tag = 2
                    #         judge = False

                    # !!!!   Mending TEST For Clear Land
                    if judge:
                        if (ndvis > 0.11 and tbb_31 < 280.) or dr_16 < 0. or ndsi_6 < -0.15:
                            i_mark[row, col] = 25
                            i_step[row, col] = 59
                            i_tag = 2
                            judge = False
                    if judge:
                        if ndvis > 0.11 and tbb_31 < 280.:
                            i_mark[row, col] = 50
                            i_step[row, col] = 60
                            i_tag = 2
                            judge = False
                    if judge:
                        if dr_16 < 0.:
                            i_mark[row, col] = 25
                            i_step[row, col] = 61
                            i_tag = 2
                            judge = False
                    if judge:
                        if ndsi_6 < -0.15:
                            i_mark[row, col] = 25
                            i_step[row, col] = 62
                            i_tag = 2
                            judge = False

                    # !!!!   Mending TEST For Clear Land and Cloud by Hai-T11
                    if judge:
                        if tbb_31 > 280.:
                            if rr_46 < 1.35:
                                i_mark[row, col] = 25
                                i_step[row, col] = 66
                                i_tag = 2
                                judge = False
                        else:
                            if judge:
                                if ref_dem >= 3300 and ref_01 >= 40. and ref_06 < 20. and \
                                        tbb_20 < 295. and rr_46 > 1.3:
                                    i_mark[row, col] = 200
                                    i_step[row, col] = 67
                                    i_tag = 2
                                    judge = False
                            if judge:
                                if rr_46 < 1.4:
                                    if ref_02 < 28.:
                                        i_mark[row, col] = 25
                                        i_step[row, col] = 68
                                        i_tag = 2
                                        judge = False
                                    else:
                                        i_mark[row, col] = 50
                                        i_step[row, col] = 69
                                        i_tag = 2
                                        judge = False
                    # !!!!   UNKNOWN TYPE
                    if judge:
                        i_mark[row, col] = 50
                        i_step[row, col] = 69
                        i_tag = 2
            judge = True

            # !!!!   Eliminate_Snow-3

            if judge:
                if i_avalible == 1:
                    ndsi_6 = (ref_04 - ref_06) / (ref_04 + ref_06)
                    dt_01 = tbb_20 - tbb_31
                    # !!!------------------------------------------------------------------------!!!
                    # !!!!    Monthly_SnowPackLine_LUT CLOUD-TEST For The REHANDLED DOT
                    # !!!------------------------------------------------------------------------!!!
                    if ref_lat > 0:
                        i_nor_s = 0
                    else:
                        i_nor_s = 1
                    if np.abs(r_mon_snow_line[round((ref_lon + 180) * 10), j_month, i_nor_s]) > np.abs(ref_lat) and \
                            (i_mark[row, col] == 200. or i_mark[row, col] == 100):
                        i_mark[row, col] = 50
                        i_step[row, col] = 57
                        i_tag = 2
                        judge = False
                    # !!!!  Take Snow-on-Ice Pixel above Water-body as ICE
                    if judge:
                        if lsm == 0 and i_mark[row, col] == 200:
                            i_mark[row, col] = 100

                    if judge:
                        if i_mark[row, col] == 1:
                            if lsm == 0:
                                if ref_02 < 18.:
                                    i_mark[row, col] = 39
                                if ref_02 > 19.:
                                    i_mark[row, col] = 50
                                # if ref_26 > 1.5:
                                #     i_mark[row, col] = 50
                                i_step[row, col] = 72
                            else:
                                if ndsi_6 > 0.27 and tbb_31 < 273.15 and 2.45 < dt_01 < 14.10:
                                    i_mark[row, col] = 200
                                    i_step[row, col] = 74
                                else:
                                    if 9.1 < ref_02 < 26.:
                                        i_mark[row, col] = 25
                                    if 1.1 < ref_02 < 8.:
                                        i_mark[row, col] = 25
                                    if ref_02 > 46.:
                                        i_mark[row, col] = 50
                                    # if ref_26 > 10.:
                                    #     i_mark[row, col] = 50
                                    i_step[row, col] = 76

            # !!!==========================================================================!!!
            # !
            # !     SE by Tree-Decision Algorithm after CM
            # !
            # !!!--------------------------------------------------------------------------!!!
            # !!!!   Value = 0 :  cloudy
            # !!!!   Value = 1 :  uncertain
            # !!!!   Value = 2 :  probably clear
            # !!!!   Value = 3 :  confident clear
            # !!!--------------------------------------------------------------------------!!!
            judge = True
            if i_avalible == 1 and i_cm is not None:
                if i_cm[row, col] == 0:
                    if judge:
                        if i_mark[row, col] == 1:
                            i_mark[row, col] = 50
                            i_step[row, col] = 80
                            judge = False
                if i_cm[row, col] == 3:
                    if judge:
                        if i_mark[row, col] == 50 or i_mark[row, col] == 1:
                            i_mark[row, col] = 25
                            i_step[row, col] = 82
                            judge = False
                    if judge:
                        if i_mark[row, col] == 200 and i_tag < 3:
                            i_mark[row, col] = 200
                            i_step[row, col] = 83
                            # i_tag = 3
                            # judge = False


def main(in_file):
    if in_file:
        pass
    in_file_l1 = r'D:\KunYu\hangzhou_anning\H8_L1\AHI8_OBI_2000M_NOM_20190426_2200.hdf'
    in_file_geo = r'D:\KunYu\hangzhou_anning\h8_2km_lut.hdf'
    ndsi(in_file_l1, in_file_geo)


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
