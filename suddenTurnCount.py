import math
from getWeatherConditions import *

"""
根据道路当时的天气情况确定道路的最大静摩擦力的mju系数，计算速度的上限值，将每两条相邻的定位数据
的转弯角速度和速度进行计算，确定是否超过阈值，角速度按照每秒30度为上限。
"""


def suddenTurn(df, weatherDict):
	# 统计单条道路急转弯次数
	count = 0
	rows = df.shape[0]
	condition = getWeatherConditionByCoordinateAndDate(df, weatherDict)
	# print(condition)
	# 确定静摩擦系数
	mju = 0
	for weaTag in condition:
		if weaTag == '大暴雨' or weaTag == '暴雨' or weaTag == '大雨' or weaTag == "雨夹雪":
			mju = 0.3
			break
		elif '雨' in weaTag or '雪' in weaTag:
			mju = 0.7
			continue
		else:
			# 没有雨雪的情况
			if mju == 0:
				mju = 1
	# print(mju)

	# 根据可见度确定转弯角速度阈值
	angular_threhold = math.pi / 4
	if '大暴雨' in condition or '暴雨' in condition or '大雨' in condition or '雷雨' in condition:
		angular_threhold = math.pi / 6
	elif '小雨' in condition or '小到中雨' in condition or '中雨' in condition or '小雪' in condition or '阵雨' in condition or '雷阵雨' in condition or '雨夹雪' in condition or '零散雷雨' in condition:
		angular_threhold = (35 * math.pi / 180)
	elif '阴' in condition or '多云' in condition:
		angular_threhold = (40 * math.pi / 180)
	elif '雾' in condition or '扬沙' in condition or '浮尘' in condition:
		angular_threhold = (25 * math.pi / 180)

	for i in range(1, rows):
		item = df.iloc[i]
		lastItem = df.iloc[i - 1]
		lastSpeed = lastItem['gps_speed']
		speed = item['gps_speed']

		if lastSpeed > 0 and speed > 0:
			# 只有两个车辆的速度都大于0时才进行急转弯判断
			lastTime = datetime.datetime.strptime(lastItem['location_time'], '%Y-%m-%d %H:%M:%S')
			currentTime = datetime.datetime.strptime(item['location_time'], '%Y-%m-%d %H:%M:%S')
			timeInterval = (currentTime - lastTime).total_seconds()
			if timeInterval == 0:
				continue

			turnAngle = abs(item['direction_angle'] - lastItem['direction_angle'])
			# 转弯角度不超过180
			if turnAngle > 180:
				turnAngle = 360 - turnAngle
			avgSpeed = (lastSpeed + speed) / 7.2  # 取平均值并转换单位为米每秒
			angular_velocity = (turnAngle * math.pi / 180) / timeInterval  # 角速度
			# print(avgSpeed)
			# print(angular_velocity)
			# print("\n")
			if angular_velocity > 0:
				# 转弯角度不为零才计算转弯半径
				radius = round((avgSpeed / angular_velocity), 2)
				# print(radius)
				# print("\n")
				# 根据静摩擦力提供向心力计算速度阈值，大于此速度为可能打滑
				speedThreshold = math.sqrt(mju * 9.8 * radius)
				# print(speedThreshold)
				# print(avgSpeed)

				if avgSpeed > speedThreshold:
					count += 1
					continue
				else:
					if angular_velocity > angular_threhold:
						# 转弯角速度过大
						count += 1
	print(count)
	return count


if __name__ == '__main__':
	WD = genLocation_Date_Weather_Dict()
	for i in range(1, 2):
		# file='C:/Users/ASUS/Downloads/泰迪杯/Roads/AA00004/AA00004/Road'+str(i)+'.csv'
		file = './Data/AD00158/Road' + str(i) + '.csv'
		df = pd.read_csv(file)
		suddenTurn(df, WD)
