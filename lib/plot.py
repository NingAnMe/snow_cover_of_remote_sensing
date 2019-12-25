#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/25 10:56
# @Author  : wangpeng
import numpy as np
from PIL import Image

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

color = {
    'invalid': (0., 0., 0.),  # 255-无数据-黑色
    'sunz': (139., 0., 0.),  # 254-太阳天顶角饱和-红褐色
    'snow': (0., 238., 238.),  # 200-雪-蓝绿色
    'ice': (0., 139., 139.),  # 100-冰-青色
    'cloud': (255., 255., 255.),  # 50-云-白色
    'ocean_water': (0., 0., 139.),  # 39-海冰-深蓝色
    'land_water': (0., 0., 255.),  # 37-内陆水-蓝色
    'land': (160., 82., 45.),  # 25-陆地-褐色
    'optical': (216., 191., 216.),  # 11-暗像元-淡粉色
    'uncertain':(255, 255, 0),  # 1-不确定-黄色
    'novalue': (100., 100., 100.)  # 0-丢线-灰色
}


def ndsi_plot_map(ndsi_data, out_fig):
    # 绘图
    dshape = ndsi_data.shape
    arryR = np.full(dshape, 255, dtype = 'uint8')
    arryG = np.full(dshape, 255, dtype = 'uint8')
    arryB = np.full(dshape, 255, dtype = 'uint8')
    print(type(ndsi_data[0, 0]))

    mask = (ndsi_data == 255)
    arryR[mask], arryG[mask], arryB[mask] = color['invalid']

    mask = (ndsi_data == 254)
    arryR[mask], arryG[mask], arryB[mask] = color['sunz']

    mask = (ndsi_data == 200)
    arryR[mask], arryG[mask], arryB[mask] = color['snow']

    mask = (ndsi_data == 100)
    arryR[mask], arryG[mask], arryB[mask] = color['ice']

    mask = (ndsi_data == 50)
    arryR[mask], arryG[mask], arryB[mask] = color['cloud']

    mask = (ndsi_data == 39)
    arryR[mask], arryG[mask], arryB[mask] = color['ocean_water']

    mask = (ndsi_data == 37)
    arryR[mask], arryG[mask], arryB[mask] = color['land_water']

    mask = (ndsi_data == 25)
    arryR[mask], arryG[mask], arryB[mask] = color['land']

    mask = (ndsi_data == 11)
    arryR[mask], arryG[mask], arryB[mask] = color['optical']

    mask = (ndsi_data == 1)
    arryR[mask], arryG[mask], arryB[mask] = color['uncertain']

    mask = (ndsi_data == 0)
    arryR[mask], arryG[mask], arryB[mask] = color['novalue']
    # 3通道合成
    imr = Image.fromarray(arryR.astype('uint8'))
    img = Image.fromarray(arryG.astype('uint8'))
    imb = Image.fromarray(arryB.astype('uint8'))
    im = Image.merge('RGB', (imr, img, imb))  # color image

    print(out_fig)
    im.save(out_fig)
