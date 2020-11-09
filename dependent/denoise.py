# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 15:10:28 2020

@author: lenovo
"""


import matplotlib.pyplot as plt
import pywt
#import math
import numpy as np

#get Data
x1=np.loadtxt(r"D:\dicu.txt")
y1=np.loadtxt(r"D:\diq.txt")

index=[]
data=[]
coffs=[]

for i in range(len(y1)-1):
    X=float(i)
    Y=float(y1[i])
    index.append(X)
    data.append(Y)
#create wavelet object and define parameters
w=pywt.Wavelet('db8')#选用Daubechies8小波
maxlev=pywt.dwt_max_level(len(data),w.dec_len)
#print("maximum level is"+str(maxlev))
threshold=0.6  #Threshold for filtering

#Decompose into wavelet components,to the level selected:
coffs=pywt.wavedec(data,'db8',level=maxlev) #将信号进行小波分解

for i in range(1,len(coffs)):
    coffs[i]=pywt.threshold(coffs[i],threshold*max(coffs[i]))

datarec=pywt.waverec(coffs,'db8')#将信号进行小波重构
#plt.plot(x1,y1, 'r',label='jisuan')
plt.plot(x1,datarec, 'g',label='jisuan')
#mintime=0
#maxtime=mintime+len(data) 
#print(mintime,maxtime)
'''
plt.figure()
plt.subplot(3,1,1)
plt.plot(index[mintime:maxtime], data[mintime:maxtime])
plt.xlabel('time (s)')
plt.ylabel('microvolts (uV)')
plt.title("Raw signal")
plt.subplot(3, 1, 2)
plt.plot(index[mintime:maxtime], datarec[mintime:maxtime])
plt.xlabel('time (s)')
plt.ylabel('microvolts (uV)')
plt.title("De-noised signal using wavelet techniques")
plt.subplot(3, 1, 3)
plt.plot(index[mintime:maxtime],data[mintime:maxtime]-datarec[mintime:maxtime])
plt.xlabel('time (s)')
plt.ylabel('error (uV)')
plt.tight_layout()
plt.show()
'''