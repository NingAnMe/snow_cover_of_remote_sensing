# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from configobj import ConfigObj
from qiae_lib.pb_csc_crontrol import run_command, run_command_parallel
from qiae_lib.pb_csc_crontrol import get_args, get_cmd_list
from qiae_lib.pb_csc_crontrol import get_job_name_list, get_job_step_list, get_job_time_list
from qiae_lib.pb_csc_crontrol import SocketServer, LogServer
from qiae_lib.pb_io import write_yaml_file, str_format
import re
import os
import sys
import glob
import warnings
import shutil

# 获取程序所在目录位置
g_path, _ = os.path.split(os.path.realpath(__file__))
os.chdir(g_path)


def log_str2str(job_name, job_id, ymd, hms, status, buf):
    lstr = '{:<18} {:<9} {:<9} {:<9} {:<8} {:<18}'.format(
        job_name, job_id, ymd, hms, status, buf)
    return lstr


def get_job_id_func(job_id):
    """
    u 返回jobid对应的函数名称 ，jobid唯一性
    :return:
    """
    job_id_func = {
        "job_0110": job_0110,
        "job_0210": job_0210,
        #         "job_0310": job_0310,
        #         "job_0311": job_0311,
        "job_0311": job_0311,
        "job_1010": job_1010,
    }
    return job_id_func.get(job_id)


def main():
    # 获取必要的三个参数(卫星对，作业编号，日期范围 , 端口, 线程, 数据补侠士每次订购天数)
    job_name, job_step, job_time, job_cfg, job_port, threads, timeout, rewrite, visfile, irfile, version = get_args()
    # 端口大于0 就开启
    if job_port > 0:
        sserver = SocketServer()
        if sserver.createSocket(job_port) == False:
            sserver.closeSocket(job_port)
            sys.exit(-1)

    # 输出模块增加版本信息命名
    job_cfg = ConfigObj(job_cfg, encoding='UTF8')
    job_cfg['PATH']['version'] = version
    job_cfg.write()

    # 是否运行作业，作业方式（单节点并行和集群并行）
    run_jobs = job_cfg['CROND']['run_jobs'].lower()
    run_mode = job_cfg['CROND']['run_mode']
    interface = job_cfg['PATH']['OUT']['interface']

    # 日志目录
    path_log = job_cfg['PATH']['OUT']['log']

    # 1 获取卫星对清单
    job_name_list = get_job_name_list(job_name, job_cfg)
    # 2 获取作业流清单
    job_step_list = get_job_step_list(job_name_list, job_step, job_cfg)
    # 3 获取日期的清单
    job_time_list = get_job_time_list(job_name_list, job_time, job_cfg)

    #  开始根据卫星对处理作业流
    for job_name in job_name_list:  # 卫星对
        for job_id in job_step_list[job_name]:  # 作业编号
            process_name = job_cfg['BAND_JOB_MODE'][job_id]  # 作业进程
            for date_s, date_e in job_time_list[job_name]:  # 处理时间
                get_job_id_func(job_id)(job_name, job_id, date_s,
                                        date_e, job_cfg, rewrite, visfile, irfile)

                # 开始获取执行指令信息
                if 'on' in run_jobs:
                    cmd_list = get_cmd_list(
                        process_name, job_name, job_id, date_s, date_e, interface)
                    if 'onenode' in run_mode:
                        run_command(cmd_list, threads, timeout,
                                    path_log, job_name, job_id)
                    elif 'cluster' in run_mode:
                        run_command_parallel(cmd_list, threads)
                    else:
                        print('error: parallel_mode args input onenode or cluster')
                        sys.exit(-1)

# 以上部分完全可复用，在不同不摸直接复制即可


def job_0110(job_name, job_id, date_s, date_e, job_cfg, rewrite, visfile, irfile):
    date1 = datetime.strptime(date_s.strftime('%Y%m%d'), '%Y%m%d')
    date2 = datetime.strptime(date_e.strftime('%Y%m%d'), '%Y%m%d')
    while date1 <= date2:
        ymd = date1.strftime('%Y%m%d')
        create_job_0110(job_name, job_id, ymd, job_cfg,
                        rewrite, visfile, irfile)
        date1 = date1 + relativedelta(days=1)


def create_job_0110(job_name, job_id, ymd, job_cfg, rewrite, visfile, irfile):
    # 调度文件中的路径信息
    yy = ymd[0:4]
    mm = ymd[4:6]
    dd = ymd[6:8]

    # 输入信息
    ipath_geo = None
    ipath_l1b = job_cfg['PAIRS'][job_name]['ipath_l1b']
    ipath_clm = job_cfg['PAIRS'][job_name]['ipath_clm']
    if 'ipath_geo' in job_cfg['PAIRS'][job_name]:
        ipath_geo = job_cfg['PAIRS'][job_name]['ipath_geo']

    ipath_l1b = str_format(ipath_l1b, {'YYYY': yy, 'MM': mm, 'DD': dd})
    ipath_clm = str_format(ipath_clm, {'YYYY': yy, 'MM': mm, 'DD': dd})
    ipath_geo = str_format(ipath_geo, {'YYYY': yy, 'MM': mm, 'DD': dd})

    # 输出信息
    opath_granule = job_cfg['PATH']['MID']['granule']
    opath_yaml = job_cfg['PATH']['OUT']['interface']

    opath_granule = str_format(
        opath_granule, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
    opath_yaml = str_format(
        opath_yaml, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
    opath_yaml = os.path.join(opath_yaml, job_id, ymd)

    # 接口文件输出目录创建
    if not os.path.isdir(opath_yaml):
        os.makedirs(opath_yaml)

    # 日志信息
    path_log = job_cfg['PATH']['OUT']['log']
    path_log = os.path.join(path_log, job_name, job_id, ymd)
    name_log = '%s.log' % ymd
    # 清理日志
    shutil.rmtree(path_log, ignore_errors=True)
    vars_log = LogServer(path_log, name_log)

    # 清理接口文件
    if rewrite:
        shutil.rmtree(opath_yaml, ignore_errors=True)

    # 遍历文件
    flist_l1b = glob.glob('%s/*%s*.HDF' % (ipath_l1b, ymd))
    flist_clm = glob.glob('%s/*%s*.HDF' % (ipath_clm, ymd))
    flist_geo = glob.glob('%s/*%s*.HDF' % (ipath_geo, ymd))

    l1b_nums = len(flist_l1b)
    clm_nums = len(flist_clm)
    geo_nums = len(flist_geo)
    if l1b_nums <= 0:
        lstr = log_str2str(job_name, job_id, ymd, '--', '--',
                           u'l1b file nums: %s' % l1b_nums)
        vars_log.error(lstr)
        return
    if clm_nums <= 0:
        lstr = log_str2str(job_name, job_id, ymd, '--', '--',
                           u'clm file nums: %s' % clm_nums)
        vars_log.error(lstr)
        return
    if geo_nums <= 0:
        lstr = log_str2str(job_name, job_id, ymd, '--', '--',
                           u'geo file nums: %s' % geo_nums)
        vars_log.error(lstr)

    # 把L1数据放入字典
    reg = '.*(\d{8})_(\d{4}).*.HDF'
    flist_l1b_dict = dict()
    for each in flist_l1b:
        file_name = os.path.basename(each)
        mreg = re.match(reg, file_name)
        if mreg:
            key_wd = '{}_{}'.format(mreg.group(1), mreg.group(2))
            flist_l1b_dict[key_wd] = each

    # 把云检测数据放入字典
    reg = '.*(\d{8})_(\d{4}).*.HDF'
    flist_clm_dict = dict()
    for each in flist_clm:
        file_name = os.path.basename(each)
        mreg = re.match(reg, file_name)
        if mreg:
            key_wd = '{}_{}'.format(mreg.group(1), mreg.group(2))
            flist_clm_dict[key_wd] = each

    # 把GEO数据放入字典
    reg = '.*(\d{8})_(\d{4}).*.HDF'
    flist_geo_dict = dict()
    for each in flist_geo:
        file_name = os.path.basename(each)
        mreg = re.match(reg, file_name)
        if mreg:
            key_wd = '{}_{}'.format(mreg.group(1), mreg.group(2))
            flist_geo_dict[key_wd] = each

    # 交集
    sat = job_name.split('_')[0]
    if sat in ['FY3D', 'FY3C']:
        key_wd_cross = flist_l1b_dict.keys() & flist_geo_dict.keys() & flist_clm_dict.keys()
    else:
        key_wd_cross = flist_l1b_dict.keys() & flist_clm_dict.keys()

    # 交集是0的记录日志
    key_wd_nums = len(key_wd_cross)
    if key_wd_nums <= 0:
        lstr = log_str2str(job_name, job_id, ymd, '--', '--',
                           u'cross time nums: %s' % key_wd_nums)
        vars_log.error(lstr)
        return

    for key in sorted(key_wd_cross):

        ymd = key.split('_')[0]
        hms = key.split('_')[1] + '00'
        full_opath_yaml = os.path.join(opath_yaml, '%s%s.yaml' % (ymd, hms))

        if os.path.isfile(opath_yaml):
            lstr = log_str2str(job_name, job_id, ymd, hms, 'skip', '--')
            vars_log.info(lstr)
            continue

        ifile_l1b = flist_l1b_dict.get(key)
        ifile_clm = flist_clm_dict.get(key)
        ifile_geo = flist_geo_dict.get(key)

        # 输出接口文件
        yaml_dict = {'INFO': {'job_name': job_name, 'ymd': ymd, 'hms': hms, 'rewrite': rewrite},
                     'PATH': {'ipath_l1b': ifile_l1b, 'ipath_geo': ifile_geo,
                              'ipath_clm': ifile_clm, 'opath': opath_granule},
                     'CALFILE': {'visfile': visfile, 'irfile': irfile}
                     }
        try:
            write_yaml_file(yaml_dict, full_opath_yaml)
            lstr = log_str2str(job_name, job_id, ymd, hms, 'sucess', '--')
            vars_log.info(lstr)
        except Exception as e:
            lstr = log_str2str(job_name, job_id, ymd, hms, 'failed', str(e))
            vars_log.info(lstr)


def job_0210(job_name, job_id, date_s, date_e, job_cfg, rewrite, visfile, irfile):
    date1 = datetime.strptime(date_s.strftime('%Y%m%d'), '%Y%m%d')
    date2 = datetime.strptime(date_e.strftime('%Y%m%d'), '%Y%m%d')
    while date1 <= date2:
        ymd = date1.strftime('%Y%m%d')
        create_job_0210(job_name, job_id, ymd, job_cfg, rewrite)
        date1 = date1 + relativedelta(days=1)


def create_job_0210(job_name, job_id, ymd, job_cfg, rewrite):
    """
    日合成代码
    """
    # 调度文件中的路径信息
    yy = ymd[0:4]
    mm = ymd[4:6]
    dd = ymd[6:8]

    # 输入信息
    ipath_granule = job_cfg['PATH']['MID']['granule']

    # 输出信息
    opath_daily = job_cfg['PATH']['MID']['daily']
    opath_yaml = job_cfg['PATH']['OUT']['interface']

    ipath_granule = str_format(
        ipath_granule, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
    opath_daily = str_format(
        opath_daily, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
    opath_yaml = str_format(
        opath_yaml, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
    opath_yaml = os.path.join(opath_yaml, job_id, ymd)
    # 接口文件输出目录创建
    if not os.path.isdir(opath_yaml):
        os.makedirs(opath_yaml)

    # 日志信息
    path_log = job_cfg['PATH']['OUT']['log']
    path_log = os.path.join(path_log, job_name, job_id, ymd[:4])
    name_log = '%s.log' % ymd
    # 清理日志
    shutil.rmtree(path_log, ignore_errors=True)
    vars_log = LogServer(path_log, name_log)

    # 清理接口文件
    if rewrite:
        shutil.rmtree(opath_yaml, ignore_errors=True)

    # 遍历目录
    file_list = glob.glob('%s/*%s*.HDF5' % (ipath_granule, ymd))
    file_list.sort()
    l1b_nums = len(file_list)
    if l1b_nums <= 0:
        lstr = log_str2str(job_name, job_id, ymd, '--',
                           'failed', u'l1b file nums: %s' % l1b_nums)
        vars_log.error(lstr)
        return

    # 输出接口文件
    yaml_dict = {'INFO': {'job_name': job_name, 'ymd': ymd, 'rewrite': rewrite},
                 'PATH': {'ipath': file_list, 'opath': opath_daily}}

    hms = '000000'
    full_opath_yaml = os.path.join(opath_yaml, '%s%s.yaml' % (ymd, hms))

    try:
        write_yaml_file(yaml_dict, full_opath_yaml)
        lstr = log_str2str(job_name, job_id, ymd, hms, 'sucess', '--')
        vars_log.info(lstr)
    except Exception as e:
        lstr = log_str2str(job_name, job_id, ymd, hms, 'failed', str(e))
        vars_log.info(lstr)

# def job_0310(job_name, job_id, date_s, date_e, job_cfg, rewrite, visfile, irfile):
#     """
#     MODIS的时次产品绘图
#     """
#     date1 = datetime.strptime(date_s.strftime('%Y%m%d'), '%Y%m%d')
#     date2 = datetime.strptime(date_e.strftime('%Y%m%d'), '%Y%m%d')
#     while date1 <= date2:
#         ymd = date1.strftime('%Y%m%d')
#         jjj = date1.strftime('%j')
#         create_job_0310(job_name, job_id, ymd, jjj, job_cfg, rewrite)
#         date1 = date1 + relativedelta(days = 1)
#
#
# def create_job_0310(job_name, job_id, ymd, jjj, job_cfg, rewrite):
#
#     # 调度文件中的路径信息
#     yy = ymd[0:4]
#     mm = ymd[4:6]
#     dd = ymd[6:8]
#
#     # 输入信息
#     ipath_hourly = job_cfg['PAIRS'][job_name]['ipath_hourly']
#
#     # 输出信息
#     opath_hourly = job_cfg['PATH']['MID']['granule']
#     opath_yaml = job_cfg['PATH']['OUT']['interface']
#
#     ipath_hourly = str_format(ipath_hourly, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
#     opath_hourly = str_format(opath_hourly, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
#     opath_yaml = str_format(opath_yaml, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
#     opath_yaml = os.path.join(opath_yaml, job_id, ymd)
#     # 接口文件输出目录创建
#     if not os.path.isdir(opath_yaml):
#         os.makedirs(opath_yaml)
#
#     # 日志信息
#     path_log = job_cfg['PATH']['OUT']['log']
#     path_log = os.path.join(path_log, job_name, job_id, ymd[:4])
#     name_log = '%s.log' % ymd
#     # 清理日志
#     shutil.rmtree(path_log, ignore_errors = True)
#     vars_log = LogServer(path_log, name_log)
#
#     # 清理接口文件
#     if rewrite:
#         shutil.rmtree(opath_yaml, ignore_errors = True)
#
#     # 遍历目录
#     file_list = glob.glob('%s/*A%s%s*.hdf' % (ipath_hourly, ymd[:4], jjj))
#     file_list.sort()
#     l1b_nums = len(file_list)
#     if l1b_nums <= 0:
#         lstr = log_str2str(job_name, job_id, ymd, '--', 'failed', u'file nums: %s' % l1b_nums)
#         vars_log.error(lstr)
#         return
#
#     # 输出接口文件A2013121.0040.
#     reg = '.*A(\d{7}).(\d{4}).*.hdf'
#
#     for each in file_list:
#         file_name = os.path.basename(each)
#         mreg = re.match(reg, file_name)
#         if mreg:
#             hm = mreg.group(2)
#         hms = '%s00' % hm
#         full_opath_yaml = os.path.join(opath_yaml, '%s%s.yaml' % (ymd, hms))
#         yaml_dict = {'INFO': {'job_name': job_name, 'ymd': ymd, 'rewrite': rewrite},
#                  'PATH': {'ipath': each, 'opath': opath_hourly}}
#         try:
#             write_yaml_file(yaml_dict, full_opath_yaml)
#             lstr = log_str2str(job_name, job_id, ymd, hms, 'sucess', '--')
#             vars_log.info(lstr)
#         except Exception as e:
#             lstr = log_str2str(job_name, job_id, ymd, hms, 'failed', str(e))
#             vars_log.info(lstr)
#
#
# def job_0311(job_name, job_id, date_s, date_e, job_cfg, rewrite, visfile, irfile):
#     """
#     MOD04_L2的日产品绘图
#     """
#     date1 = datetime.strptime(date_s.strftime('%Y%m%d'), '%Y%m%d')
#     date2 = datetime.strptime(date_e.strftime('%Y%m%d'), '%Y%m%d')
#     while date1 <= date2:
#         ymd = date1.strftime('%Y%m%d')
#         jjj = date1.strftime('%j')
#         create_job_0311(job_name, job_id, ymd, jjj, job_cfg, rewrite)
#         date1 = date1 + relativedelta(days = 1)
#
#
# def create_job_0311(job_name, job_id, ymd, jjj, job_cfg, rewrite):
#
#     # 调度文件中的路径信息
#     yy = ymd[0:4]
#     mm = ymd[4:6]
#     dd = ymd[6:8]
#
#     # 输入信息
#     ipath_daily = job_cfg['PAIRS'][job_name]['ipath_daily']
#
#     # 输出信息
#     opath_daily = job_cfg['PATH']['MID']['daily']
#     opath_yaml = job_cfg['PATH']['OUT']['interface']
#
#     ipath_daily = str_format(ipath_daily, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
#     opath_daily = str_format(opath_daily, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
#     opath_yaml = str_format(opath_yaml, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
#     opath_yaml = os.path.join(opath_yaml, job_id, ymd)
#     # 接口文件输出目录创建
#     if not os.path.isdir(opath_yaml):
#         os.makedirs(opath_yaml)
#
#     # 日志信息
#     path_log = job_cfg['PATH']['OUT']['log']
#     path_log = os.path.join(path_log, job_name, job_id, ymd[:4])
#     name_log = '%s.log' % ymd
#     # 清理日志
#     shutil.rmtree(path_log, ignore_errors = True)
#     vars_log = LogServer(path_log, name_log)
#
#     # 清理接口文件
#     if rewrite:
#         shutil.rmtree(opath_yaml, ignore_errors = True)
#
#     # 遍历目录
#     file_list = glob.glob('%s/*A%s%s*.hdf' % (ipath_daily, ymd[:4], jjj))
#     file_list.sort()
#     l1b_nums = len(file_list)
#     if l1b_nums <= 0:
#         lstr = log_str2str(job_name, job_id, ymd, '--', 'failed', u'file nums: %s' % l1b_nums)
#         vars_log.error(lstr)
#         return
#
#     # 输出接口文件
#     yaml_dict = {'INFO': {'job_name': job_name, 'ymd': ymd, 'rewrite': rewrite},
#                  'PATH': {'ipath': file_list, 'opath': opath_daily}}
#
#     hms = '000000'
#     full_opath_yaml = os.path.join(opath_yaml, '%s%s.yaml' % (ymd, hms))
#
#     try:
#         write_yaml_file(yaml_dict, full_opath_yaml)
#         lstr = log_str2str(job_name, job_id, ymd, hms, 'sucess', '--')
#         vars_log.info(lstr)
#     except Exception as e:
#         lstr = log_str2str(job_name, job_id, ymd, hms, 'failed', str(e))
#         vars_log.info(lstr)


def job_0311(job_name, job_id, date_s, date_e, job_cfg, rewrite, visfile, irfile):
    """
    AVHRR的日产品绘图
    """
    date1 = datetime.strptime(date_s.strftime('%Y%m%d'), '%Y%m%d')
    date2 = datetime.strptime(date_e.strftime('%Y%m%d'), '%Y%m%d')
    while date1 <= date2:
        ymd = date1.strftime('%Y%m%d')
        jjj = date1.strftime('%j')
        create_job_0311(job_name, job_id, ymd, jjj, job_cfg, rewrite)
        date1 = date1 + relativedelta(days=1)


def create_job_0311(job_name, job_id, ymd, jjj, job_cfg, rewrite):

    # 调度文件中的路径信息
    yy = ymd[0:4]
    mm = ymd[4:6]
    dd = ymd[6:8]

    # 输入信息
    ipath_daily = job_cfg['PAIRS'][job_name]['ipath_daily']

    # 输出信息
    opath_daily = job_cfg['PATH']['MID']['daily']
    opath_yaml = job_cfg['PATH']['OUT']['interface']

    ipath_daily = str_format(
        ipath_daily, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
    opath_daily = str_format(
        opath_daily, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
    opath_yaml = str_format(
        opath_yaml, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
    opath_yaml = os.path.join(opath_yaml, job_id, ymd)
    # 接口文件输出目录创建
    if not os.path.isdir(opath_yaml):
        os.makedirs(opath_yaml)

    # 日志信息
    path_log = job_cfg['PATH']['OUT']['log']
    path_log = os.path.join(path_log, job_name, job_id, ymd[:4])
    name_log = '%s.log' % ymd
    # 清理日志
    shutil.rmtree(path_log, ignore_errors=True)
    vars_log = LogServer(path_log, name_log)

    # 清理接口文件
    if rewrite:
        shutil.rmtree(opath_yaml, ignore_errors=True)

    # 遍历目录
    file_list = glob.glob('%s/*A%s%s*.hdf' % (ipath_daily, ymd[:4], jjj))
    file_list.sort()
    l1b_nums = len(file_list)
    if l1b_nums <= 0:
        lstr = log_str2str(job_name, job_id, ymd, '--',
                           'failed', u'file nums: %s' % l1b_nums)
        vars_log.error(lstr)
        return

    # 输出接口文件
    yaml_dict = {'INFO': {'job_name': job_name, 'ymd': ymd, 'rewrite': rewrite},
                 'PATH': {'ipath': file_list, 'opath': opath_daily}}

    hms = '000000'
    full_opath_yaml = os.path.join(opath_yaml, '%s%s.yaml' % (ymd, hms))

    try:
        write_yaml_file(yaml_dict, full_opath_yaml)
        lstr = log_str2str(job_name, job_id, ymd, hms, 'sucess', '--')
        vars_log.info(lstr)
    except Exception as e:
        lstr = log_str2str(job_name, job_id, ymd, hms, 'failed', str(e))
        vars_log.info(lstr)


def job_1010(job_name, job_id, date_s, date_e, job_cfg, rewrite, visfile, irfile):
    """
    不同版本产品的差值和统计值计算
    """
    date1 = datetime.strptime(date_s.strftime('%Y%m%d'), '%Y%m%d')
    date2 = datetime.strptime(date_e.strftime('%Y%m%d'), '%Y%m%d')
    while date1 <= date2:
        ymd = date1.strftime('%Y%m%d')
        jjj = date1.strftime('%j')
        create_job_1010(job_name, job_id, ymd, jjj, job_cfg, rewrite)
        date1 = date1 + relativedelta(days=1)


def create_job_1010(job_name, job_id, ymd, jjj, job_cfg, rewrite):

    # 调度文件中的路径信息
    yy = ymd[0:4]
    mm = ymd[4:6]
    dd = ymd[6:8]
    # 输入信息
    ipath_h1 = job_cfg['PAIRS'][job_name]['ipath_orbit1']
    ipath_h2 = job_cfg['PAIRS'][job_name]['ipath_orbit2']
    ipath_h1 = str_format(ipath_h1, {'YYYY': yy, 'MM': mm, 'DD': dd})
    ipath_h2 = str_format(ipath_h2, {'YYYY': yy, 'MM': mm, 'DD': dd})
    print(ipath_h1)
    print(ipath_h2)
    # 输出信息
    opath_check = job_cfg['PATH']['OUT']['check']
    opath_check = str_format(
        opath_check, {'JOBNAME': job_name, 'YYYY': yy, 'MM': mm, 'DD': dd})
    # 输出接口
    opath_yaml = job_cfg['PATH']['OUT']['interface']
    opath_yaml = str_format(opath_yaml, {'JOBNAME': job_name})
    opath_yaml = os.path.join(opath_yaml, job_id, ymd)

    # 接口文件输出目录创建
    if not os.path.isdir(opath_yaml):
        os.makedirs(opath_yaml)

    # 日志信息
    path_log = job_cfg['PATH']['OUT']['log']
    path_log = os.path.join(path_log, job_name, job_id, ymd[:4])
    name_log = '%s.log' % ymd
    # 清理日志
    shutil.rmtree(path_log, ignore_errors=True)
    vars_log = LogServer(path_log, name_log)

    # 清理接口文件
    if rewrite:
        shutil.rmtree(opath_yaml, ignore_errors=True)

    # 遍历目录
    file_list1 = glob.glob('%s/*.HDF5' % (ipath_h1))
    file_list1.sort()
    file_list2 = glob.glob('%s/*.HDF5' % (ipath_h2))
    file_list2.sort()

    namelist1 = [os.path.basename(each) for each in file_list1]
    namelist2 = [os.path.basename(each) for each in file_list2]
    corss_namelist = list(set(namelist1) & set(namelist2))
    nums1 = len(corss_namelist)
    if nums1 <= 0:
        lstr = log_str2str(job_name, job_id, ymd, '--',
                           'failed', u'file nums: %d' % (nums1))
        vars_log.error(lstr)
        return
#     cross_file_list = list(set(file_list1).intersection(set(file_list2)))
    # 输出接口文件
    pattern = '.*(\d{8})_(\d{4})'
    for each in corss_namelist:
        print(each)
        ifile1 = os.path.join(ipath_h1, each)
        ifile2 = os.path.join(ipath_h2, each)
        yaml_dict = {'INFO': {'job_name': job_name, 'ymd': ymd, 'rewrite': rewrite},
                     'PATH': {'ipath1': ifile1, 'ipath2': ifile2, 'opath': opath_check}}
        m = re.match(pattern, each)
        if m:
            hms = m.group(2)
            ofile_yaml = os.path.join(opath_yaml, '%s%s.yaml' % (ymd, hms))

            try:
                write_yaml_file(yaml_dict, ofile_yaml)
                lstr = log_str2str(job_name, job_id, ymd, hms, 'sucess', '--')
                vars_log.info(lstr)
            except Exception as e:
                lstr = log_str2str(job_name, job_id, ymd,
                                   hms, 'failed', str(e))
                vars_log.info(lstr)


if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    # 运行命令如下
    main()
