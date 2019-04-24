import pandas as pd
import datetime

#统计单次运行线路汽车的怠速预热累计时长和次数
def idle_preheatint(df):
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
	return [count,timeSum]
if __name__ == '__main__':
	for j in range(1,17):
		file='C:/Users/ASUS/Downloads/泰迪杯/Roads/AA00004/AA00004/Road'+str(j)+'.csv'
		df=pd.read_csv(file)
		idle_preheatint(df)
	# file='C:/Users/ASUS/Downloads/泰迪杯/Roads/AA00004/AA00004/Road1.csv'
	# df=pd.read_csv(file)
	# idle_preheatint(df)
