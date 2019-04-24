import pandas as pd
import datetime
#统计单次运行线路汽车的超长怠速累计时长和次数
def idling(df):
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

	# print(timeSum,idlingCount)
	return [timeSum,idlingCount]
if __name__ == '__main__':
	file='C:/Users/ASUS/Downloads/泰迪杯/Roads/AA00004/AA00004/Road1.csv'
	df=pd.read_csv(file)
	idling(df)

