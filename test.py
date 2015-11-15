from flask import Flask, render_template, request, redirect, session, send_from_directory
import requests
import json
from uuid import uuid4
import threading


app = Flask(__name__)
app.secret_key = 'dotBOTRuleZ'


urlBase 		= 'https://api.spark.io/v1/devices/'
access_token 	= '25dfc450c2733a52989c60ddc96c0944e45f54c1'
deviceID 		= '1f0036000147343337373738'
getFunc1 		= 'analog_val_1'
getFunc2 		= 'analog_val_2'
s1 				= 'sessionArray1'
s2				= 'sessionArray2'

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
	for x in xrange(0,len(session[s1])):
		session[s1][x] = getCodeFromSensor()


	session[s2] = [None] * dataPointsToRetrieve
	for x in xrange(0,len(session[s2])):
		session[s2][x] = getCodeFromSensor()



@app.route('/', methods=['GET'])
def gimmeResults():
	getFullSetOfResults()
	return json.dumps({"array1":session[s1], "array2":session[s2]})



@app.route('/web', methods=['GET'])
def web():
	getFullSetOfResults()
	return render_template('test_index.html', data={"array1":session[s1], "array2":session[s2]})


@app.route('/gen_large_graph', methods=['GET'])
def genLargeGraph():
	getFullSetOfResults()
	return render_template('large_graph.html', data={"array1":session[s1], "array2":session[s2]})


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=6969,debug=True)
