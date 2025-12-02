from typing import Dict, Set
from flask_sock import Sock
from flask import request
import json
import time

from utils.db.mobile_network_data import save_mobile_network_data
from authorization import is_logged
from settings import *

sock = Sock(app)
active_connections: Dict[str, Set] = {
    "authenticated": set(),
    "anonymous": set()
}
user_connection_map: Dict[str, Dict] = {}

@sock.route("/api/mobile-network/ws")
def mobile_network_websocket(ws):
    token = request.args.get("token")
    is_authenticated = False
    user_id = None
    nickname = None
    
    if token:
        logged, payload = is_logged("args")
        if logged:
            is_authenticated = True
            user_id = payload.get("user_id")
            nickname = payload.get("nickname")
    
    connection_type = "authenticated" if is_authenticated else "anonymous"
    connection_id = f"{user_id or 'anonymous'}_{int(time.time())}"
    
    active_connections[connection_type].add(ws)
    
    if is_authenticated and user_id:
        if user_id not in user_connection_map:
            user_connection_map[user_id] = {}
        user_connection_map[user_id][connection_id] = ws
    
    try:
        while True:
            message = ws.receive()
            
            if not message:
                continue
            
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue
            
            if is_authenticated and user_id:
                mobile_network_data_list = data.get("mobile_network_data_list")
                location_data = data.get("location_data")
                
                if mobile_network_data_list or location_data:
                    save_mobile_network_data(
                        user_id,
                        mobile_network_data_list,
                        location_data
                    )
                    
                    broadcast_data = {
                        nickname: {
                            "mobile_network_data_list": mobile_network_data_list,
                            "location_data": location_data
                        }
                    }
                    
                    broadcast_to_all(broadcast_data)
                    
                    ws.send(json.dumps({
                        "status": "success",
                        "message": "Data saved"
                    }))
            else:
                ws.send(json.dumps({
                    "status": "error",
                    "message": "Receive/Read mode only"
                }))
    
    except Exception as e: print(e)
    finally:
        active_connections[connection_type].discard(ws)
        
        if is_authenticated and user_id and user_id in user_connection_map:
            if connection_id in user_connection_map[user_id]:
                del user_connection_map[user_id][connection_id]
            if not user_connection_map[user_id]:
                del user_connection_map[user_id]

def broadcast_to_all(data: Dict):
    for conn in active_connections["anonymous"]:
        try:
            conn.send(json.dumps(data))
        except:
            continue