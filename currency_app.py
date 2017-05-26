#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

from bs4 import BeautifulSoup

						 
# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
	if req.get("result").get("action") == "tdbCurrencyConverter":
		baseurl = "http://www.tdbm.mn/script.php?mod=rate&ln=mn"
		result = req.get("result")
		if (result is None):
			return None
		parameters = result.get("parameters")
		if (parameters is None):
			return None
		currency = parameters.get("currency")
		if currency is None:
		    return None
			
		#yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
		result = urlopen(baseurl).read()
		table_data = [[cell.text for cell in row("td")]
							 for row in BeautifulSoup(result,"html.parser")("tr")]
		data = json.loads(json.dumps(table_data))
		#data = json.loads(result)
		#print data
		res = makeWebhookResult(data, currency)
		return res
	else:
		return {
			"speech": "no result",
			"displayText": "no result",
			# "data": data,
			# "contextOut": [],
			"source": "apiai-nomi-test-currency-converter-webhook-sample"
		}

def makeWebhookResult(data, valutName):
	speech = ""
	facebookData={
		"facebook": {
			"text":{ 
			     "default answer from Webhook"
			 }
		}
	}
	
	for value in data:
		key=''.join(value[0].split())
		if (len(value)==6 and (key==valutName or valutName=="ALL")):
			#print(value[4])
			speech += "\nOnoodriin " + key + "-n hansh: " +  + ": " + value[1]  + ", " + \
				 data[1][0] + "-" + data[2][0] + ": " + value[2] + ", " + \
				 data[1][0] + "-" + data[2][1] + ": " + value[3] + ", " + \
				 data[1][1] + "-" + data[2][0] + ": " + value[4] + ", " + \
				 data[1][1] + "-" + data[2][1] + ": " + value[5]
	 		facebookData={
				"facebook": {
					 "text":{ 
					     "Response from webhook"
					 },
					 "attachment": {
						"type": "template",
						"payload": {
						    "template_type": "generic",
						    "elements": [
							{
							    "title": "Smurfs: The Lost Village (2017)",
							    "image_url": "https://www.moovrika.com/ext/makeimg.php?tbl=movies&id=15666&img=1&type=image&movie=Smurfs+The+Lost+Village&fs=400",
							    "subtitle": "Smurfette attempts to find her purpose in the village. When she encounters a creature in the Forbidden Forest who drops a mysterious map, she sets off with her friends Brainy, Clumsy, and Hefty on an adventure to find the Lost Village before the evil wizard Gargamel does.",
							    "default_action": {
								"type": "web_url",
								"url": "https://www.moovrika.com/m/15666",
								"webview_height_ratio": "tall"
							    },
							    "buttons": [
								{
								    "title": "more info",
								    "type": "web_url",
								    "url": "https://www.moovrika.com/m/4082",
								    "webview_height_ratio": "tall"
								},
							       {
								    "title": "View trailer",
								    "type": "web_url",
								    "url": "https://www.moovrika.com/m/4082",
								    "webview_height_ratio": "tall"
								}
							    ]
							},
							{
							    "title": "Resident Evil: The Final Chapter (2017)",
							    "image_url": "https://www.moovrika.com/ext/makeimg.php?tbl=movies&id=4167&img=1&type=image&movie=Resident+Evil+The+Final+Chapter&fs=400",
							    "subtitle": "Resident Evil: The Final Chapter is an upcoming science fiction action horror film written and directed by Paul W. S. Anderson. It is the sequel to Resident Evil: Retribution (2012), and will be the sixth and final installment in the Resident Evil film series, which is very loosely based on the Capcom survival horror video game series Resident Evil.",
							    "default_action": {
								"type": "web_url",
								"url": "https://www.moovrika.com/m/4167",
								"webview_height_ratio": "tall"
							    },
							    "buttons": [
								{
								    "title": "more info",
								    "type": "web_url",
								    "url": "https://www.moovrika.com/m/4082",
								    "webview_height_ratio": "tall"
								}
							    ]
							}
						    ]
						}
					      }
					}
				}
	
			#print("%s: %s, %s: %s, %s-%s: %s, %s-%s: %s, %s-%s: %s, %s-%s: %s," %(data[0][0], key, data[0][1], value[1], data[1][0],data[2][0],value[2],data[1][0],data[2][1],value[3],data[1][1],data[2][0],value[4],data[1][1],data[2][1],value[5]))

	return JSON.stringify({
		"speech": speech,
		"displayText": speech,
        	"data": facebookData,
        # "contextOut": [],
		"source": "apiai-nomi-test-currency-converter-webhook-sample"
	})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

