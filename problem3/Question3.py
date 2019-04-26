import pandas as pd
import numpy as np
import datetime
import os
import json
import urllib.request
import sys
import copy
import math
np.seterr(divide='ignore', invalid='ignore')


data_route=os.getcwd()+"/Data"
if not (os.path.exists(data_route + "/SCORE")):
    os.mkdir(data_route + "/SCORE")#创建用来存放得分文件的文件夹
print("当前目录：",data_route)

#原始判断矩阵加上bias:
def add_bias(mtx,bias_mtx):
    for i in range(mtx.shape[0]):
        for j in range(mtx.shape[0]):
            if i<j:  #对于矩阵的右上三角
                v=mtx[i,j]
                B=bias_mtx[i,j]
                if v>=1:
                    if v+B>=1:
                        v2=v+B
                    elif v+B<1:
                        v2=1/(2-(v+B))
                elif v<1:
                    if (1/v)-B>=1:
                        v2=1/((1/v)-B)
                    elif (1/v)-B<1:
                        v2=2+B-(1/v)
                mtx[i,j]=v2
            elif i>j:  #对于矩阵的左下三角
                mtx[i,j]=1/mtx[j,i]
    return mtx

mtx_EC=np.matrix([1,1/2,1/3,1/2,1/2,1/3,
               2,1,1/2,1,1,1/2,
               3,2,1,2,2,1,
               2,1,1/2,1,1,1/2,
               2,1,1/2,1,1,1/2,
               3,2,1,2,2,1,]).reshape(6,6)     #节能（Energy Conservation）判断矩阵
mtx=np.matrix([1,4,2,3,3,1,3,
               1/4,1,1/2,1/2,1/2,1/3,2,
               1/2,2,1,2,2,1/2,2,
               1/2,2,1/2,1,1,1/2,2,
               1/3,2,1/2,1,1,1/2,1/2,
               1,3,2,2,2,1,3,
               1/3,1/2,1/2,1/2,2,1/3,1]).reshape(7,7)   #安全判断矩阵
mtx_backup = copy.deepcopy(mtx)   #备份一下原始矩阵，以便原始矩阵被修改时可以恢复
mtx_EC_backup = copy.deepcopy((mtx_EC))
bias_light_rian=np.matrix(
              [0,0,0,1,1,0,0,
               0,0,0,1,1,0,0,
               0,0,0,1,1,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_moderate_rian=np.matrix(
              [0,0,0,1.5,1.5,0,0,
               0,0,0,1.5,1.5,0,0,
               0,0,0,1.5,1.5,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_heavy_rian=np.matrix(
              [0,0,0,2,2,0,0,
               0,0,0,2,2,0,0,
               0,0,0,2,2,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_rainstorm=np.matrix(
              [0,0,0,2.5,2.5,0,0,
               0,0,0,2.5,2.5,0,0,
               0,0,0,2.5,2.5,0,0,
               0,0,0,0,1,0,0,
               0,0,0,0,0,-1,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_light_snow=np.matrix(
              [0,0,0,1.5,1.5,0,0,
               0,0,0,1.5,1.5,0,0,
               0,0,0,1.5,1.5,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_sunny=np.matrix(
              [0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_overcast=np.matrix(
              [0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_clody=np.matrix(
              [0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_shower=np.matrix(
              [0,0,0,0.5,0.5,0,0,
               0,0,0,0.5,0.5,0,0,
               0,0,0,0.5,0.5,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_thunder_shower=np.matrix(
              [0,0,0,1,1,0,0,
               0,0,0,1,1,0,0,
               0,0,0,1,1,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_fog=np.matrix(
              [0,1,1,1,1,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_sleet=np.matrix(
              [0,0,0,1.5,1.5,0,0,
               0,0,0,1.5,1.5,0,0,
               0,0,0,1.5,1.5,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_floating_dust=np.matrix(
              [0,1,1,1,1,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_blowing_sand=np.matrix(
              [0,1,1,1,1,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,]).reshape(7,7)
bias_EC_light_rain=np.matrix(
              [0,1,1,1,1,0,
               0,0,0,0,0,-1,
               0,0,0,0,0,-1,
               0,0,0,0,0,-1,
               0,0,0,0,0,-1,
               0,0,0,0,0,0,]).reshape(6,6)
bias_EC_heavy_rain=np.matrix(
              [0,2,2,2,2,0,
               0,0,0,0,0,-2,
               0,0,0,0,0,-2,
               0,0,0,0,0,-2,
               0,0,0,0,0,-2,
               0,0,0,0,0,0,]).reshape(6,6)
bias_EC_sunny=np.matrix(
              [0,0,0,0,0,0,
               0,0,0,0,0,0,
               0,0,0,0,0,0,
               0,0,0,0,0,0,
               0,0,0,0,0,0,
               0,0,0,0,0,0,]).reshape(6,6)



#根据天气情况确定bias矩阵，输入天气列表（包含1~3个str元素），返回bias和bias_EC矩阵：
def bias_determine(weather):
    if len(weather)>=1:
        if weather[0] in ['小雨','小到中雨']:
            bias1=bias_light_rian
            bias1_EC=bias_EC_light_rain
        if weather[0]=='中雨':
            bias1 = bias_moderate_rian
            bias1_EC = bias_EC_light_rain
        if weather[0]=='大雨':
            bias1 = bias_heavy_rian
            bias1_EC = bias_EC_heavy_rain
        if weather[0] in ['暴雨','大暴雨','雷雨']:
            bias1 = bias_rainstorm
            bias1_EC = bias_EC_heavy_rain
        if weather[0]=='小雪':
            bias1 = bias_light_snow
            bias1_EC = bias_EC_light_rain
        if weather[0] in ['晴','未知']:
            bias1 = bias_sunny
            bias1_EC = bias_EC_sunny
        if weather[0]=='阴':
            bias1 = bias_overcast
            bias1_EC = bias_EC_sunny
        if weather[0]=='多云':
            bias1 = bias_clody
            bias1_EC = bias_EC_sunny
        if weather[0]=='阵雨':
            bias1 = bias_shower
            bias1_EC = bias_EC_light_rain
        if weather[0] in ['雷阵雨','零散雷雨']:
            bias1 = bias_thunder_shower
            bias1_EC = bias_EC_light_rain
        if weather[0]=='雾':
            bias1 = bias_fog
            bias1_EC = bias_EC_sunny
        if weather[0]=='雨夹雪':
            bias1 = bias_sleet
            bias1_EC = bias_EC_light_rain
        if weather[0]=='浮尘':
            bias1 = bias_floating_dust
            bias1_EC = bias_EC_sunny
        if weather[0]=='扬沙':
            bias1 = bias_blowing_sand
            bias1_EC = bias_EC_sunny
        if len(weather)>=2:
            if weather[1] in ['小雨','小到中雨']:
                bias2 = bias_light_rian
                bias2_EC = bias_EC_light_rain
            if weather[1] == '中雨':
                bias2 = bias_moderate_rian
                bias2_EC = bias_EC_light_rain
            if weather[1] == '大雨':
                bias2 = bias_heavy_rian
                bias2_EC = bias_EC_heavy_rain
            if weather[1] in ['暴雨','大暴雨','雷雨']:
                bias2 = bias_rainstorm
                bias2_EC = bias_EC_heavy_rain
            if weather[1] == '小雪':
                bias2 = bias_light_snow
                bias2_EC = bias_EC_light_rain
            if weather[1] == '晴':
                bias2 = bias_sunny
                bias2_EC = bias_EC_sunny
            if weather[1] == '阴':
                bias2 = bias_overcast
                bias2_EC = bias_EC_sunny
            if weather[1] == '多云':
                bias2 = bias_clody
                bias2_EC = bias_EC_sunny
            if weather[1] == '阵雨':
                bias2 = bias_shower
                bias2_EC = bias_EC_light_rain
            if weather[1] in ['雷阵雨','零散雷雨']:
                bias2 = bias_thunder_shower
                bias2_EC = bias_EC_light_rain
            if weather[1] == '雾':
                bias2 = bias_fog
                bias2_EC = bias_EC_sunny
            if weather[1] == '雨夹雪':
                bias2 = bias_sleet
                bias2_EC = bias_EC_light_rain
            if weather[1] == '浮尘':
                bias2 = bias_floating_dust
                bias2_EC = bias_EC_sunny
            if weather[1] == '扬沙':
                bias2 = bias_blowing_sand
                bias2_EC = bias_EC_sunny
            if len(weather)==3:
                if weather[2] in ['小雨','小到中雨']:
                    bias3 = bias_light_rian
                    bias3_EC = bias_EC_light_rain
                if weather[2] == '中雨':
                    bias3 = bias_moderate_rian
                    bias3_EC = bias_EC_light_rain
                if weather[2] == '大雨':
                    bias3 = bias_heavy_rian
                    bias3_EC = bias_EC_heavy_rain
                if weather[2] in ['暴雨','大暴雨','雷雨']:
                    bias3 = bias_rainstorm
                    bias3_EC = bias_EC_heavy_rain
                if weather[2] == '小雪':
                    bias3 = bias_light_snow
                    bias3_EC = bias_EC_light_rain
                if weather[2] == '晴':
                    bias3 = bias_sunny
                    bias3_EC = bias_EC_sunny
                if weather[2] == '阴':
                    bias3 = bias_overcast
                    bias3_EC = bias_EC_sunny
                if weather[2] == '多云':
                    bias3 = bias_clody
                    bias3_EC = bias_EC_sunny
                if weather[2] == '阵雨':
                    bias3 = bias_shower
                    bias3_EC = bias_EC_light_rain
                if weather[2] in ['雷阵雨','零散雷雨']:
                    bias3 = bias_thunder_shower
                    bias3_EC = bias_EC_light_rain
                if weather[2] == '雾':
                    bias3 = bias_fog
                    bias3_EC = bias_EC_sunny
                if weather[2] == '雨夹雪':
                    bias3 = bias_sleet
                    bias3_EC = bias_EC_light_rain
                if weather[2] == '浮尘':
                    bias3 = bias_floating_dust
                    bias3_EC = bias_EC_sunny
                if weather[2] == '扬沙':
                    bias3 = bias_blowing_sand
                    bias3_EC = bias_EC_sunny
    if len(weather)==1:
        bias=bias1
        bias_EC=bias1_EC
    if len(weather)==2:
        bias=(bias1+bias2)/2
        bias_EC = (bias1_EC + bias2_EC) / 2
    if len(weather)==3:
        bias=(bias1+bias2+bias3)/3
        bias_EC = (bias1_EC + bias2_EC + bias3_EC) / 3
    return [bias,bias_EC]



#一致性检验,输入判断矩阵，输出CR值：
def Consistency_test(mtx):
    n=mtx.shape[0]
    a,b=np.linalg.eig(mtx)
    max_chrct_value=max(a)#求判断矩阵的最大特征值
    max_chrct_value=max_chrct_value.real
    CI=(max_chrct_value-n)/(n-1)
    RI=np.array([0,0,0,0.52,0.89,1.12,1.24,1.36,1.41,1.46,1.49,1.52,1.54,1.56,1.58])
    CR=CI/RI[n]
    return round(CR,3)



#列向量归一化：
def normalization(mtx):   #比例归一化
    for i in range(mtx.shape[1]):  #对矩阵的每一列进行循环
        sum = mtx[:, i].sum()  # 当前列的和
        for j in range(mtx.shape[0]):  #对每一列的每个元素进行循环
            mtx[j,i]=mtx[j,i]/sum
    return mtx

'''
#行向量求平均得出weight向量：
weight=np.array([float(0) for i in range(mtx.shape[1])])  #创建weight向量
for i in range(mtx.shape[1]):
    weight[i]=mtx[i,:].mean()
print("权重列表：\n",weight)
print("(超速，急加速，急减速，车速稳定性，熄火滑行，疲劳驾驶,急转弯)")
'''


#车速稳定性判断，返回车速标准差：
def Speed_Stability(df):
    return np.std(df['gps_speed'],ddof=1)
#急加速急减速判断，返回列表[急加速次数,急加速时长，急减速次数，急减速时长]
def acce_decelerate(df):

    rows=df.shape[0]
    # print(rows)
    acc_count=dec_count=0
    acc_time=list()
    dec_time=list()
    currentState=False  #false表示当前时间正在减速
    isAccelerate=[0]    #记录每个时间点是不是加速或减速
    isDecelerate=[0]    #第一个时刻不算加减速

    sumTime=0   #保存一段加速/减速的累计时间
    for i in range(0,rows-1):
        lastItem=df.iloc[i]
        # print(i)
        currentItem=df.iloc[i+1]
        #取出前后相邻的时间，计算差值
        lastTime=datetime.datetime.strptime(lastItem[10],'%Y-%m-%d %H:%M:%S')
        currentTime=datetime.datetime.strptime(currentItem[10],'%Y-%m-%d %H:%M:%S')
        delta=currentTime-lastTime
        #时间间隔小于等于3s，考虑加减速
        timeInterval=delta.total_seconds()
        # print(timeInterval)
        if timeInterval<=3:
            lastSpeed=lastItem[11]
            currentSpeed=currentItem[11]

            a=(currentSpeed-lastSpeed)/(3.6*timeInterval)   #计算加速度

            if a<-3 and  not currentState:#减速阶段，累加时间到sumTime
                # print(a)
                sumTime+=timeInterval
                isDecelerate.append(1)
                isAccelerate.append(0)
            elif a<-3 and currentState:#从加速进入减速
                acc_count+=1
                # print(a)
                acc_time.append(sumTime)
                sumTime=timeInterval
                isAccelerate.append(0)
                isDecelerate.append(1)
                currentState=False
            elif a>3 and currentState:  #加速阶段
                # print(a)
                sumTime+=timeInterval
                isAccelerate.append(1)
                isDecelerate.append(0)
            elif a>3 and not currentState:#从减速进入加速
                if(sumTime!=0):
                    dec_count+=1
                    dec_time.append(sumTime)
                # print(a)
                sumTime=timeInterval
                # isAccelerate.append(1)
                # isDecelerate.append(0)
                currentState=True

        else:
            #时间间隔不小于3s,不是连续的急加速急减速
            if not currentState:
                if(sumTime!=0):
                    dec_count+=1
                    dec_time.append(sumTime)
                    sumTime=0
                # isAccelerate.append(0)
                # isDecelerate.append(0)
            else:
                acc_count+=1
                acc_time.append(sumTime)
                sumTime=0
                # isAccelerate.append(0)
                # isDecelerate.append(0)
    return [acc_count,sum(acc_time),dec_count,sum(dec_time)]
#熄火滑行判断，返回列表[熄火滑行总时长，熄火滑行次数]
def SlideOnFrameOut(df):

    rows=df.shape[0]
    isSlide=False
    startTime=0
    sumTime=0
    slideCount=0
    startlng=0
    startlat=0



    for i in range(0,rows):
        item=df.iloc[i]
        acc_state=item[5]
        gps_speed=item[11]

        if acc_state==0  and gps_speed<50:
            if not isSlide:#开始熄火滑行
                isSlide=True
                startTime=datetime.datetime.strptime(item[10],'%Y-%m-%d %H:%M:%S')
                startlat=item[4]
                startlng=item[3]
            continue
        if isSlide:
            endTime=datetime.datetime.strptime(item[10],'%Y-%m-%d %H:%M:%S')
            timeInterval=(endTime-startTime).total_seconds()
            # print(timeInterval)
            endlat=item[4]
            endlng=item[3]
            isSlide=False
            #行驶里程大于0，并且经纬度有变化，时间间隔大于3s
            if timeInterval>=0 and (startlng!=endlng or startlat!=endlat) :
                sumTime+=timeInterval
                slideCount+=1
    # print(sumTime)
    # print(slideCount)
    return [sumTime,slideCount]
#超速判断，返回列表[超速时长，超速次数]
def overspeed(df,speed_max):
    Overspeed_Duration=0   #用来记录超速时长
    Overspeed_Frequency=0  #用来记录超速次数
    flag_list = [0 for i in range(df.__len__() + 3)]  # 初始化一个flag,用来标记当前记录是否已扫描
    for i in df.index:
        if df.loc[i]['gps_speed']>speed_max and flag_list[i]==0:
            t1=i #超速开始时间
            n=i+1
            while n<df.__len__() and df.loc[n]['gps_speed']>speed_max:
                flag_list[n] = 1
                n+=1
            t2=n-1  #超速结束时间
            time_len=pd.to_datetime(df.loc[t2]['location_time'])-pd.to_datetime(df.loc[t1]['location_time'])
            time_len=time_len.total_seconds()
            if time_len>=3:#为防止gps漂移，超速时长至少为3秒才会被记录
                Overspeed_Duration+=time_len
                Overspeed_Frequency+=1
    return (list([Overspeed_Duration,Overspeed_Frequency]))
#疲劳驾驶判断，返回列表[疲劳驾驶时长（单位h），疲劳驾驶次数]
def fatigueDriving(df):
    rows=df.shape[0]
    sumDriveTime=0#一辆车的总疲劳驾驶累计时长
    sumDriveCount=0#疲劳驾驶累计次数
    fatigueDriveCount=0#当天疲劳驾驶累计次数
    fatigueDriveTime=0#当天疲劳驾驶累计时长
    item=df.iloc[0]
    day=datetime.datetime.strptime(df.loc[0]['location_time'],'%Y-%m-%d %H:%M:%S').day	#当前日期

    drive=False
    setOffTime=datetime.datetime.strptime(df.loc[0]['location_time'],'%Y-%m-%d %H:%M:%S')
    startRestTime=0	#开始休息的时间
    restTime=0
    rest=False
    for i in range(1,rows):
        item=df.iloc[i]
        curTime=datetime.datetime.strptime(df.loc[i]['location_time'],'%Y-%m-%d %H:%M:%S')
        lastTime=datetime.datetime.strptime(df.loc[i-1]['location_time'],'%Y-%m-%d %H:%M:%S')
        timeInterval=(curTime-lastTime).total_seconds()
        # if curTime.day!=day:
        # 	print("new day")
        if curTime.day!=day or (timeInterval>1200 and drive) or i==(rows-1):
            #日期变化或者出现相邻两条数据之间时间间隔大于20分钟，需要结束前面的统计
            day=curTime.day

            if (lastTime-setOffTime).total_seconds()>14400:
                # print('4 hours')
                fatigueDriveCount+=1
                sumDriveTime+=(lastTime-setOffTime).total_seconds()
            if fatigueDriveCount<=1 and fatigueDriveTime>28800:
                #单次连续驾驶行为小于2并且当日驾驶时长大于8小时，则fatigueDriveCount加1
                fatigueDriveCount+=1
                # print('addition')
                if fatigueDriveCount==1:
                    #若原来的单次连续驾驶行为是0，当日驾驶时长超过8小时，则表明都是不连续的小的分散时间段，将fatigueDriveTime加入总的驾驶时长
                    sumDriveTime+=fatigueDriveTime
                    # print('8 hours')
            sumDriveCount+=fatigueDriveCount
            fatigueDriveCount=0
            fatigueDriveTime=0
            drive=False
        #开始单次连续驾驶行为
        if item[11]!=0 and not drive:
            drive=True
            setOffTime=curTime
        elif item[11]==0 and drive and not rest:
            startRestTime=curTime
            rest=True
        elif item[11]!=0 and drive and rest:
            restTime=lastTime-startRestTime
            rest=False
            if restTime.total_seconds()>=1200:#休息够20分钟，开车状态变为false,重新记录单次连续驾驶行为
                delta=startRestTime-setOffTime
                #结束当次连续驾驶
                drive=False
                if delta.total_seconds()>14400:#持续驾驶超过4小时
                    fatigueDriveCount+=1
                    # print('4 hours')
                    sumDriveTime+=delta.total_seconds()
        elif item[11]!=0 and drive and not rest:
            fatigueDriveTime+=timeInterval
    sumDriveTimeInHours=round(sumDriveTime,2)#保留两位数
    # print('%.2f	%d'%(sumDriveTime,sumDriveCount))
    return [sumDriveTimeInHours,sumDriveCount]
#急转弯判断，返回急转弯次数
def upperBoundBySpeed(speed):
    #由速度计算转弯角度的上限值，超过此角度为急转弯
    if speed>0 and speed<=40:
        return (-speed+90)/4
    elif speed>40 and speed<=80:
        return (-speed+100)/5
    else:
        return (-speed+180)/25
def suddenTurn(df,weatherDict):
    #统计单条道路急转弯次数
    count=0
    rows=df.shape[0]
    condition=getWeatherConditionByCoordinateAndDate(df,weatherDict)
    # print(condition)
    #确定静摩擦系数
    mju=0
    for weaTag in condition:
        if weaTag=='大暴雨' or weaTag=='暴雨' or weaTag=='大雨' or weaTag=="雨夹雪":
            mju=0.3
            break
        elif '雨' in weaTag or '雪' in weaTag:
            mju=0.7
            continue
        else:
            #没有雨雪的情况
            if mju==0:
                mju=1
    # print(mju)
    angular_threhold=math.pi/4
    if '大暴雨' in condition or  '暴雨' in condition or '大雨' in condition or '雷雨' in condition:
        angular_threhold=math.pi/6
    elif '小雨' in condition or '小到中雨' in condition or '中雨' in condition or '小雪' in condition or '阵雨' in condition or '雷阵雨' in condition or '雨夹雪' in condition or '零散雷雨' in condition:
        angular_threhold=(35*math.pi/180)
    elif '阴' in condition or '多云' in condition:
        angular_threhold = (40 * math.pi / 180)
    elif '雾' in condition or '扬沙' in condition or '浮尘' in condition:
        angular_threhold = (25 * math.pi / 180)

    for i in range(1,rows):
        item=df.iloc[i]
        lastItem=df.iloc[i-1]
        lastSpeed=lastItem['gps_speed']
        speed=item['gps_speed']


        if lastSpeed>0 and speed>0:
            #只有两个车辆的速度都大于0时才进行急转弯判断
            lastTime=datetime.datetime.strptime(lastItem['location_time'],'%Y-%m-%d %H:%M:%S')
            currentTime=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S')
            timeInterval=(currentTime-lastTime).total_seconds()
            if timeInterval==0:
                continue

            turnAngle=abs(item['direction_angle']-lastItem['direction_angle'])
            #转弯角度不超过180
            if turnAngle>180:
                turnAngle=360-turnAngle
            avgSpeed=(lastSpeed+speed)/7.2	#取平均值并转换单位为米每秒
            angular_velocity=(turnAngle*math.pi/180)/timeInterval	#角速度
            # print(avgSpeed)
            # print(angular_velocity)
            # print("\n")
            if angular_velocity>0:
                #转弯角度不为零才计算转弯半径
                radius=round((avgSpeed/angular_velocity),2)
                # print(radius)
                # print("\n")
                #根据静摩擦力提供向心力计算速度阈值，大于此速度为可能打滑
                speedThreshold=math.sqrt(mju*9.8*radius)
                # print(speedThreshold)
                # print(avgSpeed)

                if avgSpeed>speedThreshold:
                    count+=1
                    continue
                else:
                    if angular_velocity>angular_threhold:
                        #转弯角速度过大
                        count+=1
    # print(count)
    return count

#怠速预热判断，返回[怠速预热次数,怠速预热mins]
def idle_preheating(df):
    rows=df.shape[0]
    CurDayFirstFrame=True	#当日首次点火
    day=datetime.datetime.now().day
    startIdlePreheatTime=0
    timeSum=0
    count=0
    isIdle=False
    for i in range(0,rows):
        item=df.iloc[i]
        #新的一天
        if day!=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S').day:
            CurDayFirstFrame=True
            day=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S').day
        if item['acc_state']==1 and item['gps_speed']==0:
            #发生车辆怠速行为
            if CurDayFirstFrame or df.iloc[i-1]['acc_state']==0 or not isIdle:
                startIdlePreheatTime=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S')
                CurDayFirstFrame=False
                isIdle=True
            if i==rows-1:
                endIdlePreheatTime=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S')
                timeInterval=(endIdlePreheatTime-startIdlePreheatTime).total_seconds()
                if timeInterval>60:
                    # print("end")
                    # print(startIdlePreheatTime)
                    # print(endIdlePreheatTime)
                    # print(timeInterval)
                    timeSum+=timeInterval
                    count+=1

        else:
            if isIdle:
                endIdlePreheatTime=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S')
                timeInterval=(endIdlePreheatTime-startIdlePreheatTime).total_seconds()
                if timeInterval>60:
                    timeSum+=timeInterval
                    count+=1
                    # print(startIdlePreheatTime)
                    # print(endIdlePreheatTime)
                    # print(timeInterval)
                isIdle=False
    timeSum/=60
    timeSum=round(timeSum,2)
    return [count,timeSum]#怠速预热判断，返回[怠速预热次数,怠速预热mins]
#超长怠速判断，返回[超长怠速次数,超长怠速mins]
def overlong_idle(df):
    rows=df.shape[0]
    timeSum=0
    idlingCount=0
    startIdlingTime=df.iloc[0]['location_time']

    isIdling=False
    for i in range(0,rows):
        item=df.iloc[i]
        acc=item['acc_state']
        speed=item['gps_speed']
        if acc==1 and speed==0:
            if isIdling:
                if i==rows-1:
                    #到达最后一行
                    endIdligTime=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S')
                    timeInterval=(endIdligTime-startIdlingTime).total_seconds()
                    if timeInterval>=60:
                        #持续怠速超过60s，计数并累计时长
                        timeSum+=timeInterval
                        idlingCount+=1
                    isIdling=False

            else:
                #重新开始新的判断
                startIdlingTime=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S')
                isIdling=True
                continue
        else:
            #怠速行为结束
            if isIdling:
                endIdligTime=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S')
                timeInterval=(endIdligTime-startIdlingTime).total_seconds()
                if timeInterval>=60:
                    #持续怠速超过60s，计数并累计时长
                    timeSum+=timeInterval
                    idlingCount+=1
                isIdling=False

    #print(timeSum,idlingCount)
    return [idlingCount,timeSum]
#将天气情况的描述拆分出来,返回一个集合
def splitWeatherTag(conditions):
    result=[]
    if '转' in conditions:
        tmpTag=conditions.strip().split('转')
        for tag in tmpTag:
            if '-' in tag:
                result.extend(tag.strip().split('-'))
                continue
            result.append(tag)

    elif '-' in conditions:

        tmpTag=conditions.strip().split('-')
        for tag in tmpTag:
            if '转' in tag:
                result.extend(tag.strip().split('转'))
                continue
            result.append(tag)
    else:
        result.append(conditions)
    result=set(result)
    #print(result)
    return result
#根据气象数据返回字典，key为省市区，日期组成的列表，value为conditions属性
def genLocation_Date_Weather_Dict():
    weatherFile=os.getcwd()+"/Data/附件2-气象数据.csv"

    #有中文的文件一定要设置编码
    df=pd.read_csv(weatherFile,encoding='gbk',low_memory=False)
    rows=df.shape[0]
    resultDict={}
    for i in range(0,rows):
        item=df.iloc[i]
        tmpProvince=item['province']
        tmpCity=item['prefecture_city']
        tmpCounty=item['county']
        condition=item['conditions']
        tmpDate=datetime.datetime.strptime(item['record_date'],'%d/%m/%Y').date()
        resultKey=(tmpProvince,tmpCity,tmpCounty,tmpDate)
        resultDict[resultKey]=condition

    return resultDict
#基于百度地图API下的经纬度信息来解析地理位置信息,并获取对应时间地点的天气情况
#curDate必须为%d/%m/%Y 形式
def getWeatherConditionByCoordinateAndDate(df,weatherDict):

    item=df.iloc[0]
    lng=item['lng']
    lat=item['lat']
    DateandTime=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S')
    curDate=DateandTime.date()	#提取日期

    #转换坐标api,将WGS84坐标转换为BD09II
    transUrl='http://api.map.baidu.com/geoconv/v1/?coords='+str(lng)+','+str(lat)+'&from=1&to=5&ak=omccBE0lR4imoVYekaRdNsSW9NiiMief'
    tranReq=urllib.request.urlopen(transUrl)
    tranResult=tranReq.read().decode('utf-8')
    #返回的是str类型，使用json读取
    tranResult=json.loads(tranResult)
    tranStatus=tranResult.get('status')
    if tranStatus!=0:
        #转换失败
        print("coodinate transform error!")
        sys.exit(1)
    coodinate=tranResult.get('result')[0]	#返回的是列表，使用[0]提取，为字典类型
    lng=coodinate['x']
    lat=coodinate['y']
    # print("经度",lng)
    # print("纬度",lat)
    #使用转换后的经纬度查询省市区
    url = 'http://api.map.baidu.com/geocoder/v2/?location='+str(lat)+','+str(lng)+ '&output=json&pois=1&ak=omccBE0lR4imoVYekaRdNsSW9NiiMief'
    req = urllib.request.urlopen(url)  # json格式的返回数据
    res = req.read().decode("utf-8")  # 将其他编码的字符串解码成unicode
    resultJson=json.loads(res).get('result')
    address=resultJson.get('addressComponent')
    #获取坐标对应的省市区


    province=address.get('province').strip('省')
    city=address.get('city').strip('市')
    district=address.get('district')[:-1]
    # print(province)
    # print(city)
    # print(district)

    tmpKey=(province,city,district,curDate)
    if tmpKey in weatherDict:
        return splitWeatherTag(weatherDict[tmpKey])
    #找不到对应地点的天气情况，返回字符串集合'未知'
    # print("未知")
    return ['未知']


##主函数：
carID_list=[name for name in os.listdir(data_route) if name.__len__()==7]
for k in range(len(carID_list)):
    carID=carID_list[k]
    DIR=data_route+'/'+carID
    roadNum=len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name)) and os.path.splitext(name)[1] == '.csv']) #该车辆的路段数
    #roadNum=int(roadNum/2)
    print("当前carID：",carID)
    print("路段数：",roadNum)

    score=[0 for i in range(roadNum+1)]
    score_EC=[0 for i in range(roadNum+1)]
    score_total = [0 for i in range(roadNum + 1)]
    weather_list=['' for i in range(roadNum + 1)]
    for i in range(1,roadNum+1):
        f = open(data_route+"/"+carID+"/Road"+str(i)+".csv") #WAY
        df=pd.read_csv(f)
        print("\n*******正在处理"+carID+" Road"+str(i)+"*******")

        # 对判断矩阵进行调整：
        weather_dict=genLocation_Date_Weather_Dict()
        weather=list(getWeatherConditionByCoordinateAndDate(df, weather_dict))
        weather_list[i-1]=weather
        print("当前路段天气：",weather)
        bias = bias_determine(weather)

        mtx_adjust = add_bias(mtx, bias[0])
        mtx_EC_adjust=add_bias(mtx_EC,bias[1])

        #用调整后的安全判断矩阵计算权重：
        CR = Consistency_test(mtx_adjust)  # 一致性检验
        print("调整后的安全模型判断矩阵一致性检验：CR=",CR)
        mtx_adjust = normalization(mtx_adjust)  # 列向量归一化
        weight = np.array([float(0) for i in range(mtx_adjust.shape[1])])  # 创建weight向量
        for j in range(mtx_adjust.shape[1]):
            weight[j] = mtx_adjust[j, :].mean()  # 得出权重列表
        print("安全指标权重列表：\n", weight)
        print("(超速，急加速，急减速，车速稳定性，熄火滑行，疲劳驾驶,急转弯)")

        #用调整后的节能判断矩阵计算节能指标权重：
        CR_EC=Consistency_test(mtx_EC_adjust)
        print("调整后的节能模型判断矩阵一致性检验：CR=", CR_EC)
        mtx_EC_adjust = normalization(mtx_EC_adjust)  # 列向量归一化
        weight_EC = np.array([float(0) for i in range(mtx_EC_adjust.shape[1])])  # 创建weight向量
        for p in range(mtx_EC_adjust.shape[1]):
            weight_EC[p] = mtx_EC_adjust[p, :].mean()  # 得出权重列表
        print("节能指标权重列表：\n", weight_EC)
        print("(怠速预热，超速，急加速，急减速，车速稳定性，超长怠速)")

        speed_std=Speed_Stability(df) #车速方差
        acc_dec=acce_decelerate(df)  #急加速急减速输出列表
        rapid_acc_numbers=acc_dec[0] #急加速次数
        rapid_acc_duration=int(acc_dec[1]) #急加速时长
        rapid_dec_numbers=acc_dec[2] #急减速次数
        rapid_dec_duration=int(acc_dec[3]) #急减速时长
        slide_frameOut_list=SlideOnFrameOut(df)  #熄火滑行输出列表
        slide_frameOut_duration=slide_frameOut_list[0] #熄火滑行时长
        slide_frameOut_numbers=slide_frameOut_list[1]  #熄火滑行次数
        overspeed_list=overspeed(df,100) #超速输出列表
        overspeed_numbers=overspeed_list[1] #超速次数
        overspeed_duration=overspeed_list[0] #超速时长
        fatigueDriving_list=fatigueDriving(df) #疲劳驾驶输出列表
        fatigueDriving_numbers=fatigueDriving_list[1] #疲劳驾驶次数
        fatigueDriving_hours=fatigueDriving_list[0] #疲劳驾驶时长
        suddenTurn_numbers=suddenTurn(df,weather_dict)#急转弯次数
        idle_preheating_list=idle_preheating(df) #怠速预热输出列表
        idle_preheating_numbers=idle_preheating_list[0] #怠速预热次数
        idle_preheating_mins=idle_preheating_list[1] #怠速预热时长
        overlong_idle_list=overlong_idle(df) #超长怠速输出列表
        overlong_idle_numbers=overlong_idle_list[0] #超长怠速次数
        overlong_idle_mins=overlong_idle_list[1] #超长怠速时长


        #计算得分：
        #车速稳定性得分score_stb：
        if speed_std<=20:
            score_stb=100
        elif 20<speed_std<=40:
            score_stb = 80
        elif speed_std>40:
            score_stb=60

        #急加速次数得分：
        score_acc_numbers=100-15*rapid_acc_numbers
        if score_acc_numbers<0:score_acc_numbers=0
        #急加速时长得分：
        score_acc_duration=100-0.8*int(rapid_acc_duration)
        if score_acc_duration < 0: score_acc_duration = 0
        #急加速总得分:
        score_acc=(score_acc_numbers/2)+(score_acc_duration/2)
        #急减速次数得分：
        score_dec_numbers=100-15*rapid_dec_numbers
        if score_dec_numbers < 0: score_dec_numbers = 0
        #急减速时长得分：
        score_dec_duration=100-0.8*int(rapid_dec_duration)
        if score_dec_duration < 0: score_dec_duration = 0
        #急减速总得分:
        score_dec=(score_dec_numbers/2)+(score_dec_duration/2)


        #超速次数得分：
        score_overspeed_numbers=100-15*overspeed_numbers
        if score_overspeed_numbers < 0: score_overspeed_numbers = 0
        #超速时长得分：
        score_overspeed_duration=100-overspeed_duration
        if score_overspeed_duration < 0: score_overspeed_duration = 0
        #超速总得分:
        score_overspeed=(score_overspeed_duration/2)+(score_overspeed_numbers/2)

        #熄火滑行次数得分：
        score_slide_numbers=100-20*slide_frameOut_numbers
        if score_slide_numbers < 0: score_slide_numbers = 0
        #熄火滑行时长得分：
        if slide_frameOut_duration<=1:
            score_slide_duration=100
        elif slide_frameOut_duration>1:
            score_slide_duration=100-10*slide_frameOut_duration
            if score_slide_duration < 0: score_slide_duration = 0
        #熄火滑行总得分：
        score_slide=(score_slide_numbers/2)+(score_slide_duration/2)

        #疲劳驾驶次数得分：
        score_fati_numbers=100-15*fatigueDriving_numbers
        if score_fati_numbers < 0: score_fati_numbers = 0
        #疲劳驾驶时长得分:
        if fatigueDriving_hours>8:
            score_fati_hours=0
        else:
            score_fati_hours = 100
        #疲劳驾驶总得分：
        score_fati=(score_fati_hours/2)+(score_fati_numbers/2)

        #急转弯得分：
        score_suddenTurn=100-10*suddenTurn_numbers
        if score_suddenTurn < 0: score_suddenTurn = 0

        #怠速预热次数得分：
        score_idlePre_numbers=100-15*idle_preheating_numbers
        if score_idlePre_numbers<0: score_idlePre_numbers=0
        #怠速预热时长得分：
        score_idlePre_mins = 100 - 2.5 * idle_preheating_mins
        if score_idlePre_mins < 0: score_idlePre_mins = 0
        #怠速预热总得分：
        score_idlePre=(score_idlePre_numbers/2)+(score_idlePre_mins/2)

        # 超长怠速次数得分：
        score_overIdle_numbers = 100 - 10 * overlong_idle_numbers
        if score_overIdle_numbers < 0: score_overIdle_numbers = 0
        # 超长怠速时长得分：
        score_overIdle_mins = 100 - 0.8 * overlong_idle_mins
        if score_overIdle_mins < 0: score_overIdle_mins = 0
        # 超长怠速总得分：
        score_overIdle = (score_overIdle_numbers / 2) + (score_overIdle_mins / 2)


        #计算安全模型总得分：
        score[i]=weight[0]*score_overspeed+weight[1]*score_acc+weight[2]*score_dec+weight[3]*score_stb+weight[4]*score_slide+weight[5]*score_fati+weight[6]*score_suddenTurn
        print("Road"+str(i)+"安全模型得分：",score[i])
        #计算节能模型总得分：
        score_EC[i]=weight_EC[0]*score_idlePre+weight_EC[1]*score_overspeed+weight_EC[2]*score_acc+weight_EC[3]*score_dec+weight_EC[4]*score_stb+weight_EC[5]*score_overIdle
        print("Road" + str(i) + "节能模型得分：", score_EC[i])
        #计算综合模型得分：
        score_total[i]=(score[i]/2)+(score_EC[i]/2)
        print("Road" + str(i) + "综合模型得分：", score_total[i])
        mtx = copy.deepcopy(mtx_backup)  #恢复初始判断矩阵
        mtx_EC = copy.deepcopy(mtx_EC_backup)
    print("车辆"+carID+"综合模型总得分：",sum(score_total)/roadNum)

    #将数据输出为csv文件
    col1=["Road"+str(i) for i in range(1,roadNum+1)]
    col1.append("AVG_score")
    col2 = weather_list
    col3=[round(score[i],2) for i in range(1,roadNum+1)]
    col3.append(round(sum(score)/roadNum,2))
    col4 = [round(score_EC[i], 2) for i in range(1, roadNum + 1)]
    col4.append(round(sum(score_EC) / roadNum, 2))
    col5 = [round(score_total[i], 2) for i in range(1, roadNum + 1)]
    col5.append(round(sum(score_total) / roadNum, 2))
    df=pd.DataFrame(np.matrix([col1,col2,col3,col4,col5]).T,columns=[carID,'天气状况','安全评分','节能评分','总得分'])
    df.to_csv(data_route+"/SCORE"+"/"+carID+"_score.csv",encoding='gbk',index=False)
