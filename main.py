from settings import *

from flask import render_template, redirect, url_for
from utils.api_response import *
from authorization import is_logged, login_required

import api.mobile_network.http
import api.mobile_network.websocket
import api.authorization
import api.admin
import events

@app.route("/")
def mainPage():
    logged, payload = is_logged("cookies")
    return render_template("index.html", **payload, logged = logged)

# @app.route("/login")
# def loginPage():
#     logged, payload = is_logged("cookies")
#     if logged:
#         return redirect(url_for("mainPage"))
#     return render_template("login.html")

if __name__ == '__main__':
    app.run(
        host = settings['host'], 
        port = settings['port'],
        debug = settings['debug']
    )