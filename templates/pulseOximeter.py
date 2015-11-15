# code for pulse oximeter

import numpy as np
import time
import math
import simpy
from scipy.signal import argrelextrema

# molar extintion coefficients at respective wavelengths 
eHb650 =   3750.12
eHb950 =   602.24
eHbO2950 = 1204
eHbO2650 = 368
#  equation for absorbativity from light intensity
# equation form A650 = eHb650 * Chb + eHbo2650 * ChbO2


def concentration(raw650,raw950):
    print('finding concentration')
    mat1 = np.array([[eHb650,eHbO2650],[eHb950,eHbO2950]])
    cHb = []
    cHbO2 = []
    sO2 = []
    c = np.array([])
    total = 0
    avg = 0
    for x in  range (raw650.size):
        b = np.array([raw650[x],raw950[x]])
        try:
            c = np.linalg.solve(mat1,b)
        except:
            print('couldnt solve system of equations')
        if c.size != 0:
            cHb.append(c[0])
            cHbO2.append(c[1])
    for h in range(len(cHb)):
        l = cHbO2[h] / (cHb[h] + cHbO2[h])
        sO2.append(l)
        
    nuArray = np.array(sO2)
    oxy = np.average(reject_outliers(nuArray))
    print('the percent oxygenation is ')
    print(oxy)
    heartBeat(raw650)
    

def reject_outliers(data, m = 2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]

def heartBeat(raw950):
     sampleRate = 1
     heartBeat = 0
     print('in heartbeat')
     print(raw650)
     nuRaw650 = np.array(raw650)
     print(nuRaw650)
     dist = 0
     localMax = argrelextrema(raw650,np.greater)
     print(localMax)
     for z in range (localMax[0].size):
         if z != 0:
             dist = dist + localMax[0][z] - localMax[0][z-1]
     print(dist)
     if dist != 0:
        avgDist = dist/localMax[0].size
        heartBeat = avgDist * sampleRate

     print(heartBeat)
     getData()


def getData():    #function called to get data
    
    startTime = time.time()
    raw650 = np.array([33,45,34,80,26,45,60,93,63])
    raw950 = np.array([20,22,34,60,55,40,55,72,60])
  
    while True:

        if time.time() - startTime >= 5:
           startTime = time.time()
           print('got data')
           heartbeat(raw950)


getData()

    


    
     
    
         
            
        
        

