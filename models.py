import uuid
from datetime import datetime
import json
from flask import session
import os
import requests

class User:
    def placeOrder(userinfo):
        user = {
            "custPhone":userinfo["phone"],
            "last":userinfo["last"],
            "first":userinfo["first"],
            "dob":userinfo["dob"],
            "address":userinfo["address"],
            "pharmacy":userinfo["pharmacy"],
            "rx":userinfo["rx"],
            "username":userinfo["first"], #default: username=first,pw=last
            "password":userinfo["last"]
        }

        orderNum = requests.post("https://rx2u-rest.appspot.com/orderService/placeOrder",json=user)
        return orderNum.text

    def timestamp():
        epoch = datetime.utcfromtimestamp(0)
        now = datetime.now()
        delta = now - epoch
        return delta.total_seconds()

    def checkOrderStatus():
        data = requests.get("https://rx2u-rest.appspot.com/rest/orderService/checkOrders")
        return data.json()

    def lookupOrder(orderNum):
        order = requests.get("https://rx2u-rest.appspot.com/rest/orderService/lookupOrder/"+orderNum)
        return order.json()

    def populateOrders(phoneNum):
        orders = requests.get("https://rx2u-rest.appspot.com/rest/customerService/getProfile/"+phoneNum)
        return orders.json()

    def populateUserOrders(phoneNum):
        orders = requests.get("https://rx2u-rest.appspot.com/rest/customerService/getProfile/"+phoneNum)
        return orders.json()

    def populateUserInfo(phoneNum):
        orders = requests.get("https://rx2u-rest.appspot.com/rest/customerService/getUserInfo/"+phoneNum)
        return orders.json()

    def receiveOrder(orderNum):
        res = requests.put("https://rx2u-rest.appspot.com/rest/customerService/receive/"+orderNum)
        return res.text

    def find(username):
        user = requests.post("https://rx2u-rest.appspot.com/rest/customerService/checkUser?username="+username)
        return user.text

    def register(userinfo):
        user = {
            "custPhone":userinfo["phone"],
            "last":userinfo["last"],
            "first":userinfo["first"],
            "dob":userinfo["dob"],
            "address":userinfo["address"],
            "pharmacy":userinfo["pharmacy"],
            "rx":userinfo["rx"],
            "username":userinfo["username"],
            "password":userinfo["password"]
        }
        res = requests.post("https://rx2u-rest.appspot.com/rest/customerService/registerUser",json=user)
        return res.text

    def verifyPassword(username, password):
        res = requests.post("https://rx2u-rest.appspot.com/rest/customerService/authenticate?username="+username+"&password="+password)
        return res.text

class Pharmacy:
    def populateOrders():
        orders = requests.get("https://rx2u-rest.appspot.com/rest/pharmacyService/populateOrders")
        return orders.json()

    def fillOrder(orderNum):
        res = requests.put("https://rx2u-rest.appspot.com/rest/pharmacyService/fillOrder/"+orderNum)
        return res.text

    def completeOrder(orderNum):
        res = requests.put("https://rx2u-rest.appspot.com/rest/pharmacyService/completeOrder/"+orderNum)
        return res.text

class Uber:
    def populateOrders():
        orders = requests.get("https://rx2u-rest.appspot.com/rest/uberService/populateOrders")
        return orders.json()

    def acceptOrder(orderNum):
        res = requests.put("https://rx2u-rest.appspot.com/rest/uberService/acceptOrder/"+orderNum)
        return res.text

    def startOrder(orderNum):
        res = requests.put("https://rx2u-rest.appspot.com/rest/uberService/startOrder/"+orderNum)
        return res.text

    def endOrder(orderNum):
        res = requests.put("https://rx2u-rest.appspot.com/rest/uberService/endOrder/"+orderNum)
        return res.text
