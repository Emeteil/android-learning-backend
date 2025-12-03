from authorization import login_required
from utils.api_response import *
from flask import request
from settings import *

@app.route("/api/admin/ping", methods=['GET'])
def ping_server():
    return apiResponse({"message": "Pong!"})

@app.route("/api/admin/loged_ping", methods=['GET'])
@login_required("cookies")
def loged_ping_server(payload):
    return apiResponse({"message": "Pong!"})

@app.route("/error_page", methods=['GET'])
def error_page_cheack():
    args = request.args
    status_code: int = int(args.get("code", 500))
    raise ApiError(
        code = status_code
    )