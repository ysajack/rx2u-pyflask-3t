from flask import Flask, render_template, url_for, request, redirect, session, flash, make_response
from models import User, Pharmacy, Uber
import sys
import json
import os
import requests

app = Flask(__name__)
#app.secret_key = 'verytoplevelsecret'

app.secret_key = os.urandom(24)
#port = int(os.environ.get('PORT', 5000))

@app.route('/')
def home():
    resp = make_response(render_template('home.html'))
    resp.delete_cookie('UserPhoneCookie')
    resp.delete_cookie('UserNameCookie')
    return resp

@app.route('/requestpickup')
def requestpickup(userinfo=None):
    phone = request.cookies.get('UserPhoneCookie')
    username = request.cookies.get('UserNameCookie')
    if phone:userinfo = User.populateUserInfo(phone)
    return render_template('requestpickup.html', userinfo=userinfo, username=username)

@app.route('/requestpickup/placeorder', methods=['GET','POST'])
def placeorder(userinfo=None):
    username = request.cookies.get('UserNameCookie')
    #Expecting this placeorder page is sent from the previous page requestpickup via post method in html
    if request.method == 'POST':
        userinfo = {"first": request.form['first'],
                        "last": request.form['last'],
                        "phone": request.form['phone'],
                        "dob": request.form['dob'],
                        "address": request.form['address'],
                        "pharmacy": request.form['pharmacy'],
                        "rx": request.form['rx']}
        #Store userinfo object in session (for convenience) to pass in the User.placeOrder() method in the next page (orderinfo page)
        session["userinfo"]=userinfo
        return render_template('placeorder.html', userinfo=userinfo, username=username)

@app.route('/requestpickup/placeorder/orderinfo', methods=['GET','POST'])
def orderinfo(orderNum=None, fullName=None, phone=None):
    username = request.cookies.get('UserNameCookie')
    #Expecting this page landing via a post method from the previous page (placeorder page)
    if request.method == 'POST':
        #Pass in userinfo object stored in session from the previous page (placeorder page) which sends it here
        orderNum=User.placeOrder(session["userinfo"])
        first = session["userinfo"]["first"]
        last = session["userinfo"]["last"]
        phone = session["userinfo"]["phone"]
        fullName = first + ' ' + last
        if orderNum:
            return render_template('orderinfo.html', orderNum=orderNum, fullName=fullName, phone=phone,username=username)
        else:
            flash('Errors placing order! Pls place order again!')
            return redirect(url_for('requestpickup'))

@app.route('/orderstatus')
def orderstatus(orderinfo=None):
    username = request.cookies.get('UserNameCookie')
    orderinfo = User.checkOrderStatus()
    return render_template('orderstatus.html', orderinfo=orderinfo, username=username)

@app.route('/lookuporder', methods=['GET','POST'])
def lookuporder(orderinfo=None):
    username = request.cookies.get('UserNameCookie')
    if request.method == 'POST':
        orderinfo = User.lookupOrder(request.form['orderNumber'].lower())
        if orderinfo==[None]:
            flash('Order number not found! Pls review and reenter!')
            return redirect(url_for('orderstatus'))
        else:
            return render_template('orderstatus.html', orderinfo=orderinfo, username=username)

@app.route('/pharmacy', methods=['POST']) #Strictly allowing only POST to avoid refresh issues via path /pharmacy
def pharmacydashboard(orderinfo=None):
    if request.method == 'POST': #Expected a post method, when perform an action
        if request.form['method']=='Fill':
            Pharmacy.fillOrder(request.form['orderNum'].lower())
            orderinfo = Pharmacy.populateOrders()
            return redirect(url_for('pharmacyrefresh')) #Redirecting to pharmacyrefresh to avoid post refresh resending data issues
            # return render_template('pharmacy.html', orderinfo=orderinfo)
        elif request.form['method']=='Complete':
            Pharmacy.completeOrder(request.form['orderNum'].lower())
            orderinfo = Pharmacy.populateOrders()
            return redirect(url_for('pharmacyrefresh')) #Redirecting to pharmacyrefresh to avoid post refresh resending data issues

@app.route('/pharmacy') #Automatically allowing only GET method for the first time landing via /pharmacy
def pharmacyrefresh(): #For refresh and for the first time landing via path /pharmacy
    orderinfo = Pharmacy.populateOrders()
    return render_template('pharmacy.html', orderinfo=orderinfo)

@app.route('/uber', methods=['POST']) #Strictly allowing only POST to avoid refresh issues via path /uber
def uberdashboard(orderinfo=None):
    if request.method == 'POST': #Expected a post method, when perform an action
        if request.form['method']=='Accept':
            Uber.acceptOrder(request.form['orderNum'].lower())
            orderinfo = Uber.populateOrders()
            return redirect(url_for('uberrefresh')) #Redirecting to uberrefresh to avoid post refresh resending data issues
        elif request.form['method']=='Start':
            Uber.startOrder(request.form['orderNum'].lower())
            orderinfo = Uber.populateOrders()
            return redirect(url_for('uberrefresh')) #Redirecting to uberrefresh to avoid post refresh resending data issues
        elif request.form['method']=='End':
            Uber.endOrder(request.form['orderNum'].lower())
            orderinfo = Uber.populateOrders()
            return redirect(url_for('uberrefresh')) #Redirecting to uberrefresh to avoid post refresh resending data issues

@app.route('/uber') #Automatically allowing only GET method for the first time landing via /uber
def uberrefresh(): #For refresh and for the first time landing via path /pharmacy
    orderinfo = Uber.populateOrders()
    return render_template('uber.html', orderinfo=orderinfo)

@app.route('/user', methods=['POST']) #Strictly allowing only POST to avoid refresh issues via path /user
def user(orderinfo=None):
    username = request.cookies.get('UserNameCookie')
    phone = request.cookies.get('UserPhoneCookie')
    if request.method == 'POST':
        if request.form['method']=='Receive':
            res = User.receiveOrder(request.form['orderNum'].lower())
            orderinfo = User.populateUserOrders(request.form['phone'])
            if(res !="Errors performing SQL functions"):
                return redirect(url_for('userrefresh')) #Redirecting to uberrefresh to avoid post refresh resending data issues
                # return render_template('user.html', orderinfo=orderinfo, username=username)
            else:
                flash(res+'. Pls try again!')
                return redirect(url_for('userrefresh')) #Redirecting to uberrefresh to avoid post refresh resending data issues

@app.route('/user') #Automatically allowing only GET method for the first time landing via /user
def userrefresh(): #For refresh and for the first time landing via path /pharmacy
    username = request.cookies.get('UserNameCookie')
    phone = request.cookies.get('UserPhoneCookie')
    if phone: #Expected this page is populated for a specific user; else, sends error in flash
        orderinfo = User.populateUserOrders(phone)
        return render_template('user.html', orderinfo=orderinfo,username=username)
    else:
        flash('Erros loging in. Pls log in again!')
        return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    #Expecting the register.html page sends username and password for validation via a post
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 2:
            flash('Your username must be at least one character.')
        elif len(password) < 5:
            flash('Your password must be at least 5 characters.')
        elif User.find(username)=="0":
            flash('A user with that username already exists.')
        else:
            session['credentials'] = {"username": username, "password": password}
            return redirect(url_for('registration')) #If no errors, will redirect to the registration page
    return render_template('register.html') #If errors, the register.html page will populate the flash message

@app.route('/register/registration', methods=['GET','POST'])
def registration():
    if request.method == 'POST':
        userinfo = {"username": session["credentials"]["username"],
            "password": session["credentials"]["password"],
            "first": request.form['first'],
            "last": request.form['last'],
            "phone": request.form['phone'],
            "dob": request.form['dob'],
            "rx": request.form['rx'],
            "address": request.form['address'],
            "pharmacy": request.form['pharmacy']
            }
        res = User.register(userinfo)
        app.logger.info(res)
        if(res =="Success"):
            flash('You are now registered. Please login!')
            return redirect(url_for('login'))
        else:
            flash('Errors. Please re-register!')
            return redirect(url_for('login'))
    return render_template('registration.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        res = User.verifyPassword(username, password)
        if res != "1":
            phone = res
            response = redirect(url_for('user'))
            response.set_cookie('UserNameCookie', username)
            response.set_cookie('UserPhoneCookie', phone)
            return response
        else:
            flash('Invalid username/password! Pls review and reenter!')
        return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/about')
def about():
    username = request.cookies.get('UserNameCookie')
    return render_template('about.html', username=username)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # app.run(debug=True)
    #app.run(host='0.0.0.0', port=port)
