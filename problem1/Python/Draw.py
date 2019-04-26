import folium
import pandas as pd
def draw(n):
    for i in range(1,n+1,1):
        #route为路径文件
        route="E:/teddy/venv/Answer/Q1/AF00373/Road"+str(i)+".csv"
        #save_route为html文件保存路径
        save_route='E:/teddy/venv/Answer/Q1/AF00373/Road'+str(i)+'.html'
        f = open(route)
        AA00001 = pd.read_csv(f)
        m1 = folium.Map(location=[AA00001['lat'].mean(), AA00001['lng'].mean()], zoom_start=11)
        mydata1 = AA00001.loc[:, ["lat", "lng"]].values.tolist()
        mydata1 = AA00001.loc[:, ["lat", "lng"]].values.tolist()
        folium.PolyLine(mydata1, color='red').add_to(m1)
        m1.save(save_route)

#参数为路径数
draw(49)