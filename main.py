#coding:gbk
import os
import time
import requests
from jsonpath import jsonpath
import json
import datetime
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
ocid={"数据结构":41064,
      "线性代数":40799,
      "大学心理健康": 98680,
    "中国近代史": 44704,
    "就业指导规划": 98281,
    "英语听说" :98225,
    "英语读写 ":98205,
    "高数":19751}
now_time = str(datetime.datetime.now()).replace(" ","-").replace(":","-")[0:18]
headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
         # "Referer": "https://courseweb.ulearning.cn/",
         "Authorization": "xxxxxxxxx\"   #此处需要自己填写
         }
#定义发送邮件的函数
def send_email(data):
    msg = MIMEText(data, "html", "utf-8")
    # 邮件上显示的主题
    msg["Subject"] = "课程信息"
    # 发送邮件
    receiver=["xxxxx@qq.com","xxxxxxxx@qq.com"]   #设置收件人
    server = smtplib.SMTP_SSL("smtp.qq.com")
    server.login("xxxxxxxx@qq.com", 'axxxxxxxx')
    server.sendmail("xxxxxxxx@qq.com", receiver, msg.as_string())
    server.quit()
    # send_email()
#优学院作业数据获取
def yxy(ocid,headers,now_time):
    url = "https://courseapi.ulearning.cn/homeworks/student/v2?ocId={}&pn=1&ps=10&lang=zh"
    homework_ygq=[]  #存储已过期的作业
    homework_wgq=[]   #存储未过期的作业
    homework_fast=[]
    for i in ocid.values():
        res = requests.get(url.format(i), headers=headers)
        data = json.loads(res.text)
        # print(data)
        # print(data)
        if jsonpath(data, "$..total")[0] > 0:
            homeworklist = jsonpath(data, "$..homeworkList")[0]
            # print(homeworklist)
            work_len = len(homeworklist[0])  # 记录作业的个数,相当于循环的次数
            # print(work_len)
            for content in homeworklist:
                namew = jsonpath(content, "$..homeworkTitle")[0]  # 获取作业内容字典
                stat_time = (str(int(jsonpath(content, "$..startTime")[0]) / 1000).replace(".0", ''))  # 转换为正常的时间戳
                stat_time = str(datetime.datetime.fromtimestamp(int(stat_time))).replace(" ", "-").replace(":",
                                                                                                           "-")
                endtime = str(int(jsonpath(content, "$..endTime")[0]) / 1000).replace(".0", '')  # 转换为正常的时间戳
                endtime = str(datetime.datetime.fromtimestamp(int(endtime))).replace(" ", "-").replace(":", "-")
                # 转换为正常的时间戳
                url_time = "https://riqicha.bmcx.com/?kaishi={}&jieshu={}"  # 获取某网站查询时间间隔的接口
                res_time = requests.get(url_time.format(now_time, endtime), headers=headers)
                time_html = BeautifulSoup(res_time.text, 'lxml')  # 利用bs4处理数据
                # print(url_time.format(now_time,endtime))
                try:
                    time_difference = time_html.find_all("td", bgcolor="#FFFFFF")[0]  # 获取时间间隔数据
                    time_difference = time_difference.getText()
                    time_day=time_html.find_all("td", bgcolor="#FFFFFF")[1]   #获取天数数据，进行后期判断
                    time_day=time_day.getText()
                    time_day=float(str(time_day).replace('天',''))
                except IndexError:
                    time_difference = "已过期"
                if time_difference=='已过期':    #对数据进行分类，分为已结束和未结束的作业
                    con_g=[namew,"------开始时间：",stat_time,"------结束时间:", endtime,"-----状态:", time_difference]
                    con_g=list(map(str,con_g))
                    con_g=''.join(con_g)
                    homework_ygq.append(con_g)
                else:
                    con_g = [namew, "------开始时间：", stat_time, "------结束时间:", endtime, "-----状态:", time_difference]
                    con_g = list(map(str, con_g))
                    con_g = ''.join(con_g)
                    homework_wgq.append(con_g)
                    # print(time_day)
                    if time_day <=1 :
                        con_g = [namew, "------开始时间：", stat_time, "------结束时间:", endtime, "-----状态:", time_difference]
                        con_g = list(map(str, con_g))
                        con_g = ''.join(con_g)
                        homework_fast.append(con_g)
    # print(homework_fast)
    # homework_ygq=str(homework_ygq)
    # print(homework_wgq)
    # send_email(homework)
    return homework_wgq
    # os.system("pause")
#获取优学院课堂情况(主要以签到数据为主)
def yxy_class(ocid,headers,now_time):
    url = "https://courseapi.ulearning.cn/classActivity/stu/{}/-1?pn=1&ps=10&lang=zh"
    kc_class=[]
    for i in ocid.values():
        res = requests.get(url.format(i), headers=headers)
        data = json.loads(res.text)
        total = jsonpath(data, "$..total")[0]  # 获取内容数量
        list = jsonpath(data, '$..list')[0]
        for cont in list:
            timedisplay = jsonpath(cont, '$..timeDisplay')[0]
            if timedisplay == '已结束':
                title = jsonpath(cont, '$..title')[0]  # 获取内容title
                teacher = jsonpath(cont, "$..publisher")[0]  # 获取老师信息
                stat_time = str(jsonpath(cont, '$..startTime')[0] / 1000).replace('.0', '')
                stat_time = str(datetime.datetime.fromtimestamp(int(stat_time))).replace(" ", "-").replace(":",
                                                                                                           "-")
                url_time = "https://riqicha.bmcx.com/?kaishi={}&jieshu={}"  # 获取某网站查询时间间隔的接口
                res_time = requests.get(url_time.format(stat_time, now_time), headers=headers)
                time_html = BeautifulSoup(res_time.text, 'lxml')  # 利用bs4处理数据
                time_difference = time_html.find_all("td", bgcolor="#FFFFFF")[3]  # 获取时间间隔数据
                time_difference = time_difference.getText()
                time_difference = float(time_difference.replace('分', ''))
                if time_difference < 5.0:
                    kc_ct=['标题:', title, '  教师', 'teacher:', teacher]
                    # kc_ct=list(map(str,kc_ct))
                    kc_ct=''.join(kc_ct)
                    kc_class.append(kc_ct)
                    # print('标题:', title, '  教师', 'teacher:', teacher)
    return kc_class
all_content=''
now_time_day=str(datetime.datetime.now())[11:-10]
# print(now_time_day)
while  True:
    try:
        zy = yxy(ocid, headers, now_time)
        qd = yxy_class(ocid, headers, now_time)
        # print(len(zy),len(qd))
        if len(zy) > 0 and now_time_day == '00:00':
            data = "您最近有以下作业未完成:\n" + ''.join(zy)
            print(data)
            send_email(data)
        kt = ''
        zyqk = ''
        if len(qd) > 0:
            for i in qd:
                kt += str(i) + '\n'
            for i in zy:
                zyqk += str(i) + '\n'
            data = "你的课堂出现以下情况" + '\n' + kt + '你目前的作业还剩\n' + zyqk
            # data="你的课堂出现以下状况:\n"+''.join(qd)+"你目前的作业还剩\n"+''.join(zy)
            print(data)
            send_email(data)
        time.sleep(60)
        if len(qd)==0 and now_time_day != '00:00':
            print("暂无消息")
    except TypeError:
        data="请重新配置优学院cooike数据"
        send_email(data)
        break
