function []=DeleteData(Name,M,Delta,MAXTime,MAXDIS,MINSIZE)
%文件名称，最大速度，累计时间差，两点最大时间差，最大距离差，最小数据量
format long g;
Table=readtable(['E:\teddy\venv\RawData\',Name,'.csv']);
Load='E:\teddy\venv\Data\';
Name=[Load Name];
mkdir(Name);
E=table2cell(Table);
Org={'vehicleplatenumber'	'device_num' 'direction_angle' 'lng' 'lat' 'acc_state'  'right_turn_signals' 'left_turn_signals' 'hand_brake' 'foot_brake' 'location_time' 'gps_speed' 'mileage'};
R=Org;
index=2;
max=M;
i=2;%to init i as 2
Total_Time=0;
R_Index=1;
X=E(1,:);
GPS_Zero=0;
AX=cell2mat(E(1,[4 5]));
while(i<=size(E,1))%遍历整个记录
    Y=E(i,:);%前面有错误起始点，检测该点与起始点的距离差
    AY=cell2mat(E(i,[4 5]));
    T=etime(datevec(Y(1,11)),datevec(X(1,11)));    

      %GPS速度为0
    Temp=cell2mat(Y(1,12));
    if( Temp(1,1)==0)
        GPS_Zero=GPS_Zero+1;
    end
    
    if(AX==AY)
            Total_Time=Total_Time+T;
            if(Total_Time>=Delta)
                if(size(R,1)>MINSIZE&&GPS_Zero<size(R,1)*0.75)
                    cell2csv([Name,'/Road',num2str(R_Index),'.csv'],R);
                     R_Index=R_Index+1;
                end
                GPS_Zero=0;
                R=Org;
                index=2;
                Total_Time=0;  
            end
            R(index,:)=Y;
            index=index+1;
            X=Y;
            AX=AY; 
            i=i+1;
            continue;
    end
    
    if(T>MAXTime)
            if(size(R,1)>MINSIZE&&GPS_Zero<size(R,1)*0.75)
               cell2csv([Name,'/Road',num2str(R_Index),'.csv'],R);
                 R_Index=R_Index+1;
            end
            GPS_Zero=0;
            R=Org;
            index=2;
            Total_Time=0;  
            X=Y;
            AX=AY;
            %Not to Add the i because this one may be the new start of the
            %next journal
            i=i+1;
            continue;
    end
    
    Total_Time=0;%not equal,clear
    if(distance(AX(1,2),AX(1,1),AY(1,2),AY(1,1))/180*pi*6370>MAXDIS)
            if(size(R,1)>MINSIZE&&GPS_Zero<size(R,1)*0.75)
                 cell2csv([Name,'/Road',num2str(R_Index),'.csv'],R);
                 R_Index=R_Index+1;
            end
            GPS_Zero=0;
            R=Org;
            index=2;
            Total_Time=0;  
            X=Y;
            AX=AY;
            i=i+1;
    end

    %时间间隔为0
    if(T==0)
        i=i+1;
        continue;
    end
  
    if(distance(AX(1,2),AX(1,1),AY(1,2),AY(1,1))/180*pi*6370>T*max)
            i=i+1;         
    else
        R(index,:)=Y;
        %直接赋值
        X=Y;
        AX=AY;
        index=index+1;
        i=i+1;
    end
    
end

end




