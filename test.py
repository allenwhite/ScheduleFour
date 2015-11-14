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
getFunc 		= 'analog_value'
s 				= 'sessionArray'

dataPointsToRetrieve = 15


def getCodeFromSensor():
	fullUrl = urlBase + deviceID + '/' + getFunc + '/?access_token=' + access_token 
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
	session[s] = [None] * dataPointsToRetrieve
	for x in xrange(0,len(session[s])):
		session[s][x] = getCodeFromSensor()



@app.route('/', methods=['GET'])
def gimmeResults():
	getFullSetOfResults()
	return json.dumps(session[s])



@app.route('/web', methods=['GET'])
def web():
	getFullSetOfResults()
	return render_template('index.html', data=session[s])



if __name__ == "__main__":
    app.run(host='0.0.0.0',port=6969,debug=True)
