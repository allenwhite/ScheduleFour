from flask import Flask, render_template, request, redirect, session, send_from_directory
import requests
import json
from uuid import uuid4
import threading
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


app = Flask(__name__)
app.secret_key = 'dotBOTRuleZ'


urlBase 		= 'https://api.spark.io/v1/devices/'
access_token 	= '25dfc450c2733a52989c60ddc96c0944e45f54c1'
deviceID 		= '1f0036000147343337373738'
getFunc1 		= 'analog_val_1'
getFunc2 		= 'analog_val_2'
s1 				= 'sessionArray1'
s2				= 'sessionArray2'
s1Vals			= 'sessionArray1Values'
s2Vals			= 'sessionArray2Values'
sDates			= 'sessionArrayDates'

dataPointsToRetrieve = 15


def getForFunc1():
	fullUrl = urlBase + deviceID + '/' + getFunc1 + '/?access_token=' + access_token 
	return getCodeFromSensor(fullUrl)


def getForFunc2():
	fullUrl = urlBase + deviceID + '/' + getFunc2 + '/?access_token=' + access_token 
	return getCodeFromSensor(fullUrl)



def getCodeFromSensor(fullUrl):
	try:
		r = requests.get(fullUrl, timeout=2)
		if r.status_code > 199 and r.status_code < 300:
			# print json.dumps(r.json())
			return r.json()
		else:
			print str(r.content)
			return None	
	except Exception, e:
		print str(e)
		return None
	

def getFullSetOfResults():
	session[s1] = [None] * dataPointsToRetrieve
	session[s1Vals] = [None] * dataPointsToRetrieve
	session[sDates] = [None] * dataPointsToRetrieve
	for x in xrange(0,len(session[s1])):
		session[s1][x] = getForFunc1()
		print '! -- ' +  str(session[s1][x])
		session[s1Vals][x] = session[s1][x]['result']
		session[sDates][x] = session[s1][x]['coreInfo']['last_heard']

	session[s2Vals] = [None] * dataPointsToRetrieve
	session[s2] = [None] * dataPointsToRetrieve
	for x in xrange(0,len(session[s2])):
		session[s2][x] = getForFunc2()
		session[s2Vals][x] = session[s2][x]['result']



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



@app.route('/', methods=['GET'])
def gimmeResults():
	getFullSetOfResults()
	# Do calculations for arrays of values to create one new array, replace the part below
	# with just one array
	processData()
	# return json.dumps({"arrayVals":session[finalVals], "arrayDates":session[sDates]}, DONT NEED INDENT)
	return json.dumps(session[s1])




@app.route('/getBigNumber', methods=['GET'])
def getBigNumber():
	pass




@app.route('/web', methods=['GET'])
def web():
	# This method calculates the values form sensor one (s1Vals) and sensor two (s2Vals) as well as
	# stores the corresponding dates (sDates)
	getFullSetOfResults()
	# This code renders the test_index.html file and passes the data from both sensors in
	# and then these values are plotted (see the html file)
	return render_template('test_index.html', data=session[s1])


@app.route('/gen_large_graph', methods=['GET'])
def genLargeGraph():
	# See code in '/' for what needs to be done here as well; basically just need to execute the script
	# greg wrote using the data from this API so that processed values are plotted
	getFullSetOfResults()
	return render_template('large_graph.html', data=session[s1])


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=6969,debug=True)
