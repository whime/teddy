#-*- coding:utf-8 -*-
import  pandas as pd
'''
提取天气情况的所有类别
'''
def splitWeatherTag(df):
	rows=df.shape[0]
	result=[]
	for i in range(0,rows):
		item=df.iloc[i]
		conditions=item[7]
		if '转' in conditions:
			# print(conditions.strip().split('转'))
			tmpTag=conditions.strip().split('转')
			# result.extend(conditions.strip().split('转'))
			for tag in tmpTag:
				if '夹' in tag:
					result.extend(tag.strip().split('夹'))
					continue
				if '-' in tag:
					result.extend(tag.strip().split('-'))
					continue
				result.append(tag)
			continue
		if '夹' in conditions:
			# print(conditions.strip().split('夹'))
			tmpTag=conditions.strip().split('夹')
			# result.extend(conditions.strip().split('夹'))
			for tag in tmpTag:
				if '转' in tag:
					result.extend(tag.strip().split('转'))
					continue
				if '-' in tag:
					result.extend(tag.strip().split('-'))
					continue
				result.append(tag)	#使用extend会将一个词语拆成单个汉字再加入列表
			continue
		if '-' in conditions:
			# print(conditions.strip().split('转'))
			tmpTag=conditions.strip().split('-')
			for tag in tmpTag:
				if '转' in tag:
					result.extend(tag.strip().split('转'))
					continue
				if '夹' in tag:
					result.extend(tag.strip().split('夹'))
					continue
				result.append(tag)
			continue
		# print(conditions)
		result.append(conditions)
	result=set(result)
	print(result)


if __name__ == '__main__':
	file='C:/Users/ASUS/Downloads/泰迪杯/13000123sgik/第七届泰迪杯赛题C题-全部数据/附件2-气象数据.csv'
	df=pd.read_csv(file,encoding='gbk',low_memory=False)
	splitWeatherTag(df)
