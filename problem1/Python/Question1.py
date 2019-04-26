#from slideOnFrameOut import *
#from rapidAccelarate_Decelerate import *
import numpy as np
import pandas as pd
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import datetime
import os
np.seterr(divide='ignore', invalid='ignore')
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

def avg_speed(df):
    sum=0
    count=0
    for i in df.index:
        if df.loc[i]['gps_speed']>0:
            sum+=df.loc[i]['gps_speed']
            count+=1
    if count==0:
        avg_spd=0
    else:
        avg_spd=sum/count
    return avg_spd

data_route=os.getcwd()+"/Data/Q1"
print("当前目录：",data_route)
carID_list=[name for name in os.listdir(data_route)]
print(carID_list)

for i in range(10):
	carID=carID_list[i]
	DIR=data_route+'/'+carID
	roadNum=len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]) #该车辆的路段数
	print("当前carID：",carID)
	print("路段数：",roadNum)




	if __name__ == '__main__':
		#carID = 'AF00131'
		#roadNum = 30
		for i in range(1,roadNum+1):
			save_route = data_route+"/"+carID+"/Road"+str(i)+".png"  # 图片输出目录
			f=open(data_route+"/"+carID+"/Road"+str(i)+".csv")
			df=pd.read_csv(f)      #读取文件
			acc_dec=acce_decelerate(df)  #急加速急减速输出列表
			rapid_acc_numbers=acc_dec[0] #急加速次数
			rapid_acc_duration=int(acc_dec[1]) #急加速时长
			rapid_dec_numbers=acc_dec[2] #急减速次数
			rapid_dec_duration=int(acc_dec[3]) #急减速时长
			slide_frameOut=SlideOnFrameOut(df)  #熄火滑行输出列表
			mileage=df.loc[df.__len__()-1]['mileage']-df.loc[0]['mileage']  #行车里程
			if mileage==0: mileage="<1" #若行车里程为0，则最后在图上输出“<1km”
			avg_spd=avg_speed(df)  #平均速度
			avg_spd=round(avg_spd,2)

			#画坐标系图：
			plt.figure(figsize=(15, 7))  # 设置整个图片的比例
			gs = gridspec.GridSpec(1, 4)  # 设置1*5的网格
			ax = plt.subplot(gs[:, 0:3])
			ax.plot(df['lng'], df['lat'])
			font2 = {'family': 'SimHei',
					 'weight': 'normal',
					 'color': 'black',
					 'size': 22
					 }
			font3 = {'family': 'serif',
					 'style': 'italic',
					 'weight': 'normal',
					 'color': 'black',
					 'size': 15
					 }
			plt.title(carID+' Route'+str(i),fontdict=font2)
			plt.xlabel('Longitude',fontdict=font3)
			plt.ylabel('Latitude',fontdict=font3)
			ax = plt.subplot(gs[:, 3])
			ax.plot()
			plt.axis('off')
			ax.set_xticks([1, 2, 3, 4, 5])
			ax.set_yticks([1, 2, 3, 4, 5])
			font = {'family': 'serif',
					'style': 'italic',
					'weight': 'normal',
					'color': 'purple',
					'size': 13
					}
			plt.text(0, 4,'Mileage : ' + str(mileage) + 'km',fontdict=font)
			plt.text(0.1, 3.5,'Average Speed : '+str(avg_spd)+'km/s',fontdict=font)
			plt.text(0.1, 3, 'Number of Rapid Acceleration : '+str(rapid_acc_numbers)+' times',fontdict=font)
			plt.text(0.1, 2.5, 'Total duration of Rapid Acceleration : ' + str(rapid_acc_duration)+'s',fontdict=font)
			plt.text(0.1, 2, 'Number of Rapid Deceleration : ' + str(rapid_dec_numbers)+' times',fontdict=font)
			plt.text(0.1, 1.5, 'Total duration of Rapid Deceleration : ' + str(rapid_dec_duration)+'s',fontdict=font)
			#plt.show()
			plt.savefig(save_route)



