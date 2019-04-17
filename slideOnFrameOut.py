import pandas
import datetime

#计算单次路程的熄火滑行次数和时长
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
if __name__ == '__main__':
	for i in range(1,17):
		file="C:/Users/ASUS/Downloads/Roads/AA00004/AA00004/Road"+str(i)+".csv"
		df=pandas.read_csv(file)
		SlideOnFrameOut(df)
