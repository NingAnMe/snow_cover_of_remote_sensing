# -*- coding: utf-8 -*-

from datetime import datetime
import os
import re
import sys
# import time

from pyhdf.SD import SD, SDC

from lib.pb_io import attrs2dict
from lib.pb_sat import radiance2tbb
from lib.read_base import ReadL1
from qiae_lib.pb_time import JDay2Datetime
import numpy as np
from spectral.io import envi
from conda.gateways.disk.update import rename

__description__ = u'CRIS传感器读取'
__author__ = 'wangpeng'
__date__ = '2018-09-03'
__version__ = '1.0.0_beat'

g_main_path, g_main_file = os.path.split(os.path.realpath(__file__))


class ReadModisEnvi(ReadL1):

    def __init__(self, in_file, cloud_file=None):
        sensor = 'MODIS'
        super(ReadModisEnvi, self).__init__(in_file, sensor)
        self.cloud_file = cloud_file
        img = envi.open(self.in_file)
        bands = range(0, 44)
        img_data = img.read_bands(bands)
        self.data = img_data

    def set_ymd_hms(self):
        """
        use filename  set self.ymd self.hms
        """
        file_name = os.path.basename(self.in_file)
        pat = u'\w+.A(\d{4})(\d{3}).(\d{4}).*'
#         MOD021KM.A2014181.0035.005.Ref_Tbb.44Ch.Hdr
        g = re.match(pat, file_name)
        if g:
            tt = JDay2Datetime(g.group(1), g.group(2), g.group(3) + '00')
            self.ymd = tt.strftime('%Y%m%d')
            self.hms = g.group(3) + '00'
        else:
            raise ValueError('Cant get the ymdhms from file name.')

    def get_cloudmask(self):
        img = envi.open(self.cloud_file)
        img_data = img.read_band(0)
        print(img_data.shape)
        return img_data

    def get_ref(self):
        data = dict()

        for i in range(44):
            if i <= 18 or i == 25:
                band = 'CH_{:02d}'.format(i + 1)
                data[band] = self.data[:, :, i]

        return data

    def get_tbb(self):
        data = dict()
        for i in range(44):
            if i >= 19 and i <= 35:
                if i == 25:
                    continue
                band = 'CH_{:02d}'.format(i + 1)
                data[band] = self.data[:, :, i]
        return data

    def get_land_sea_mask(self):
        data = self.data[:, :, 43]
        return data

    def get_height(self):
        data = self.data[:, :, 42]
        return data

    def get_longitude(self):
        pass
        data = self.data[:, :, 41]
        return data

    def get_latitude(self):
        data = self.data[:, :, 40]
        return data

    def get_solar_azimuth(self):
        data = self.data[:, :, 39]
        return data

    def get_solar_zenith(self):
        data = self.data[:, :, 38]
        return data

    def get_sensor_azimuth(self):
        data = self.data[:, :, 37]
        return data

    def get_sensor_zenith(self):
        data = self.data[:, :, 36]
        return data


class ReadModisL1(ReadL1):
    """
     读取 modis 传感器的 L1 数据
     分辨率：1000
     卫星：AQUA TERRA
     通道数量：36 (正常38个，13i和14i删除不需要)
     可见光通道：1 2 3 4 5 6 7 8 9 10 11 12 13  14  15 16 17 18 19 26
     红外通道：20 21 22 23 24 25  27 28 29 30 31 32 33 34 35 36
    """

    def __init__(self, in_file):
        sensor = 'MODIS'
        super(ReadModisL1, self).__init__(in_file, sensor)

    def set_resolution(self):
        """
        use filename set self.resolution
        :return:
        """
        file_name = os.path.basename(self.in_file)
        if '1KM' in file_name:
            self.resolution = 1000
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))

    def set_satellite(self):
        """
        use filename set self.satellite
        :return:
        """
        if "MYD" in self.in_file:
            self.satellite = "AQUA"
        elif "MOD" in self.in_file:
            self.satellite = "TERRA"
        else:
            raise ValueError('Cant get the satellite name from file name.')

    def set_ymd_hms(self):
        """
        use filename  set self.ymd self.hms
        """
        file_name = os.path.basename(self.in_file)
        pat = u'\w+.A(\d{4})(\d{3}).(\d{4}).\d{3}.\d+.hdf$'
        g = re.match(pat, file_name)
        if g:
            tt = JDay2Datetime(g.group(1), g.group(2), g.group(3) + '00')
            self.ymd = tt.strftime('%Y%m%d')
            self.hms = g.group(3) + '00'
        else:
            raise ValueError('Cant get the ymdhms from file name.')

    def set_file_attr(self):
        """
        get hdf5 file attrs self.file_attr
        :return:
        """
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                try:
                    h4r = SD(self.in_file, SDC.READ)
                    self.file_attr = attrs2dict(h4r.attributes())
                except Exception as e:
                    print(str(e))
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                "Cant handle this resolution: ".format(self.resolution))

    def set_data_shape(self):
        """
        use dataset set self.data_shape
        :return:
        """
        # 如果分辨率是 1000 米
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                try:
                    h4File = SD(self.in_file, SDC.READ)
                    in_data_r250 = h4File.select('EV_250_Aggr1km_RefSB').get()
                    self.data_shape = in_data_r250.shape[1:]
                except Exception as e:
                    print(e)
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                "Cant handle this resolution: ".format(self.resolution))

    def set_channels(self):
        """
        return sensor channels
        :return:
        """
        if self.resolution == 1000:
            self.channels = 36
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))

    def get_dn(self):
        """
        return DN
        """
        data = dict()
        if self.resolution == 1000:  # 分辨率为 1000
            satellite_type = ['AQUA', 'TERRA']
            data_file = self.in_file
            if self.satellite in satellite_type:
                h4r = SD(data_file, SDC.READ)
                ary_ch1_2 = h4r.select('EV_250_Aggr1km_RefSB').get()
                ary_ch3_7 = h4r.select('EV_500_Aggr1km_RefSB').get()
                ary_ch8_19and26 = h4r.select('EV_1KM_RefSB').get()
                ary_ch20_36 = h4r.select('EV_1KM_Emissive').get()
                h4r.end()

                # 删除13i 14i
                ary_ch8_19and26 = np.delete(ary_ch8_19and26, (6, 8), 0)

                vmin = 0
                vmax = 32767

                # 逐个通道处理
                for i in range(self.channels):
                    band = 'CH_{:02d}'.format(i + 1)
                    # 1,2通道
                    if i < 2:
                        k = i
                        data_pre = ary_ch1_2[k]
                    # 3,4,5,6,7通道
                    elif i >= 2 and i < 7:
                        k = i - 2
                        data_pre = ary_ch3_7[k]

                    # 8,9,10,11,12,13lo,14lo,15,16,17,18,19,26通道
                    elif i >= 7 and i <= 19:
                        k = i - 7
                        if i == 19:
                            band = 'CH_{:02d}'.format(i + 7)
                        data_pre = ary_ch8_19and26[k]
                    # 20,21,22,23,24,25,27,28,29,30,31,32,33,34,35,36
                    else:
                        k = i - 20
                        if i <= 25:
                            band = 'CH_{:02d}'.format(i)
                        data_pre = ary_ch20_36[k]

                    data_pre = data_pre.astype(np.float32)
                    invalid_index = np.logical_or(
                        data_pre <= vmin, data_pre > vmax)
                    data_pre[invalid_index] = np.nan
                    data[band] = data_pre
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))

        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_ref(self):
        """
        return ref
        """

        data = dict()
#         dsl = sun_earth_dis_correction(self.ymd)
        if self.resolution == 1000:  # 分辨率为 1000
            satellite_type = ['AQUA', 'TERRA']
            data_file = self.in_file
            if self.satellite in satellite_type:
                dn = self.get_dn()
                h4r = SD(data_file, SDC.READ)
                # 12通道ab
                ary_ch1_2_a = h4r.select(
                    'EV_250_Aggr1km_RefSB').attributes()['reflectance_scales']
                ary_ch1_2_b = h4r.select(
                    'EV_250_Aggr1km_RefSB').attributes()['reflectance_offsets']

                ary_ch3_7_a = h4r.select(
                    'EV_500_Aggr1km_RefSB').attributes()['reflectance_scales']
                ary_ch3_7_b = h4r.select(
                    'EV_500_Aggr1km_RefSB').attributes()['reflectance_offsets']

                ary_ch8_19and26_a = h4r.select(
                    'EV_1KM_RefSB').attributes()['reflectance_scales']
                ary_ch8_19and26_b = h4r.select(
                    'EV_1KM_RefSB').attributes()['reflectance_offsets']

#                 ary_ch20_36_a = h4r.select(
#                     'EV_1KM_Emissive').attributes()['radiance_scales']
#                 ary_ch20_36_b = h4r.select(
#                     'EV_1KM_Emissive').attributes()['radiance_offsets']

                h4r.end()

                # 删除13i 14i通道的下标
#                 print ary_ch8_19and26_a, type(ary_ch8_19and26_a)
#                 print ary_ch8_19and26_a[6, 8]
                ary_ch8_19and26_a.pop(8)
                ary_ch8_19and26_a.pop(6)
                ary_ch8_19and26_b.pop(8)
                ary_ch8_19and26_b.pop(6)

                # 逐个通道处理
                for i in range(self.channels):
                    band = 'CH_{:02d}'.format(i + 1)
                    # 1,2通道
                    if i < 2:
                        k = i
                        data_pre = (dn[band] - ary_ch1_2_b[k]) * ary_ch1_2_a[k]
                    # 3,4,5,6,7通道
                    elif i >= 2 and i < 7:
                        k = i - 2
                        data_pre = (dn[band] - ary_ch3_7_b[k]) * ary_ch3_7_a[k]

                    # 8,9,10,11,12,13lo,14lo,15,16,17,18,19,26通道
                    elif i >= 7 and i <= 19:
                        k = i - 7
                        if i == 19:
                            band = 'CH_{:02d}'.format(i + 7)
                        data_pre = (
                            dn[band] - ary_ch8_19and26_b[k]) * ary_ch8_19and26_a[k]
                    else:
                        continue
                    data[band] = data_pre  # * dsl

        return data

    def get_rad(self):
        """
        return rad
        """
        data = dict()
        if self.resolution == 1000:  # 分辨率为 1000
            satellite_type = ['AQUA', 'TERRA']
            data_file = self.in_file
            if self.satellite in satellite_type:
                dn = self.get_dn()
                h4r = SD(data_file, SDC.READ)

                ary_ch20_36_a = h4r.select(
                    'EV_1KM_Emissive').attributes()['radiance_scales']
                ary_ch20_36_b = h4r.select(
                    'EV_1KM_Emissive').attributes()['radiance_offsets']

                h4r.end()

                center_wn = self.get_central_wave_number()
                # 逐个通道处理
                for i in range(self.channels):
                    band = 'CH_{:02d}'.format(i + 1)

                    if i >= 20:
                        k = i - 20
                        if i <= 25:
                            band = 'CH_{:02d}'.format(i)
                        data_pre = (
                            dn[band] - ary_ch20_36_b[k]) * ary_ch20_36_a[k]

                        data[band] = data_pre * \
                            ((10000 / center_wn[band]) ** 2) / 10.

        return data

    def get_rad1(self):
        """
        return rad
        """
#         dsl = sun_earth_dis_correction(self.ymd)
        data = dict()
        if self.resolution == 1000:  # 分辨率为 1000
            satellite_type = ['AQUA', 'TERRA']
            data_file = self.in_file
            if self.satellite in satellite_type:
                dn = self.get_dn()
                h4r = SD(data_file, SDC.READ)

                ary_ch20_36_a = h4r.select(
                    'EV_1KM_Emissive').attributes()['radiance_scales']
                ary_ch20_36_b = h4r.select(
                    'EV_1KM_Emissive').attributes()['radiance_offsets']

                h4r.end()

#                 center_wn = self.get_central_wave_number()
                # 逐个通道处理
                for i in range(self.channels):
                    band = 'CH_{:02d}'.format(i + 1)

                    if i >= 20:
                        k = i - 20
                        if i <= 25:
                            band = 'CH_{:02d}'.format(i)
                        data_pre = (
                            dn[band] - ary_ch20_36_b[k]) * ary_ch20_36_a[k]

                        data[band] = data_pre

        return data

    def get_tbb_k1(self):
        """
        return K1
        """
        data = dict()
        if self.resolution == 1000:  # 分辨率为 1000
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                data = {'CH_20': 9.993363E-01, 'CH_21': 9.998626E-01, 'CH_22': 9.998627E-01, 'CH_23': 9.998707E-01,
                        'CH_24': 9.998737E-01, 'CH_25': 9.998770E-01, 'CH_27': 9.995694E-01, 'CH_28': 9.994867E-01,
                        'CH_29': 9.995270E-01, 'CH_30': 9.997382E-01, 'CH_31': 9.995270E-01, 'CH_32': 9.997271E-01,
                        'CH_33': 9.999173E-01, 'CH_34': 9.999070E-01, 'CH_35': 9.999198E-01, 'CH_36': 9.999233E-01}
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_tbb_k0(self):
        """
        return K0
        """
        data = dict()

        if self.resolution == 1000:  # 分辨率为 1000
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                data = {'CH_20': 4.818401E-01, 'CH_21': 9.426663E-02, 'CH_22': 9.458604E-02, 'CH_23': 8.736613E-02,
                        'CH_24': 7.873285E-02, 'CH_25': 7.550804E-02, 'CH_27': 1.848769E-01, 'CH_28': 2.064384E-01,
                        'CH_29': 1.674982E-01, 'CH_30': 8.304364E-02, 'CH_31': 1.343433E-01, 'CH_32': 7.135051E-02,
                        'CH_33': 1.948513E-02, 'CH_34': 2.131043E-02, 'CH_35': 1.804156E-02, 'CH_36': 1.683156E-02}

            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_tbb(self):
        """
        return rad
        """

        data = dict()
        if self.resolution == 1000:  # 分辨率为 1000
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                # rad转tbb的修正系数，所有时次都是固定值
                tbb_k0 = self.get_tbb_k0()
                tbb_k1 = self.get_tbb_k1()
                rads = self.get_rad1()
#                 rads = self.get_rad()
                central_wave_numbers = self.get_central_wave_number()
                # 逐个通道处理
                for i in range(self.channels):
                    band = 'CH_{:02d}'.format(i + 1)
                    if band in rads.keys():
                        k0 = tbb_k0[band]
                        k1 = tbb_k1[band]
                        central_wave_number = central_wave_numbers[band]
                        rad = rads[band]
#                         tbb = planck_r2t(rad, central_wave_number)
#                         data[band] = tbb * k1 + k0
                        tbb = radiance2tbb(rad, central_wave_number)
                        data[band] = (tbb - k0) / k1

        return data

    def __get_geo_file(self):
        """
        return 定位文件
        """
        if self.resolution == 1000:
            satellite_type1 = ['AQUA', 'TERRA']
            if self.satellite in satellite_type1:
                file_path = os.path.dirname(self.in_file)
                file_name = os.path.basename(self.in_file)
                part1 = file_name.split('.')[1]
                part2 = file_name.split('.')[2]
                pat = u'\w{5}.%s.%s.\d{3}.\d+.hdf$' % (part1, part2)
                if os.path.isdir(file_path):
                    file_list = sorted(os.listdir(file_path), reverse=False)
                    for line in file_list:
                        m = re.match(pat, line)
                        if m:
                            geo_file = os.path.join(file_path, line)
                            break
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                "Cant handle this resolution: ".format(self.resolution))
        return geo_file

    def get_central_wave_number(self):
        '''
        return 中心波数
        central_wave_number
        wn(cm-1) = 10 ^ 7 / wave_length(nm)
        '''
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                data = {'CH_20': 2.647409E+03, 'CH_21':  2.511760E+03, 'CH_22': 2.517908E+03,
                        'CH_23': 2.462442E+03, 'CH_24': 2.248296E+03, 'CH_25': 2.209547E+03,
                        'CH_27': 1.474262E+03, 'CH_28': 1.361626E+03, 'CH_29': 1.169626E+03,
                        'CH_30': 1.028740E+03, 'CH_31': 9.076813E+02, 'CH_32': 8.308411E+02,
                        'CH_33': 7.482978E+02, 'CH_34': 7.307766E+02, 'CH_35': 7.182094E+02,
                        'CH_36': 7.035007E+02}
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data

    def get_longitude(self):
        """
        return longitude
        """
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                geo_file = self.__get_geo_file()
                h4r = SD(geo_file, SDC.READ)
                data_pre = h4r.select('Longitude').get()
                h4r.end()
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))

            # 过滤无效值
            invalid_index = np.logical_or(data_pre < -180., data_pre > 180.)
            data_pre = data_pre.astype(np.float32)
            data_pre[invalid_index] = np.nan
            data = data_pre

        return data

    def get_latitude(self):
        """
        return latitude
        """
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                geo_file = self.__get_geo_file()
                h4r = SD(geo_file, SDC.READ)
                data_pre = h4r.select('Latitude').get()
                h4r.end()
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))

            # 过滤无效值
            invalid_index = np.logical_or(data_pre < -90., data_pre > 90.)
            data_pre = data_pre.astype(np.float32)
            data_pre[invalid_index] = np.nan
            data = data_pre

        return data

    def get_sensor_azimuth(self):
        """
        return sensor_azimuth
        """
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                vmin = -18000.
                vmax = 18000.
                geo_file = self.__get_geo_file()
                h4r = SD(geo_file, SDC.READ)
                data_pre = h4r.select('SensorAzimuth').get()
                h4r.end()
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))

            # 过滤无效值
            invalid_index = np.logical_or(data_pre < vmin, data_pre > vmax)
            data_pre = data_pre.astype(np.float32)
            data_pre[invalid_index] = np.nan
            data = data_pre / 100.

        return data

    def get_sensor_zenith(self):
        """
        return sensor_zenith
        """
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                vmin = 0.
                vmax = 18000.
                geo_file = self.__get_geo_file()
                h4r = SD(geo_file, SDC.READ)
                data_pre = h4r.select('SensorZenith').get()
                h4r.end()
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))

            # 过滤无效值
            invalid_index = np.logical_or(data_pre < vmin, data_pre > vmax)
            data_pre = data_pre.astype(np.float32)
            data_pre[invalid_index] = np.nan
            data = data_pre / 100.

        return data

    def get_solar_azimuth(self):
        """
        return solar_azimuth
        """
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                vmin = -18000.
                vmax = 18000.
                geo_file = self.__get_geo_file()
                h4r = SD(geo_file, SDC.READ)
                data_pre = h4r.select('SolarAzimuth').get()
                h4r.end()
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))

            # 过滤无效值
            invalid_index = np.logical_or(data_pre < vmin, data_pre > vmax)
            data_pre = data_pre.astype(np.float32)
            data_pre[invalid_index] = np.nan
            data = data_pre / 100.

        return data

    def get_solar_zenith(self):
        """
        return solar_zenith
        """
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                vmin = 0.
                vmax = 18000.
                geo_file = self.__get_geo_file()
                h4r = SD(geo_file, SDC.READ)
                data_pre = h4r.select('SolarZenith').get()
                h4r.end()
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))

            # 过滤无效值
            invalid_index = np.logical_or(data_pre < vmin, data_pre > vmax)
            data_pre = data_pre.astype(np.float32)
            data_pre[invalid_index] = np.nan
            data = data_pre / 100.

        return data

    def get_land_sea_mask(self):
        """
        return land_sea_mask
        """
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                vmin = 0.
                vmax = 7.
                geo_file = self.__get_geo_file()
                h4r = SD(geo_file, SDC.READ)
                data_pre = h4r.select('Land/SeaMask').get()
                h4r.end()
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))

            # 过滤无效值
            invalid_index = np.logical_or(data_pre < vmin, data_pre > vmax)
            data_pre = data_pre.astype(np.float32)
            data_pre[invalid_index] = np.nan
            data = data_pre

        return data

    def get_height(self):
        """
        return height
        """
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                vmin = 27000
                vmax = 65535
                geo_file = self.__get_geo_file()
                h4r = SD(geo_file, SDC.READ)
                data_pre = h4r.select('Range').get()
                scale = h4r.select('Range').attributes()['scale_factor']
                h4r.end()
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))

            # 过滤无效值
            invalid_index = np.logical_or(data_pre < vmin, data_pre > vmax)
            data_pre = data_pre.astype(np.float32)
            data_pre[invalid_index] = np.nan
            data = data_pre * scale

        return data

    def get_timestamp(self):
        """
        return from 1970-01-01 00:00:00 seconds
        """
        if self.resolution == 1000:
            satellite_type = ['AQUA', 'TERRA']
            if self.satellite in satellite_type:
                seconds_of_file = 300  # 一个时次持续 300 秒
            else:
                raise ValueError(
                    'Cant read this satellite`s data.: {}'.format(self.satellite))
            file_date = datetime.strptime(self.ymd + self.hms, '%Y%m%d%H%M%S')
            timestamp = (
                file_date - datetime(1970, 1, 1, 0, 0, 0)).total_seconds()
            row_length = self.data_shape[0]
            delta = np.linspace(0, seconds_of_file - 1, row_length)
            data = np.full(self.data_shape, np.nan, dtype=np.float64)
            data[:] = (delta + timestamp).reshape(-1, 1)
            data = data.astype(np.int32)
        else:
            raise ValueError(
                'Cant read this data, please check its resolution: {}'.format(self.in_file))
        return data


if __name__ == '__main__':

    infile = r'D:\data\ndsi\MOD021KM.A2014181.0035.005.Ref_Tbb.44Ch.Hdr'
    cld_file = r'D:\data\ndsi\MOD021KM.A2014181.0035.005.CloudMask.hdr'
    modis = ReadModisEnvi(infile, cld_file)
    ref = modis.get_ref()
    tbb = modis.get_tbb()
    row = 63
    col = 496
    for key in ref:
        print(key, ref[key][row, col])
    for key in tbb:
        print(key, tbb[key][row, col])
    cld = modis.get_cloudmask()
    satz = modis.get_sensor_zenith()
    sata = modis.get_sensor_azimuth()
    sunz = modis.get_solar_zenith()
    suna = modis.get_solar_azimuth()
    lon = modis.get_longitude()
    lat = modis.get_latitude()
    dem = modis.get_height()
    mask = modis.get_land_sea_mask()
    print(satz.shape)
    print('sensor_zenith=', satz[row, col])
    print('sensor_azimuth=', sata[row, col])
    print('solar_zenith=', sunz[row, col])
    print('solar_azimuth=', suna[row, col])

    print('lon=', lon[row, col])
    print('lat=', lat[row, col])
    print('dem=', dem[row, col])
    print('mask=', mask[row, col])
    print('cld=', cld[row, col])
