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
    if req.get("result").get("action") != "tdbCurrencyConverter":
        return {}
    baseurl = "http://www.tdbm.mn/script.php?mod=rate&ln=mn"
    #result = req.get("result")
	#parameters = result.get("parameters")
    #currency = parameters.get("currency")
    #if city is None:
    #    return None
		
    #yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(baseurl).read()
    table_data = [[cell.text for cell in row("td")]
                         for row in BeautifulSoup(result)("tr")]
	data = json.dumps(OrderedDict(table_data))
	#data = json.loads(result)
    print data
	#res = makeWebhookResult(data)
    return res



def makeWebhookResult(data):

    return {
        "speech": "here is your result",
        "displayText": data,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-nomi-test-currency-converter-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

