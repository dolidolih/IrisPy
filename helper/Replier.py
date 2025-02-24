import json
import base64
import time
import threading
from PIL import Image
import io
import requests

class Replier:
    def __init__(self, request_data):
        self.config = get_config()
        self.bot_url = self.config["bot_endpoint"] + "/reply"
        self.json = request_data["json"]
        self.room = str(self.json["chat_id"])
        self.queue = []
        self.last_sent_time = time.time()

    def send_http_request(self, type, data, room):
        """Sends an HTTP POST request to the bot's reply endpoint."""
        payload = {
            "type": type,
            "room": room,
            "data": data
        }
        headers = {'Content-type': 'application/json'}

        try:
            response = requests.post(self.bot_url, json=payload, headers=headers)
            response.raise_for_status()
            print(f"HTTP request successful for room {room}, type {type}")
        except requests.exceptions.RequestException as e:
            print(f"HTTP request failed for room {room}, type {type}: {e}")


    def reply(self, msg, room=None):
        if room == None:
            room = self.room
        self.__queue_message("text",str(msg),str(room))


    def reply_image_from_file(self, room, filepath):
        img = Image.open(filepath)
        self.reply_image_from_image(room,img)

    def reply_image_from_image(self, room, img):
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        png_bytes = buffered.getvalue()
        base64_bytes = base64.b64encode(png_bytes)
        base64_string = base64_bytes.decode('utf-8')
        if room == None:
            room = self.room
        self.__queue_message("image",base64_string,str(room))

    def __queue_message(self, type, data, room):
        self.queue.append((type, data, room))
        if len(self.queue) == 1:
            self.__send_message()

    def __send_message(self):
        next_message = self.queue[0]
        current_time = time.time()
        if current_time-self.last_sent_time >= 0.1:
            msg_type, msg_data, msg_room = next_message
            self.send_http_request(msg_type, msg_data, msg_room)
            self.queue.pop(0)
            self.last_sent_time = current_time
        if len(self.queue) > 0:
            timer = threading.Timer(0.1, self.__send_message)
            timer.start()

def get_config():
    with open('config.json','r') as fo:
        config = json.loads(fo.read())
    return config