from flask import Flask, request, render_template
from twilio import twiml
from twilio.rest import TwilioRestClient
from pymongo import MongoClient
from threading import Thread
import time

app = Flask(__name__)
mClient = MongoClient("localhost", 27017)
db = mClient.test

myTwilioPhone = "+14155697669"
accountSID = "ACa404484dc7120971067789bf4ad96f52"
authToken = "4caf331b14c23d5d6644669d3352770b"
myURL = "https://cbc8a8c8.ngrok.io" #ngrok url here


def delayCall(totalDelay, _phoneNumber, currentTime):
	client = TwilioRestClient(accountSID, authToken)
	time.sleep(totalDelay)
	call = client.calls.create(to=_phoneNumber,
							from_=myTwilioPhone,
							url=myURL+"/prompt/"+currentTime)


def delayCall2(totalDelay, _phoneNumber, fizzBuzzNum):
	client = TwilioRestClient(accountSID, authToken)
	time.sleep(totalDelay)
	call = client.calls.create(to=_phoneNumber,
							from_=myTwilioPhone,
							url=myURL+"/fizzBuzz2/"+fizzBuzzNum)


def updateHistory():
	hist = []
	cursor = db.calls.find()
	for doc in cursor:
		entry = []
		entry.append(doc["date"])
		entry.append(doc["delay"])
		entry.append(doc["phoneNum"])
		entry.append(doc["fizzBuzzNum"])
		hist.append(entry)
	return hist


@app.route("/")
def main():
	hist = updateHistory()
	return render_template("index.html",
							history = hist)


@app.route("/getNumber", methods=["POST"])
def getNumber():
	client = TwilioRestClient(accountSID, authToken)
	_phoneNumber = request.form["phoneNumber"]
	_hourDelay = request.form.get("hourDelay", 0)
	_minDelay = request.form.get("minDelay", 0)
	_secDelay = request.form.get("secDelay", 0)

	totalDelay = int(_hourDelay)*3600 + int(_minDelay)*60 + int(_secDelay)
	currentTime = time.strftime("%m-%d-%Y-%H:%M:%S")
	if _phoneNumber and _hourDelay and _minDelay and _secDelay:
		db.calls.insert_one(
			{
				"date": currentTime,
				"delay": _hourDelay + " hours " + 
						_minDelay + " minutes " +
						_secDelay + " seconds",
				"totalDelay": totalDelay,
				"phoneNum": _phoneNumber,
				"fizzBuzzNum": ""
			}
		)
	if (totalDelay > 0):
		t = Thread(target=delayCall, args=(totalDelay, _phoneNumber, currentTime))
		t.start()
	else:
		call = client.calls.create(to=_phoneNumber,
									from_=myTwilioPhone,
									url=myURL+"/prompt/"+currentTime)
	r = twiml.Response()
	return str(r)


@app.route("/prompt/<currentTime>", methods=['GET', 'POST'])
def prompt(currentTime):
	r = twiml.Response()
	with r.gather(numDigits=2, action="/fizzBuzz/"+currentTime, method="POST") as g:
		g.say("Enter a number.")
	return str(r)


@app.route("/fizzBuzz/<currentTime>", methods=['GET', 'POST'])
def fizzBuzz(currentTime):
	num = request.values.get('Digits', None)
	if (num):
		db.calls.update_one(
			{"date": currentTime},
			{
				"$set": {
					"fizzBuzzNum": str(num)
				}
			}
		)
	else:
		db.calls.update_one(
			{"date": currentTime},
			{
				"$set": {
					"fizzBuzzNum": "0"
				}
			}
		)

	r = twiml.Response()
	fb = ""
	for i in range(1, int(num)+1):
		if (i%3 == 0) and (i%5 == 0):
			fb += "Fizz Buzz, "
		elif i%3 == 0:
			fb += "Fizz, "
		elif i%5 == 0:
			fb += "Buzz, "
		else:
			fb += str(i) + ", "
	r.say(fb)
	return str(r)

@app.route("/fizzBuzz2/<fizzBuzzNum>", methods=['GET', 'POST'])
def fizzBuzz2(fizzBuzzNum):
	r = twiml.Response()
	fb = ""
	for i in range(1, int(fizzBuzzNum)+1):
		if (i%3 == 0) and (i%5 == 0):
			fb += "Fizz Buzz, "
		elif i%3 == 0:
			fb += "Fizz, "
		elif i%5 == 0:
			fb += "Buzz, "
		else:
			fb += str(i) + ", "
	r.say(fb)
	return str(r)

@app.route("/redial/<date>", methods=['GET', 'POST'])
def redial(date):
	client = TwilioRestClient(accountSID, authToken)
	cursor = db.calls.find({"date": date})
	for doc in cursor:
		_phoneNumber = doc["phoneNum"]
		delay = doc["delay"]
		totalDelay = doc["totalDelay"]
		fizzBuzzNum = doc["fizzBuzzNum"]

	currentTime = time.strftime("%m-%d-%Y-%H:%M:%S")
	db.calls.insert_one(
		{
			"date": currentTime,
			"delay": delay,
			"totalDelay": totalDelay,
			"phoneNum": _phoneNumber,
			"fizzBuzzNum": fizzBuzzNum
		}
	)

	if (int(totalDelay) > 0):
		t = Thread(target=delayCall2, args=(int(totalDelay), _phoneNumber, fizzBuzzNum))
		t.start()
	else:
		call = client.calls.create(to=_phoneNumber,
								from_=myTwilioPhone,
								url=myURL+"/fizzBuzz2/"+fizzBuzzNum)

	r = twiml.Response()
	return str(r)


if __name__ == "__main__":
	app.run(debug=True)