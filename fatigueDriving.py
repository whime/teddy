import pandas as pd
import datetime

#计算一个司机多天内疲劳驾驶的总时长和次数

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
if __name__ == '__main__':
	file='C:/Users/ASUS/Downloads/泰迪杯/Combine/Road3'+'.csv'
	df=pd.read_csv(file)
	fatigueDriving(df)
