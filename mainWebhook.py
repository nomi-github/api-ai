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

def processCurrencyConverter(parameters):
	baseurl = "http://www.tdbm.mn/script.php?mod=rate&ln=mn"
	currency = parameters.get("currency")
	if currency is None:
		return None
	result = urlopen(baseurl).read()
	table_data = [[cell.text for cell in row("td")]
						 for row in BeautifulSoup(result,"html.parser")("tr")]
	data = json.loads(json.dumps(table_data))
	res = makeWebhookResult(data, currency)
	return res
		
def processSpecificDistrictBranch(parameters):
	baseurl = 'http://tdbm.mn/bundles/tdbm/js/xml/Dists.xml'
	currency = parameters.get("distcode")
	if currency is None:
		return None
	result = urlopen(baseurl).read()
	table_data = [[cell.text for cell in row("td")]
						 for row in BeautifulSoup(result,"html.parser")("tr")]
	data = json.loads(json.dumps(table_data))
	res = makeWebhookResult(data, currency)
	return res

def processRequest(req):
	result = req.get("result")
	if (result is None):
		return None
	parameters = result.get("parameters")
	if (parameters is None):
		return None
		
	action = req.get("result").get("action")
	
	if action == "tdbCurrencyConverter":
		return processCurrencyConverter(parameters)
	elif action == "getBranchInSpecificDistrict":
		return processSpecificDistrictBranch(parameters)
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
			elements = []
			elements.append(constructFacebookListItem(key, "http://www.tdbm.mn/bundles/tdbm/css/img/icon/currency/" + key + ".png", "Өнөөдрийн ханш", "http://tdbm.mn/mn/exchange", []))
			elements.append(constructFacebookListItem(data[0][1], "https://www.mongolbank.mn/images/logo.png", value[1], "https://www.mongolbank.mn/dblistforexoa.aspx", []))
			elements.append(constructFacebookListItem(data[1][0], "https://seeklogo.com/images/T/TDB-logo-EE3C11F918-seeklogo.com.gif", 
						data[2][0] + ": " + value[2] + ", " + data[2][1] + ": "  + value[3], "https://www.mongolbank.mn/dblistforexoa.aspx", [constructFacebookButton("Зарах/Авах", "web_url", "http://tdbm.mn/mn/exchange", None)]))
			elements.append(constructFacebookListItem(data[1][1], "https://seeklogo.com/images/T/TDB-logo-EE3C11F918-seeklogo.com.gif", 
						data[2][0] + ": " + value[4] + ", " + data[2][1] + ": " + value[5], "https://www.mongolbank.mn/dblistforexoa.aspx", [constructFacebookButton("Ойр салбарыг хайх", "postback", None, "OIR_SALBARUUD_PAYLOAD")]))
						
						
			facebookData={
				  "facebook": {
				    "attachment": {
						"type": "template",
						"payload": {
							"template_type": "list",
							"elements": elements,
							 "buttons": [constructFacebookButton("Өөр валют сонго", "postback", None, "valutiin hansh")]
				 
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

def constructFacebookListItem(tittle, subtittle, image_url, url, buttons):
	if (buttons): 
		return {
			"title": tittle,
			"image_url": image_url,
			"subtitle": subtittle,
			"default_action": {
				"type": "web_url",
				"url": url,
				"webview_height_ratio": "tall"
			},
			"buttons": buttons   
		}
	else:
		return {
			"title": tittle,
			"image_url": image_url,
			"subtitle": subtittle,
			"default_action": {
				"type": "web_url",
				"url": url,
				"webview_height_ratio": "tall"
			} 
		}

def constructFacebookButton(tittle, type, url, payload):
	if (type == "web_url"):
		return {
			"title": tittle,
			"type": type,
			"url": url,
			"webview_height_ratio": "tall"
		}
	elif (type == "posback"):
		return {
			"title": tittle,
			"type": type,
			"payload": payload
		}
		
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')

