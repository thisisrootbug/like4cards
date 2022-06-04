#"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import ast
import logging
import requests
import time as formal_time
from odoo import http
from odoo.addons.restful.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
from odoo.http import request
#from odoo.addons.restful.controller import validate_token
from Crypto.Cipher import AES
import base64
import hashlib
import math
import json

_logger = logging.getLogger(__name__)


class Like4Cards(http.Controller):

    try:
        creds = request.env['res.config.settings'].sudo().get_values()
    except Exception as ops:
        _logger.error(ops)
        # Please, find below your account's credentials for testing:
	#in testing mode, you can create a test order containing only one of the test cards ( productId = 819 ) 
        creds = {
                "like4cards_deviceid": "233cb68f094fade2054f289990049705c571184990a3f410a6c5b8a43c3d229a",
                "like4cards_email": "ali@saleproo.com",
                "like4cards_password": "0f4a8609f73739cb4477e8e5a86b2bdd62aee2f4af72f355ab9afd0a1936c03e",
                "like4cards_securitycode": "f47beeb40b63599114916cf3629fbc868847d5d2c0872b8135fde0919db55642",
                'like4cards_phone': "966507224222222",
                'like4cards_hash_key': "8Tyr4EDw!2sN" ,
                'like4cards_secret_key': "t-3zafRa" ,
                'like4cards_secret_iv': "St@cE4eZ" ,
                }

    def generateHash(self,vals):
        data = "%s%s%s%d" % (vals['email'].lower(),self.creds['like4cards_phone'],self.creds['like4cards_hash_key'],vals['time'])
        return hashlib.sha256(data.encode()).hexdigest()

    def decryptSerial(self,serialCode):
        key = hashlib.sha256(self.creds["like4cards_secret_key"].encode('utf-8')).hexdigest()[:32]
        iv = hashlib.sha256(self.creds["like4cards_secret_iv"].encode('utf-8')).hexdigest()[:16]
        decrypted = b''
        encrypted = base64.b64decode(base64.b64decode(serialCode))
        cipher = AES.new(key, AES.MODE_CBC,iv)
        decrypted += cipher.decrypt(encrypted[:16])
        unpadded = decrypted[:-ord(decrypted[len(decrypted)-1:])]
        if unpadded == b'':
            unpadded = decrypted
        return unpadded.decode('utf-8')

    #@validate_token
    @http.route("/online/check_balance", auth="public", method=["POST"],type='http', csrf=False)
    def check_balance(self,langId=2, **kw):
        data = {"deviceId": self.creds["like4cards_deviceid"],
		"email": self.creds["like4cards_email"],
		"password": self.creds["like4cards_password"],
		"securityCode": self.creds["like4cards_securitycode"],
		"langId": langId,
                }
        res = requests.post("https://taxes.like4app.com/online/check_balance",data=data)
        return res.text


    #@validate_token
    @http.route("/online/categories", auth="public", method=["POST"],type='http', csrf=False)
    def categories(self,langId=2, **kw):
        data = {"deviceId": self.creds["like4cards_deviceid"],
		"email": self.creds["like4cards_email"],
		"password": self.creds["like4cards_password"],
		"securityCode": self.creds["like4cards_securitycode"],
		"langId": langId,
	}
        res = requests.post("https://taxes.like4app.com/online/categories",data=data)
        return res.text


    #@validate_token
    @http.route("/online/products", auth="public", method=["POST"],type='http', csrf=False)
    def products(self,langId=2,categoryId=0,ids=[], **kw):
        data = {"deviceId": self.creds["like4cards_deviceid"],
		"email": self.creds["like4cards_email"],
		"password": self.creds["like4cards_password"],
		"securityCode": self.creds["like4cards_securitycode"],
		"langId": langId,
	}
        if ids != []:
            data_ids = ast.literal_eval(ids)
            data.update({"ids[]": data_ids})
        elif categoryId != 0:
            data["categoryId"] = categoryId
            res = requests.post("https://taxes.like4app.com/online/products",data=data)
            return res.text


    #@validate_token
    @http.route("/online/orders", auth="public", method=["POST"],type='http', csrf=False)
    def orders(self,langId=2,page=1,orderType="asc",fromUnixTime=0.0,toUnixTime=1651439620.631006, **kw):
        data = {"deviceId": self.creds["like4cards_deviceid"],
		"email": self.creds["like4cards_email"],
		"password": self.creds["like4cards_password"],
		"securityCode": self.creds["like4cards_securitycode"],
		"langId": langId,
                }
        res = requests.post("https://taxes.like4app.com/online/orders",data=data)
        return res.text



    #@validate_token
    @http.route("/online/orders/details", auth="public", method=["POST"],type='http', csrf=False)
    def orders_details(self,langId=2, orderId=0,referenceId="", **kw):
        data = {"deviceId": self.creds["like4cards_deviceid"],
		"email": self.creds["like4cards_email"],
		"password": self.creds["like4cards_password"],
		"securityCode": self.creds["like4cards_securitycode"],
		"langId": langId,
                }
        if orderId != 0:
            data["orderId"] = orderId
        if referenceId != "":
            data["referenceId"] = referenceId
        res = requests.post("https://taxes.like4app.com/online/orders/details",data=data)
        return res.text



    #@validate_token
    @http.route("/online/create_order", auth="public", method=["POST"],type='http', csrf=False)
    def create_order(self,langId=2, productId=0,referenceId="",time=0,quantity=1,optionalFields={},  **kw):
        data = {"deviceId": self.creds["like4cards_deviceid"],
		"email": self.creds["like4cards_email"],
		"password": self.creds["like4cards_password"],
		"securityCode": self.creds["like4cards_securitycode"],
		"quantity": quantity,
		"langId": langId,
	}
        if productId != 0:
            data["productId"] = int(productId)
        if referenceId != "":
            data["referenceId"] = referenceId
        if time != 0:
            data["time"] = int(time)
        else:
            data["time"] = int(formal_time.time())
        if optionalFields != {}:
            data["optionalFields"] = optionalFields
        data['hash'] = self.generateHash(data)
        res = requests.post("https://taxes.like4app.com/online/create_order",data=data)
        jdata = json.loads(res.text)
        if(jdata["response"] == 1):
            for i in range(len(jdata["serials"])):
                jdata["serials"][i]["serialCode"] = self.decryptSerial(jdata["serials"][i]["serialCode"])
            #request.env['pos.order'].sudo().create({})
        return json.dumps(jdata)


    @http.route("/like4cards/get_categories", auth="user", method=["POST"],type='json')
    def get_categories(self,langId=2, **kw):
        data = {"deviceId": self.creds["like4cards_deviceid"],
		"email": self.creds["like4cards_email"],
		"password": self.creds["like4cards_password"],
		"securityCode": self.creds["like4cards_securitycode"],
		"langId": langId,
	}
        res = requests.post("https://taxes.like4app.com/online/categories",data=data)
        return res.text

    @http.route("/like4cards/get_products", auth="user", method=["POST"],type='json')
    def get_products(self,langId=2,categoryId=0,ids=[], **kw):
        data = {"deviceId": self.creds["like4cards_deviceid"],
		"email": self.creds["like4cards_email"],
		"password": self.creds["like4cards_password"],
		"securityCode": self.creds["like4cards_securitycode"],
		"langId": langId,
	}
        if categoryId != 0:
            data["categoryId"] = categoryId
            res = requests.post("https://taxes.like4app.com/online/products",data=data)
            return res.text

    @http.route("/like4cards/create_order", auth="user", method=["POST"],type='json')
    def pos_create_order(self,langId=2, productId=0,referenceId="",time=0,quantity=1,optionalFields={},  **kw):
        data = {"deviceId": self.creds["like4cards_deviceid"],
		"email": self.creds["like4cards_email"],
		"password": self.creds["like4cards_password"],
		"securityCode": self.creds["like4cards_securitycode"],
		"quantity": quantity,
		"langId": langId,
	}
        if productId != 0:
            data["productId"] = int(productId)
        if referenceId != "":
            data["referenceId"] = referenceId
        if time != 0:
            data["time"] = int(time)
        else:
            data["time"] = int(formal_time.time())
        if optionalFields != {}:
            data["optionalFields"] = optionalFields
        data['hash'] = self.generateHash(data)
        res = requests.post("https://taxes.like4app.com/online/create_order",data=data)
        jdata = json.loads(res.text)
        if(jdata["response"] == 1):
            for i in range(len(jdata["serials"])):
                jdata["serials"][i]["serialCode"] = self.decryptSerial(jdata["serials"][i]["serialCode"])
        return json.dumps(jdata)


    #@validate_token
    @http.route("/like4cards/order_details", auth="user", method=["POST"],type='json')
    def orders_details(self,langId=2, orderId=0,referenceId="", **kw):
        data = {"deviceId": self.creds["like4cards_deviceid"],
		"email": self.creds["like4cards_email"],
		"password": self.creds["like4cards_password"],
		"securityCode": self.creds["like4cards_securitycode"],
		"langId": langId,
                }
        if orderId != 0:
            data["orderId"] = orderId
        if referenceId != "":
            data["referenceId"] = referenceId
        res = requests.post("https://taxes.like4app.com/online/orders/details",data=data)
        jdata = json.loads(res.text)
        if(jdata["response"] == 1):
            for i in range(len(jdata["serials"])):
                jdata["serials"][i]["serialCode"] = self.decryptSerial(jdata["serials"][i]["serialCode"])
        return json.dumps(jdata)

