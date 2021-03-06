# -*- coding: utf-8 -*-

import os
import sys
import h5py
import yaml
import numpy as np
from qiae_lib.dp_proj import prj_core
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
# import cartopy.feature as cfeature
# from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from pylab import axis
# 必须加这个字段，否则引用 pyplot 服务器会报错，服务器上面没有 TK
mpl.use("Agg")
'''
Created on 2019年12月20日
@author: wape2
'''
main_path, main_file = os.path.split(os.path.realpath(__file__))

color_lst_lab = ['Bad Value', 'Undeterminted', 'Night', 'Clear Land', 'Inland Water', 'Sea Water', 'Cloud Cover', 'Ice Cover', 'Snow Cover', 'Satturated', 'No Data']
color_lst_bar = ['w', 'black', 'black', 'w', 'w', 'w', 'black', 'w', 'w', 'w', 'w', 'w']

color_lst = {
    'No Data': (0., 0., 0.),  # 255-无数据-黑色
    'Satturated': (139 / 255., 0., 0.),  # 254-太阳天顶角饱和-红褐色
    'Snow Cover': (0., 238 / 255., 238 / 255.),  # 200-雪-蓝绿色
    'Ice Cover': (0., 139 / 255., 139 / 255.),  # 100-冰-青色
    'Cloud Cover': (255 / 255., 255 / 255., 255 / 255.),  # 50-云-白色
    'Sea Water': (0., 0., 139 / 255.),  # 39-海冰-深蓝色
    'Inland Water': (0., 0., 255 / 255.),  # 37-内陆水-蓝色
    'Clear Land': (160 / 255., 82 / 255., 45 / 255.),  # 25-陆地-褐色
    'Night': (216 / 255., 191 / 255., 216 / 255.),  # 11-暗像元-淡粉色
    'Undeterminted':(255 / 255., 255 / 255., 0),  # 1-不确定-黄色
    'Bad Value': (100 / 255., 100 / 255., 100 / 255.)  # 0-丢线-灰色
}

color_dict = ['#646464', '#FFFF00', '#D8BFD8', '#A0522E', '#0000FF', '#00008B', '#FFFFFF',
             '#008B8B', '#00EEEE', '#8B0000', '#000000']
# cdict = ['#646464', '#FFFF00', '#D8BFD8', '#A0522E', '#0000FF', '#00018A', '#FFFFFF',
#              '#008B8B', '#00EEEE', '#8B0000', '#000000']


def ndsi_colormap():
    # 灰色  黄色  淡粉 褐色 蓝色  深蓝  白色 青色  蓝绿  红褐 黑色

    # 按照上面定义的colordict，将数据分成对应的部分，indexed：代表顺序
    return mpl.colors.ListedColormap(color_dict, 'indexed')


class ReadModeYaml():

    def __init__(self, in_file):
        """
        读取yaml格式配置文件
        """
        if not os.path.isfile(in_file):
            print ('Not Found %s' % in_file)
            sys.exit(-1)

        with open(in_file, 'r') as stream:
            cfg = yaml.load(stream)

        self.area = cfg['a02']['area']
        self.res = cfg['a02']['res']


class ReadInPutYaml():

    def __init__(self, in_file):
        """
        读取yaml格式配置文件
        """
        if not os.path.isfile(in_file):
            print ('Not Found %s' % in_file)
            sys.exit(-1)

        with open(in_file, 'r') as stream:
            cfg = yaml.load(stream)

            self.job_name = cfg['INFO']['job_name']
            self.ymd = cfg['INFO']['ymd']
            self.ipath = cfg['PATH']['ipath']
            self.opath = cfg['PATH']['opath']


class ReadAodData():

    def __init__(self):

        pass

    def load_lonlat(self, infile):

        data_dict = {}
        with h5py.File(infile, 'r') as h5w:
            lons = h5w.get('Longitude')[:]
            lats = h5w.get('Latitude')[:]

        data_dict['lon'] = lons
        data_dict['lat'] = lats
        return data_dict

    def load_snc(self, infile):
        with h5py.File(infile, 'r') as h5w:
            aod = h5w.get('SNC')[:]
        return aod


#     def loads(self, infile):
#         """
#         dataset | group/dataset   input dict
#         """
#
#         if not os.path.isfile(infile):
#             raise ValueError('File is not exist: {}'.format(infile))
#
#         data = dict()
#
#         with h5py.File(infile, 'r') as h5w:
#             for root_name in h5w:
#                 h5_name = h5w.get(root_name)
#
#                 if 'Dataset' in type(h5_name).__name__:
#                     sds_name = root_name
#                     print ('-->', sds_name)
#                     data[sds_name] = h5w.get(sds_name)[:]
#
#                 elif 'Group' in type(h5_name).__name__:
#                     grp_name = root_name
#                     if grp_name not in data:
#                         data[grp_name] = {}
#                     for sds_name in h5_name:
#                         print ('-->', grp_name, sds_name)
#                         data[grp_name][sds_name] = h5_name.get(sds_name)[:]
#         return data
def combine(yaml1, yaml2, outfile):

    nlat, slat, wlon, elon = yaml2.area
    res = yaml2.res  # degree
    # 记录个点中心位置
    if nlat <= 0:
        nlat = nlat + res / 2
    else:
        nlat = nlat - res / 2

    if slat <= 0:
        slat = slat + res / 2
    else:
        slat = slat - res / 2

    if wlon <= 0:
        wlon = wlon + res / 2
    else:
        wlon = wlon - res / 2

    if elon <= 0:
        elon = elon + res / 2
    else:
        elon = elon - res / 2

    cmd = '+proj=longlat +datum=WGS84 +no_defs'
    print (wlon, nlat, elon, slat)
    pp = prj_core(cmd, res, unit = 'deg', pt_tl = (wlon, nlat), pt_br = (elon, slat))
    print (yaml2.res)

    proj_ndsi = np.full((pp.row, pp.col), 0, np.uint8)

    proj_lut = {}

    """
    Python将内存分为了3“代”，分别为年轻代（第0代）、中年代（第1代）、老年代（第2代）
        对应的是3个链表，它们的垃圾收集频率随着对象的存活时间的增大而减小
    """
    h5data = ReadAodData()
    for infile in yaml1.ipath:
        data = h5data.load_lonlat(infile)
        lons = data['lon']
        lats = data['lat']
        lut = pp.create_lut(lons, lats)
        proj_lut[infile] = lut

    h5data = ReadAodData()
    for infile in proj_lut:
        di = proj_lut[infile]['pre_i']
        dj = proj_lut[infile]['pre_j']
        pi = proj_lut[infile]['prj_i']
        pj = proj_lut[infile]['prj_j']
        ndsi = h5data.load_snc(infile)
        proj_ndsi[pi, pj] = ndsi[di, dj]

    h5w = h5py.File(outfile, 'w')
    h5w.create_dataset('ndsi', data = proj_ndsi, compression = 'gzip', compression_opts = 5, shuffle = True)
    h5w.close()

    return proj_ndsi


def main(yaml_file):

    # 读取接口文件
    yaml1 = ReadInPutYaml(yaml_file)
    mode_file = os.path.join(main_path, 'cfg', '%s.yaml' % (yaml1.job_name))
    yaml2 = ReadModeYaml(mode_file)

    resname = int(yaml2.res * 100000)
    outpath = yaml1.opath
    outname = '%s_NDSI_DAILY_%s_%sM.HDF5' % (yaml1.job_name, yaml1.ymd, resname)

    sat, sensor = yaml1.job_name.split('_')
    ymd = yaml1.ymd

    if not os.path.isdir(outpath):
        os.makedirs(outpath)

    outfile = os.path.join(outpath, outname)
    outpng = outfile + '.png'
    ndsi = None
    if not os.path.isfile(outfile):
        ndsi = combine(yaml1, yaml2, outfile)
    if not os.path.isfile(outpng):
        if ndsi is not None:
            plot_map(sat, sensor, ymd, ndsi, outpng)
        else:
            h5w = h5py.File(outfile)
            data = h5w.get('ndsi')[:]
            h5w.close()
            plot_map(sat, sensor, ymd, data, outpng)


def plot_map(sat, sensor, ymd, img, outfig):

    fig = plt.figure(figsize = (20, 10))
    ax = fig.add_subplot(111, projection = ccrs.PlateCarree())
    pos1 = ax.get_position()
    print (pos1)
#     ax2 = fig.add_axes([0.91, 0.11, 0.02, 0.771])  # 距离左下的x,y,宽,高
#     ax.set_global()
    ax.coastlines(resolution = '50m', color = 'black', linewidth = 0.3, zorder = 100)
#     ax.stock_img()
    print('start')
    # w e n s
    img_extent = (-180, 180, -90, 90)

    # 设置色标的最大最小值
#     norm = mpl.colors.Normalize(vmin = 0, vmax = 255)
    mycolormap = ndsi_colormap()
    # 11个颜色值，对应的11个区间，数据是12个
    bounds = [0, 0.1, 1.1, 11.1, 25.1, 37.1, 39.1, 50.1, 100.1, 200.1, 254.1, 255.1]

    norm = mpl.colors.BoundaryNorm(bounds, mycolormap.N)
    print (mycolormap.N)
    img = np.ma.masked_where(img < 0 , img)

#     cb = ax.scatter(lon, lat, marker = '.', c = value, s = 0.4, cmap = 'jet', lw = 0, norm = norm)
    im = ax.imshow(img, origin = 'upper', cmap = mycolormap, norm = norm, extent = img_extent, transform = ccrs.PlateCarree())

    # 标注坐标轴
    ax.set_xticks([-180, -120, -60, 0, 60, 120, 180], crs = ccrs.PlateCarree())
    ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], crs = ccrs.PlateCarree())
    # zero_direction_label用来设置经度的0度加不加E和W
    lon_formatter = LongitudeFormatter(zero_direction_label = False)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.grid(linestyle = '--')
    ax.tick_params(labelsize = 12)

    pos1 = ax.get_position()
    print (pos1)
    ax2 = fig.add_axes([0.1275, 0.01, 0.77, 0.04])  # 距离左下的x,y,宽,高
#     ax2 = fig.add_subplot(212)
    ax2.set_xticks([])
    ax2.set_yticks([])
    if sat in ['FY3D']:
        sat = sat[:2] + '-' + sat[2:]
        ax.set_title('%s/%s-II Daily Snow Extent %s' % (sat, sensor, ymd), fontsize = 20)
    else:
        sat = sat[:2] + '-' + sat[2:]
        ax.set_title('%s/%s Daily Snow Extent %s' % (sat, sensor, ymd), fontsize = 20)
    # 取消colorbar上的刻度
#     cb.set_ticks([])
#     xpos = 0
#     for i in range(0, 11):
#         # text的xy是针对fig的xy
#         xpos_step = 1 / 11
#         xpos = i * xpos_step + 0.005
#         ax2.text(xpos, 0.45, label_lst[i], color = color_lst[i], ha = 'left', va = 'center', fontsize = 6)
    drawRects(ax2)
    # 更改刻度位置 写入自定义内容，删除数值标记
#     color_lst = ['灰色-丢线', '黄色-不确定', '淡粉-暗像元', '褐色-陆地', '蓝色-内陆水', '深蓝-海水', '白色-云', '青色-冰', '蓝绿-雪', '红褐-饱和', '黑色-无效']
#     labels = np.arange(0, 12, 1)
#     loc = labels + .5
#     cb.set_ticks(loc)
#     ax2.yaxis.set_tick_params(labelsize = 7)
#     cb.set_ticklabels(color_lst)
#     out_fig = r'D:\data\ndsi\global_map_10km.png'
#     plt.savefig(out_fig, dpi = 300)
    plt.savefig(outfig, dpi = 360)
#     plt.show()
    print('end')


def drawRects(ax):
    '''
    色标
    '''
#     divider = make_axes_locatable(ax)
#     fig = ax.get_figure()
#     ax2 = divider.append_axes("bottom", "2%", pad = "0.1%")
#     fig.add_axes(ax2)
    patches = []
    # add a rectangle
    x0 = 0.
    y0 = 0.01
    rectl = 0.0909  # 1/11
    recth = 0.99
    step = 0.
    for i, eachkey in enumerate(color_lst_lab):

        color_bar = color_lst_bar[i]
        color_str = color_lst_lab[i]
        rect = mpatches.Rectangle((x0, y0), rectl, recth, ec = 'k', fc = color_lst[eachkey], fill = True, lw = 0.3)
        patches.append(rect)
        ax.add_patch(rect)
        strt = color_str
        if eachkey in ['Night', 'No Data']:
            x1 = x0 + (13 - len(eachkey)) / 250.
        else:
            x1 = x0 + (14 - len(eachkey)) / 250.
        y1 = y0 + 0.4

#         print(eachkey, len(eachkey))
#         if eachkey.count(' ') == 2:  # 3个单词加回车
#             i = eachkey.rfind(' ')
#             l = list(eachkey)
#             l[i] = '\n'
#             strt = ''.join(l)
#             y1 = y1 - 0.5
#         x1 = x0 + 13 - len(eachkey)
#         plt.text(x1, y1, strt, color = color_bar, ha = 'left', va = 'center', fontsize = 6.5, FontWeight = 'bold')
        plt.text(x1, y1, strt, color = color_bar, ha = 'left', va = 'center', fontsize = 11, weight = 'bold')
        x0 = x0 + rectl + step
    axis('off')


if __name__ == '__main__':

    args = sys.argv[1:]
    yaml_file = args[0]
    main(yaml_file)

