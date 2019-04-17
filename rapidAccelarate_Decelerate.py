#-*- coding:utf-8 -*-
import pandas as pd
import datetime

'''
求出一段路的急加速急减速次数和对应的时间
'''
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
        # print(currentTime)
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


if __name__=='__main__':
    file="C:/Users/ASUS/Downloads/泰迪杯/Roads/AA00004/AA00004/Road"+"1.csv"
    df=pd.read_csv(file)
    acce_decelerate(df)

