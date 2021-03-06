#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import codecs

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
			speech += "\nOnoodriin " + key + "-n hansh: " + data[0][1] + ": " + value[1]  + ", " + \
				 data[1][0] + "-" + data[2][0] + ": " + value[2] + ", " + \
				 data[1][0] + "-" + data[2][1] + ": " + value[3] + ", " + \
				 data[1][1] + "-" + data[2][0] + ": " + value[4] + ", " + \
				 data[1][1] + "-" + data[2][1] + ": " + value[5]
			facebookData={
				  "facebook": {
				     "attachment": {
					"type": "template",
					"payload": {
					    "template_type": "list",
					    "elements": [
						{
						    "title": key,
						    "image_url": "http://www.tdbm.mn/bundles/tdbm/css/img/icon/currency/" + key + ".png",
						    "subtitle": "Өнөөдрийн ханш",
						    "default_action": {
							"type": "web_url",
							"url": "http://tdbm.mn/mn/exchange",
							"webview_height_ratio": "tall"
						    }                    
						},
						{
						    "title": data[0][1],
						    "image_url": "https://www.mongolbank.mn/images/logo.png",
						    "subtitle": value[1],
						    "default_action": {
							"type": "web_url",
							"url": "https://www.mongolbank.mn/dblistforexoa.aspx",
							"webview_height_ratio": "tall"
						    },           
						},
						{
						    "title": data[1][0],
						    "image_url": "https://seeklogo.com/images/T/TDB-logo-EE3C11F918-seeklogo.com.gif",
						    "subtitle": data[2][0] + ": " + value[2] + ", " + data[2][1] + ": "  + value[3],
						    "default_action": {
							"type": "web_url",
							"url": "http://tdbm.mn/mn/exchange",
							"webview_height_ratio": "tall"
						    },
						    "buttons": [
							{
							    "title": "Зарах/Авах",
							    "type": "web_url",
							    "url": "http://tdbm.mn/mn/exchange",
							    "webview_height_ratio": "tall"
							}
						    ]                
						},
						{
						    "title": data[1][1],
						    "image_url": "https://seeklogo.com/images/T/TDB-logo-EE3C11F918-seeklogo.com.gif",
						    "subtitle": data[2][0] + ": " + value[4] + ", " + data[2][1] + ": " + value[5],
						    "default_action": {
							"type": "web_url",
							"url": "http://tdbm.mn/mn/exchange",
							"webview_height_ratio": "tall"
						    },
						    "buttons": [
							{
							    "title": "Ойр салбарыг хайх",
							    "type": "postback",
							    "payload": "OIR_SALBARUUD_PAYLOAD",
							    
							}
						    ]                
						},
					    ],
					     "buttons": [
						{
						    "title": "Өөр валют сонгох",
						    "type": "postback",
						    "payload": "valutiin hansh"                        
						}
					    ]  
					}
				    }

				  }
				}
   
			#print("%s: %s, %s: %s, %s-%s: %s, %s-%s: %s, %s-%s: %s, %s-%s: %s," %(data[0][0], key, data[0][1], value[1], data[1][0],data[2][0],value[2],data[1][0],data[2][1],value[3],data[1][1],data[2][0],value[4],data[1][1],data[2][1],value[5]))

	return {
		"speech": speech,
		"displayText": speech,
        	"data": facebookData,
        # "contextOut": [],
		"source": "apiai-nomi-test-currency-converter-webhook-sample"
	}


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

