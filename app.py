# coding: utf8
from flask import Flask,request,json,jsonify
import base64
from chatbot.Response import response
from helper.Replier import Replier
from helper.KakaoDB import KakaoDB
from helper.SharedDict import get_shared_state
import time
import sys

from dataclass import RequestData # Import the dataclass

app = Flask(__name__)
db = KakaoDB()
g = get_shared_state()

@app.route('/db', methods=['POST'])
def py_exec_db():
    r = app.response_class(
        response="200",
        status=200,
        mimetype='text/plain; charset="utf-8"'
    )

    try:
        request_json_data = request.get_json()

        if request_json_data is None:
            return jsonify({"error": "No JSON data received"}), 400

        required_keys = ["room", "msg", "sender", "json"]
        if not all(key in request_json_data for key in required_keys):
            missing_keys = [key for key in required_keys if key not in request_json_data]
            return jsonify({"error": f"Missing required keys: {missing_keys}"}), 400

        try:
            request_data = RequestData(request_json_data)
            
        except Exception as e:
            return jsonify({"error": "Failed to parse request data into dataclass", "details": str(e)}), 400


        replier = Replier(RequestData.chat_id) # pass dict for now, you might need to adjust Replier to use dataclass

        @r.call_on_close
        def on_close():
            response(
                request_data.room,
                request_data.msg,
                request_data.sender,
                replier,
                request_data.json, # Now this should be parsed json object (ChatLog dataclass)
                db,
                g
            )
            sys.stdout.flush()
        return r

    except Exception as e:
        print(f"Error processing JSON request: {e}")
        return jsonify({"error": "Failed to process JSON data", "details": str(e)}), 400


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)