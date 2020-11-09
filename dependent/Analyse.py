import pandas as pd
import numpy as np
import pywt
from copy import copy
from collections.abc import Iterable
import time
Index = ["波长nm","计数count"]
Peak = {"U":[367.007, 378.284, 385.464, 424.166, 434.169, 454.363, 387.103, 389.036, 405.004, 409.013, 417.159],"U*":[385.957,386.592,393.202]}

# 降噪
def reduceNoise(data: pd.DataFrame, threshold: float) -> pd.DataFrame:
    yData = data[Index[1]].values
    # 初始化小波降噪
    w = pywt.Wavelet('db8')  # 选用Daubechies8小波
    maxLevel = pywt.dwt_max_level(yData.shape[0], w.dec_len)
    coffs = pywt.wavedec(yData, 'db8', level=maxLevel)
    for i in range(1, len(coffs)):
        coffs[i] = pywt.threshold(coffs[i], threshold * max(coffs[i]))
    dataRec = pywt.waverec(coffs, 'db8')  # 将信号进行小波重构
    result = copy(data)
    result.loc[:,Index[1]] = dataRec[:result.shape[0]]
    return result

# 扣除本底
def backgroundSubraction(data: pd.DataFrame) -> pd.DataFrame:
    yData_raw = data[Index[1]].values
    yData_LLS = np.log(np.log(np.sqrt(yData_raw + abs(np.min(yData_raw))+1)+ 1)+ 1)
    for i in range(13,yData_LLS.shape[0]-13):
        tmpStorage = np.empty(13)
        for j in range(13):
            tmpStorage[j] = (yData_LLS[i+j] + yData_LLS[i-j])/2
        yData_LLS[i] = np.min(tmpStorage)
    yData_SNIP = np.exp(np.exp(yData_LLS-1)**2-1)
    yData_raw[13:] = yData_raw[13:] - yData_SNIP[13:]
    result = copy(data)
    result.loc[:,Index[1]] = yData_raw
    return result

# 将小于阈值的数据置零
def replaceZeroFromThreshold(data: pd.DataFrame,threshold: float) -> pd.DataFrame:
    result = copy(data)
    needChange = data[Index[1]].values < threshold
    result.loc[needChange,Index[1]] = 0
    return result

# 筛选大于阈值的数据
def siftiongFromThreshold(data: pd.DataFrame, threshold: float) -> pd.DataFrame:
    index = data[Index[1]].values >= threshold
    return data.iloc[index]

# 计数转变成强度信息/归一化
def countTranslateTontensityI(MeasureData: pd.DataFrame) -> pd.DataFrame:
    yData = MeasureData[Index[1]].values
    CunteSum = np.sum(yData)
    return pd.DataFrame({Index[0]:MeasureData[Index[0]].values,Index[1]:yData/CunteSum})

# 寻找匹配峰位置
def findFitPeak(ASD_Data: pd.DataFrame,Measured_Data: pd.DataFrame) -> list:
    Measured_wavelength = Measured_Data["波长nm"].values
    result = []
    for i in ASD_Data["波长nm"]:
        diffValues = Measured_wavelength - i
        checkFit = np.abs(diffValues) < 0.1
        result.extend(Measured_wavelength[checkFit].tolist())
    result = list(set(result))
    result.sort()
    return result

# 寻找特征峰是否存在
def findCharacteristicPeaf(peak,waveLength: np.array,sigma: float = 0.01):
    if isinstance(peak, Iterable):
        result = []
        for i in peak:
            result.append(findCharacteristicPeaf(i,waveLength))
        return result
    else:
        check: np.array = np.abs(waveLength - peak) < sigma
        if np.sum(check.astype("int64")) > 0:
            result = True
        else:
            result = False
        return result

# 寻找目标波长范围内的峰
def findPeak(peak, data: pd.DataFrame,sigma: float = 0.01, threshold: float = 0.):
    waveLength = data[Index[0]].values
    check: np.array = np.abs(waveLength - peak) < sigma
    # 检查目标附近是否有数据
    if np.sum(check.astype("int64")) > 0:
        yData = np.max(data[Index[1]].values[check])    #获取峰（最大值）
        # 检查峰是否大于阈值
        if yData >= threshold:
            d = data.loc[check].set_index(Index[1])
            tmp = d.loc[yData]
            if tmp.shape[0] > 1:
                xData = tmp.iloc[0].values[0]
            else:
                xData = d.loc[yData][0]
            return (xData,yData)
    return None

# 将光谱向右平移
def moveWaveLength(data: pd.DataFrame,moveToRigh: float) -> pd.DataFrame:
    xData = data[Index[0]].values + moveToRigh
    yData = data[Index[1]].values
    d = pd.DataFrame(columns=Index)
    d.loc[:,Index[0]] = xData
    d.loc[:,Index[1]] = yData
    return d

# 求光谱面积
def calculateArea(data: pd.DataFrame):
    xData = data[Index[0]].values
    yData = data[Index[1]].values
    xDiff = xData[1:] - xData[:-1]
    yAverge = (yData[:-1] + yData[1:])/2
    result = np.sum(xDiff * yAverge)
    return result

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    measure = pd.read_csv("../data/低精度.txt",sep="\s+")
    measure1 = reduceNoise(measure,0.6)
    measure2 = backgroundSubraction(measure1)
    measure3 = replaceZeroFromThreshold(measure2,0.)
    measure4 = countTranslateTontensityI(measure3)
    print(calculateArea(measure4))
    plt.plot(measure4[Index[0]].values,measure4[Index[1]].values)
    plt.show()
