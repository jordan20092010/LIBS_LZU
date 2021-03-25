# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 19:53:48 2020

@author: dell
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']
list=[]
list2=[] # 保存UO2大于阈值的强度信息
x1=np.loadtxt(r"D:\xinASDbo.txt")
y1=np.loadtxt(r"D:\guiASDq.txt")
UO2bo=np.loadtxt(r"D:\ha.txt")
UO2q=np.loadtxt(r"D:\xinshujuq.txt")
list5=[]
list6=[]
# 实测数据筛选大于阈值的数据
for j in range(len(UO2q)):
    if UO2q[j]>300:
        list2.append(j)
        print(UO2bo[j],UO2q[j])
        list5.append(UO2bo[j]) #252 #波长
        list6.append(UO2q[j])# 强度
list3=[]
list4=[]
# 筛选ASD筛选大于阈值的数据
for i in range(len(y1)):
    if y1[i]>0.02:
        list.append(i)
        print(x1[i],y1[i])
        list3.append(x1[i])   #23
        list4.append(y1[i]/2)
        
#----------寻峰部分--------
n=0
list7=[]
list10=[]
list11=[]
for k in range(len(list5)): #实测波长
    for o in range(len(list3)):   #ASD波长
        if abs(list5[k]-list3[o])<0.1:
            n+=1  
            #print(list5[k],list3[o])
            #print(list5[k])
           # print(list6[k])
            list7.append(list5[k])# 满足的实测波长
            list10.append(list3[o])
            list11.append(list6[k])
for q in range(len(list7)):
            print(list7[q],list11[q])


#-----插值部分
list8=UO2bo.tolist()
list9=[]
for cs in range(len(list7)):
    pa=list8.index(list7[cs])
    list9.append(pa)
#for q in range(len(list7)):
    #for w in range(len(list9)):
      #  print(w)

df3 = pd.DataFrame(list3)
df5 = pd.DataFrame(list5)
df00 = [None for i in range(len(df3))]
df01 = [None for i in range(len(df3))]
for i in range(len(df3)):
    temp_df5 = df5 - df3.iloc[i]
    df00[i] = temp_df5[abs(temp_df5.values) <0.1]
    df01[i] = len(df00[i])
    print(f'{list3[i]} nm: {df01[i]}')
print(f'Total: {sum(df01)}')


#-------------绘图部分--------------
"""
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy import signal 
list1=[]
x=np.loadtxt(r"D:\zhua1.txt")
y=np.loadtxt(r"D:\zhua2.txt")
bo=np.loadtxt(r"D:\bochang.txt")
J2=np.loadtxt(r"D:\Ju.txt")
Jl=np.loadtxt(r"D:\Ja.txt")
E2=np.loadtxt(r"D:\E2.txt")
A=np.loadtxt(r"D:\A1.txt")
for i in range(0,len(J2),1):
    a=(A[i]*((2*J2[i]+1)/(2*Jl[i]+1)))* math.exp((-1)*(E2[i]/8065.5)/2)
    list1.append(a)
num_peak = signal.find_peaks(list1, distance=1) 
print(num_peak[0])
print('the number of peaks is ' + str(len(num_peak[0])))
plt.plot(x, y, 'b', linewidth=1)
for j in  range(len(num_peak[0])):
    plt.plot(bo[num_peak[0][j]],list1[num_peak[0][j]],'o')
    plt.text(bo[num_peak[0][j]],list1[num_peak[0][j]],(bo[num_peak[0][j]],list1[num_peak[0][j]]))
plt.plot(bo, list1, 'r',label='jisuan')
plt.xlabel('nm')
plt.ylabel('count')
plt.legend(loc=4)
plt.show()
"""
#fig1, ax1 = plt.subplots()
#ax1.plot(x1,y1/5,color="r",linewidth=0.5)
#ax1.plot(UO2bo,UO2q,color="b",linewidth=0.3)
#ax1.set_ylim([0, 1000])

fig2 = plt.subplots()
#fig2 = plt.figure()
ax2 = plt.subplot(221)
#ax2.plot(x1,y1/5,color="r",linewidth=0.5)
ax2.plot(UO2bo,UO2q,color="b",linewidth=0.3,label="高精度")
ax2.set_xlim([382.5,384])
plt.legend(loc='upper left', bbox_to_anchor=(0.002, 0.99))
plt.xlabel("nm")
plt.ylabel("count")

#ax3 = plt.subplot(222)
#ax3.plot(x1,y1,color="r",linewidth=0.5)
#ax3.plot(UO2bo,UO2q,color="b",linewidth=0.3)
#ax3.set_xlim([390,395])

ax4 = plt.subplot(223)
ax4.plot(x1,y1,color="r",linewidth=0.5,label="ASD")
#ax4.plot(UO2bo,UO2q,color="b",linewidth=0.3)
#ax4.set_xlim([403,406])
ax4.set_xlim([382.5,384])
plt.xlabel("nm")
plt.ylabel("count")
plt.legend(loc='upper left', bbox_to_anchor=(0.002, 0.9520))

#ax5 = plt.subplot(224)
#ax5.plot(x1,y1/5,color="r",linewidth=0.5)
#ax5.plot(UO2bo,UO2q,color="b",linewidth=0.3)
#ax5.set_xlim([408,418])
# ax1 = plt.subplot(221)
# plt.xlim(380,390)
# ax2 = plt.subplot(222)
# plt.xlim(390,395)
# #plt.ylim(0,1000)
# plt.show()