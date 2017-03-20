#coding:utf-8
from django.shortcuts import render,redirect,get_object_or_404,render_to_response
from .models import *
from django.http import  HttpResponseRedirect,HttpResponse
from django.db import connection
from SQLclass import Newmofang
import datetime
import json
import psycopg2
import MySQLdb
# Create your views here.
import sys
reload(sys)
sys.setdefaultencoding('utf8')


###全平台模块
def platform(request):

    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).date().strftime('%Y%m%d')###查询开始时间
    end_date = (datetime.datetime.now()-datetime.timedelta(days=1)).date().strftime('%Y%m%d')###查询结束时间

    last_week_start_date = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().isoweekday()+6)).date().strftime('%Y%m%d')###最近一周的开始日期
    last_week_end_date = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().isoweekday())).date().strftime('%Y%m%d')###最近一周的结束日期

    ###查询月vv
    vv_month_result = Newmofang(searchtype='vv_platform_month',end_date=end_date).sql_query()

    ###查询日vv
    vv_day_result = Newmofang(searchtype='vv_platform_day',start_date=start_date,end_date=end_date).sql_query()
    ###查询日uv
    uv_day_result = Newmofang(searchtype='uv_platform_day',start_date=start_date,end_date=end_date).sql_query()
    ###查询日pv
    pv_day_result = Newmofang(searchtype='pv_platform_day',start_date=start_date,end_date=end_date).sql_query()
    ###查询日时长
    duration_day_result = Newmofang(searchtype='duration_platform_day',start_date=start_date,end_date=end_date).sql_query()
    print duration_day_result


    ###查询频道vv、uv
    date_list = Newmofang(start_date=start_date, end_date=end_date).datetime_process()
    terminal_list = Newmofang().bid_dict.values()
    vv_terminal_day_result = Newmofang(searchtype='vv_terminal_day',start_date=start_date,end_date=end_date).sql_query()
    # print vv_terminal_day_result
    uv_terminal_day_result = Newmofang(searchtype='uv_terminal_day',start_date=start_date,end_date=end_date).sql_query()


    ###查询频道vv、uv
    channel_list = Newmofang().cid_dict.values()
    vv_channel_day_result = Newmofang(searchtype='vv_channel_day', start_date=start_date, end_date=end_date).sql_query()
    uv_channel_day_result = Newmofang(searchtype='uv_channel_day', start_date=start_date, end_date=end_date).sql_query()

    ###查询dau
    dau_platform_day_result = Newmofang(searchtype='dau_platform_day', start_date=start_date, end_date=end_date).sql_query()

    ###查询最近一周的日均uv、日均vv
    uv_pid_day_avg_result = Newmofang(searchtype='uv_pid_day_avg', start_date=last_week_start_date, end_date=last_week_end_date).sql_query()###合集日均uvtop20
    pid_str = ','.join(map(lambda x: str(x[0]), uv_pid_day_avg_result))###合集id列表，供vv查询用
    vv_pid_day_avg_result = Newmofang(searchtype='vv_pid_day_avg', start_date=last_week_start_date,pid_str=pid_str,end_date=last_week_end_date).sql_query()  ###合集日均uvtop20

    pid_day_avg_result_dict = pid_day_avg_result_process(pid_str, vv_pid_day_avg_result, uv_pid_day_avg_result)
    print pid_day_avg_result_dict
    ###数据转化为列表传入前端
    overview_platform_day_dict = overview_platform_day_process(date_list,end_date,vv_day_result,uv_day_result,pv_day_result,duration_day_result)###往日概览数据
    vv_month_date, vv_month_lastyear, vv_month_thisyear = vv_platform_month_process(vv_month_result=vv_month_result)###平台月度uv数据
    vv_day_date, vv_day_data, uv_day_data,vv_day_perperson = vv_platform_day_process(vv_day_result=vv_day_result,uv_day_result=uv_day_result)###全平台日vv、uv、人均vv数据
    vv_terminal_day_dict = vv_terminal_day_process(vv_terminal_day_result=vv_terminal_day_result,date_list=date_list,terminal_list=terminal_list)  ###分端vv变化
    uv_terminal_day_dict = uv_terminal_day_process(uv_terminal_day_result=uv_terminal_day_result, date_list=date_list,terminal_list=terminal_list)  ###分端uv变化
    vv_channel_day_dict = vv_channel_day_process(vv_channel_day_result=vv_channel_day_result, date_list=date_list,channel_list=channel_list)  ###分频道vv变化
    uv_channel_day_dict = uv_channel_day_process(uv_channel_day_result=uv_channel_day_result, date_list=date_list,channel_list=channel_list)  ###分频道uv变化
    dau_day_data, uv_ration_day_data = dau_platform_day_process(dau_platform_day_result=dau_platform_day_result,uv_day_data=uv_day_data)


    return render(request, 'index.html', {'vv_day_date':json.dumps(vv_day_date),'vv_day_data':json.dumps(vv_day_data),
                                       'uv_day_data': json.dumps(uv_day_data),'vv_day_perperson':json.dumps(vv_day_perperson),
                                       'vv_month_date':json.dumps(vv_month_date),'vv_month_lastyear':json.dumps(vv_month_lastyear),
                                       'vv_month_thisyear':json.dumps(vv_month_thisyear),'vv_terminal_day_dict':vv_terminal_day_dict,
                                       'uv_terminal_day_dict':uv_terminal_day_dict,'vv_channel_day_dict':vv_channel_day_dict,
                                       'uv_channel_day_dict':uv_channel_day_dict,'dau_day_data':dau_day_data,'uv_ration_day_data':uv_ration_day_data,
                                        'overview_platform_day_dict':overview_platform_day_dict,'pid_day_avg_result_dict':pid_day_avg_result_dict})


def ltt(request):
    return render(request,'indexThree.html')




def data_format(result,format_type):###sql返回结果处理
    if result != []:
        date_list = [each[0] for each in result]###日期列表
        if format_type == 'normal':
            data_list = [round(each[1]/10000,1) for each in result]###数据列表
        elif format_type == 'duration':
            data_list = [round(each[1] / 60, 1) for each in result]  ###数据列表
        return date_list,data_list###返回x轴时间列表和y轴值列表

def overview_platform_day_process(date_list,end_date,vv_day_result,uv_day_result,pv_day_result,duration_day_result):###处理往日概况模块,暂定为昨日vv、uv、pv、时长数据
    month_to_month_date = (datetime.datetime.now() - datetime.timedelta(days=2)).date().strftime('%Y%m%d')###环比的日期，2天前
    year_to_year_date = (datetime.datetime.now() - datetime.timedelta(days=8)).date().strftime('%Y%m%d')###同比的日期，8天前
    days_ago_location = date_list.index(end_date)###昨日日期在日期列表中的位置
    month_to_month_location = date_list.index(month_to_month_date)###环比日期在日期列表中的位置
    year_to_year_location = date_list.index(year_to_year_date)###同比日期在日期列表中的位置
    print days_ago_location,month_to_month_location,year_to_year_location
    vv_day_data = data_format(vv_day_result,format_type='normal')[1]###获取vv列表
    uv_day_data = data_format(uv_day_result,format_type='normal')[1]###获取uv列表
    vv_perperson_day_data = list(map(lambda x: round(x[0] / x[1], 1), zip(vv_day_data, uv_day_data)))###计算人均vv列表
    pv_day_data = data_format(pv_day_result,format_type='normal')[1]###获取pv列表
    duration_day_data = data_format(duration_day_result,format_type='duration')[1]###获取时长列表
    duration_perperson_day_data = list(map(lambda x: round(x[0] / x[1]/10000, 1), zip(duration_day_data, uv_day_data)))  ###计算人均观看时长列表
    data_dict = {'vv': vv_day_data, 'uv': uv_day_data, 'pv': pv_day_data, 'vv_perperson':vv_perperson_day_data,'duration_perperson': duration_perperson_day_data }
    print uv_day_data,duration_day_data,duration_perperson_day_data
    overview_platform_day_dict = {}
    ###计算概览数据,每个部分的数据均以 [昨日数据，环比，同比] 进行显示
    for key in data_dict.keys():
        x = data_dict[key]
        overview_result = [x[days_ago_location],round((x[days_ago_location]/x[month_to_month_location]-1)*100,2),round(x[days_ago_location]/x[year_to_year_location]-1,2)]
        overview_platform_day_dict[key] = overview_result
    return overview_platform_day_dict
    # overview_platform_day_dict['vv'] = [vv_day_data[days_ago_location],round(vv_day_data[days_ago_location]/vv_day_data[month_to_month_location]-1]

def pid_day_avg_result_process(pid_str,vv_pid_day_avg_result,uv_pid_day_avg_result):
    cms_result = Newmofang(pid_str=pid_str).cms_sql()
    pid_list = map(lambda x: str(x[0]), uv_pid_day_avg_result)
    pid_day_avg_result = []
    pid_day_avg_result_dict = {}
    for pid in pid_list:
        for cms_each in cms_result:
            for vv_each in vv_pid_day_avg_result:
                for uv_each in uv_pid_day_avg_result:
                    if str(pid) == str(cms_each[0]) and str(pid) == str(vv_each[0]) and str(pid) == str(uv_each[0]):
                        pid_day_avg_result.append([round(vv_each[1]),round(uv_each[1]),round(vv_each[1]/uv_each[1],1),str(cms_each[1])])
    pid_day_avg_result_dict['data'] = pid_day_avg_result
    return pid_day_avg_result_dict


def vv_platform_month_process(vv_month_result):###月vv处理
    vv_month_data = data_format(vv_month_result,format_type='normal')[1]
    ###月份列表
    vv_month_date = [str(i) + '月' for i in range(1, 13)]
    ###第一年vv
    vv_month_lastyear = vv_month_data[:12]
    vv_month_thisyear = vv_month_data[12:]
    return vv_month_date,vv_month_lastyear,vv_month_thisyear

def vv_platform_day_process(vv_day_result,uv_day_result):###日vv、uv、人均vv处理
    vv_day_date,vv_day_data = data_format(vv_day_result,format_type='normal')
    uv_day_date, uv_day_data = data_format(uv_day_result,format_type='normal')
    vv_day_perperson = list(map(lambda x:round(x[0]/x[1],1),zip(vv_day_data,uv_day_data)))
    # print ("{vv_day_data} \n {uv_day_data} \n {vv_day_perperson}").format(vv_day_data=vv_day_data,uv_day_data=uv_day_data,vv_day_perperson=vv_day_perperson)
    return vv_day_date,vv_day_data,uv_day_data,vv_day_perperson

def vv_terminal_day_process(vv_terminal_day_result,date_list,terminal_list):
    vv_terminal_day_dict = dict()###返回的数据字典，数据格式为：  {终端1：[列表1],终端2：[列表2]}
    for terminal in terminal_list:
        terminal_list = list()###每个终端对应的字典
        for date in date_list:
            for result in vv_terminal_day_result:
                if date == str(result[0]) and terminal == str(result[1]):
                    terminal_list.append(round(result[2]/10000,1))
        vv_terminal_day_dict[terminal] = terminal_list
    return vv_terminal_day_dict

def uv_terminal_day_process(uv_terminal_day_result,date_list,terminal_list):
    uv_terminal_day_dict = dict()###返回的数据字典，数据格式为：  {终端1：[列表1],终端2：[列表2]}
    for terminal in terminal_list:
        terminal_list = list()###每个终端对应的字典
        for date in date_list:
            for result in uv_terminal_day_result:
                if date == str(result[0]) and terminal == str(result[1]):
                    terminal_list.append(round(result[2]/10000,1))
        uv_terminal_day_dict[terminal] = terminal_list
    return uv_terminal_day_dict

def vv_channel_day_process(vv_channel_day_result,date_list,channel_list):
    vv_channel_day_dict = dict()###返回的数据字典，数据格式为：  {终端1：[列表1],终端2：[列表2]}
    for channel in channel_list:
        channel_list = list()###每个终端对应的字典
        for date in date_list:
            for result in vv_channel_day_result:
                if date == str(result[0]) and channel == str(result[1]):
                    channel_list.append(round(result[2]/10000,1))
        vv_channel_day_dict[channel] = channel_list
    return vv_channel_day_dict

def uv_channel_day_process(uv_channel_day_result,date_list,channel_list):
    uv_channel_day_dict = dict()###返回的数据字典，数据格式为：  {终端1：[列表1],终端2：[列表2]}
    for channel in channel_list:
        channel_list = list()###每个终端对应的字典
        for date in date_list:
            for result in uv_channel_day_result:
                if date == str(result[0]) and channel == str(result[1]):
                    channel_list.append(round(result[2]/10000,1))
        uv_channel_day_dict[channel] = channel_list
    return uv_channel_day_dict

def dau_platform_day_process(dau_platform_day_result,uv_day_data):
    ###先将sql结果转换为列表，再对应位置相除
    dau_result = data_format(dau_platform_day_result,format_type='normal')[1]
    uv_dau = zip(uv_day_data,dau_result)
    uv_ration = map(lambda x:round(x[0]/x[1],2),uv_dau)
    return dau_result,uv_ration