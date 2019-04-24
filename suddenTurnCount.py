import pandas as pd
import datetime
import math
def scorePerTurn(radius):
	#由速度计算转弯角度的上限值，超过此角度为急转弯
	if radius<5:
		return 0
	elif radius>=5 and radius<=30:
		score=round((4*(radius-5)**2)/25,2)
		return score
	else:
		return 100

def suddenTurn(df):
	#统计单条道路急转弯次数
	score=0
	rows=df.shape[0]
	for i in range(1,rows):
		item=df.iloc[i]
		lastItem=df.iloc[i-1]
		lastSpeed=lastItem['gps_speed']
		speed=item['gps_speed']

		if lastSpeed>0 and speed>0:
			#只有两个车辆的速度都大于20时才进行急转弯判断
			lastTime=datetime.datetime.strptime(lastItem['location_time'],'%Y-%m-%d %H:%M:%S')
			currentTime=datetime.datetime.strptime(item['location_time'],'%Y-%m-%d %H:%M:%S')
			timeInterval=(currentTime-lastTime).total_seconds()

			turnAngle=abs(item['direction_angle']-lastItem['direction_angle'])
			#转弯角度不超过180
			if turnAngle>180:
				turnAngle=360-turnAngle
			avgSpeed=(lastSpeed+speed)/7.2	#取平均值并转换单位为米每秒
			angular_velocity=(turnAngle*math.pi/180)/timeInterval	#角速度
			if angular_velocity!=0:
				#转弯角度不为零才计算转弯半径
				radius=round((avgSpeed/angular_velocity),2)
				# print(radius)
				score+=scorePerTurn(radius)
	score=round(score/(rows-1))
	print(score)
	return score



if __name__ == '__main__':
	for i in range(1,23):
		# file='C:/Users/ASUS/Downloads/泰迪杯/Roads/AA00004/AA00004/Road'+str(i)+'.csv'
		file='./Data/AA00002/Road'+str(i)+'.csv'
		df=pd.read_csv(file)
		suddenTurn(df)
