# -*- coding: utf-8 -*-

import os
import sys
import h5py
import yaml
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
# import cartopy.feature as cfeature
# from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
# 必须加这个字段，否则引用 pyplot 服务器会报错，服务器上面没有 TK
mpl.use("Agg")

'''
Created on 2019年12月20日
@author: wape2
'''
main_path, main_file = os.path.split(os.path.realpath(__file__))

plot_map_use_scatter = True


class ReadPlotYaml():
    pass


class ReadModeYaml():
    pass


class ReadInPutYaml():

    def __init__(self, in_file):
        """
        读取yaml格式配置文件
        """
        if not os.path.isfile(in_file):
            print('Not Found %s' % in_file)
            sys.exit(-1)

        with open(in_file, 'r') as stream:
            cfg = yaml.load(stream)

            self.job_name = cfg['INFO']['job_name']
            self.ymd = cfg['INFO']['ymd']
            self.ipath1 = cfg['PATH']['ipath1']
            self.ipath2 = cfg['PATH']['ipath2']
            self.opath = cfg['PATH']['opath']


color = {
    'invalid': (0., 0., 0.),  # 255-无数据-黑色
    'same': (0., 255., 127.),  # 0 绿色
    'diff': (205., 38., 38.)
}


def main(yaml_file):

    # 读取接口文件
    yaml1 = ReadInPutYaml(yaml_file)
    ipath1 = yaml1.ipath1
    ipath2 = yaml1.ipath2
    opath = yaml1.opath

    data1 = read_hdf5(ipath1)
    data2 = read_hdf5(ipath2)

    same_idx = data1 == data2
    diff_idx = data1 != data2
    diff_value = data1 - data2
    diff_data = np.full(data1.shape, fill_value=-1, dtype='i1')
    diff_data[same_idx] = 0
    diff_data[diff_idx] = 1
    oname_t = os.path.basename(ipath1)
    ofig1 = os.path.join(opath, oname_t.split('.')[0] + '_difference.png')
    ofig2 = os.path.join(opath, oname_t.split('.')[0] + '_statistics.png')
    plot_image_difference(diff_value, ofig1)
    idx1 = np.where(diff_data == 0)
    idx2 = np.where(diff_data == 1)
    diff_percent = len(idx1[0]) / data1.size * 100
    same_percent = len(idx2[0]) / data1.size * 100
    plot_image_statistics(diff_value, ofig2, diff_percent, same_percent)


def read_hdf5(ifile):

    h5r = h5py.File(ifile, 'r')
    data = h5r.get('SNC')[:]
    h5r.close()
    return data


def plot_image_difference(r, out_file):
    row, col = np.shape(r)
    width = col / 100.
    length = row / 100.
    dpi = 100
    fig = plt.figure(figsize=(width, length), dpi=dpi)  # china

    #     rgb = np.stack([r, g, b], axis = 2)
    #     rgb = np.stack([r], axis = 2)

    plt.imshow(r, cmap='jet')

    plt.axis('off')

    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)

    out_dir = os.path.dirname(out_file)

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    fig.savefig(out_file, dpi=dpi)
    fig.clear()
    plt.close()
    print('>>> {}'.format(out_file))


def plot_image_statistics(r, out_file, diff_p, same_p):
    color_list = ['#00FF7F', '#CD2626', '#000000']
    # 设置色标的最大最小值
    #     norm = mpl.colors.Normalize(vmin = 0, vmax = 255)
    mycolormap = mpl.colors.ListedColormap(color_list, 'indexed')
    bounds = [0, 0.1, 1.1, 255.1]

    norm = mpl.colors.BoundaryNorm(bounds, mycolormap.N)
    row, col = np.shape(r)
    width = col / 100.
    length = row / 100.
    dpi = 100
    print(width, length)
    fig = plt.figure(figsize=(6, 6), dpi=dpi)  # china

    #     rgb = np.stack([r, g, b], axis = 2)
    #     rgb = np.stack([r], axis = 2)
    plt.imshow(r, cmap=mycolormap, norm=norm)
    plt.text(30, 30, 'same point: %0.1f %%' %
             same_p, ha='left', va='center', fontsize=8)
    plt.text(30, 60, 'diff point: %0.1f %%' %
             diff_p, ha='left', va='center', fontsize=8)
    plt.axis('off')

    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)

    out_dir = os.path.dirname(out_file)

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    fig.savefig(out_file, dpi=dpi)
    fig.clear()
    plt.close()
    print('>>> {}'.format(out_file))


def rgb_image(rgb_data, out_fig):
    # 绘图
    dshape = rgb_data.shape
    arryR = np.full(dshape, 255, dtype='uint8')
    arryG = np.full(dshape, 255, dtype='uint8')
    arryB = np.full(dshape, 255, dtype='uint8')
    print(type(rgb_data[0, 0]))

    mask = (rgb_data == 255)
    arryR[mask], arryG[mask], arryB[mask] = color['invalid']

    mask = (rgb_data == 0)
    arryR[mask], arryG[mask], arryB[mask] = color['same']

    mask = (rgb_data == 1)
    arryR[mask], arryG[mask], arryB[mask] = color['diff']

    # 3通道合成
    imr = Image.fromarray(arryR.astype('uint8'))
    img = Image.fromarray(arryG.astype('uint8'))
    imb = Image.fromarray(arryB.astype('uint8'))
    im = Image.merge('RGB', (imr, img, imb))  # color image

    print(out_fig)
    im.save(out_fig)


if __name__ == '__main__':
    args = sys.argv[1:]
    yaml_file = args[0]
    main(yaml_file)
