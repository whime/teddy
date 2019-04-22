import pandas as pd
import datetime
def upperBoundBySpeed(speed):
	#由速度计算转弯角度的上限值，超过此角度为急转弯
	if speed>0 and speed<=40:
		return (-speed+90)/4
	elif speed>40 and speed<=80:
		return (-speed+100)/5
	else:
		return (-speed+180)/25

def suddenTurn(df):
	#统计单条道路急转弯次数
	count=0
	rows=df.shape[0]
	for i in range(1,rows):
		item=df.iloc[i]
		lastItem=df.iloc[i-1]
		lastSpeed=lastItem['gps_speed']
		speed=item['gps_speed']

		if lastSpeed>20 and speed>20:
			#只有两个车辆的速度都大于20时才进行急转弯判断
			lastTime=datetime.datetime.strptime(lastItem['location_time'],'%Y-%m-%d %H:%M:%S')
			currentTime=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S')
			timeInterval=(currentTime-lastTime).total_seconds()
			turnAngle=abs(item['direction_angle']-lastItem['direction_angle'])
			#转弯角度不超过180
			if turnAngle>180:
				turnAngle=360-turnAngle
			if turnAngle>upperBoundBySpeed(speed)*timeInterval:
				count+=1
			if turnAngle>31 and speed>51:
				count+=1
	print(count)



if __name__ == '__main__':
	for i in range(1,17):
		file='C:/Users/ASUS/Downloads/泰迪杯/Roads/AA00004/AA00004/Road'+str(i)+'.csv'
		df=pd.read_csv(file)
		suddenTurn(df)
