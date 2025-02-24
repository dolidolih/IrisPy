import requests
import json
import time

def send_query(query, bind=None, endpoint="/query", bot_url=None):
    """
    Sends an HTTP request to the bot service with the given query.

    Args:
        query (str): The SQL query to execute.
        bind (list, optional): Parameters to bind to the query. Defaults to None.
        endpoint (str, optional): The API endpoint to hit. Defaults to "/query".
        bot_url (str, optional): The base URL of the bot service.
            If None, it tries to get it from config.json.

    Returns:
        list or None: Parsed JSON data from the response if successful, None otherwise.
    """
    if bot_url is None:
        config = get_config()
        bot_url = config["bot_endpoint"]

    url = bot_url + endpoint
    headers = {'Content-Type': 'application/json'}
    payload = {"query": query}
    if bind is not None:
        payload["bind"] = bind
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        response_json = response.json()
        if response_json.get("success"):
            data = response_json.get("data")
            if data == "[]" or not data:
                return None
            return data
        else:
            print(f"HTTP request to bot service failed: {response_json.get('error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during HTTP request: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON response from bot service.")
        return None


class KakaoDB():
    def __init__(self):
        self.config = get_config()
        self.BOT_ID = self.config["bot_id"]
        self.BOT_NAME = self.config["bot_name"]
        self.BOT_URL = self.config["bot_endpoint"]

    def get_column_info(self, table):
        query = f"SELECT * FROM {table} LIMIT 1"
        data = send_query(query, bot_url=self.BOT_URL) # Use the outside function
        if data is None:
            return []
        try:
            if not data:
                return []
            first_row = data[0]
            if isinstance(first_row, dict):
                cols = list(first_row.keys())
            elif isinstance(first_row, list):
                cols = first_row
            else:
                return []
            return cols
        except Exception as e:
            print(f"Error processing get_column_info data: {e}")
            return []

    def get_table_info(self):
        query = "SELECT name FROM sqlite_schema WHERE type='table';"
        data = send_query(query, bot_url=self.BOT_URL) # Use the outside function
        if data is None:
            return []
        try:
            if not data:
                return []
            tables = [table[0] for table in data]
            return tables
        except Exception as e:
            print(f"Error processing get_table_info data: {e}")
            return []

    def get_name_of_user_id(self, user_id):
        if self.check_new_db():
            query = f"""
                    WITH info AS (
                        SELECT ? AS user_id
                    )
                    SELECT
                        COALESCE(open_chat_member.nickname, friends.name) AS name,
                        COALESCE(open_chat_member.enc, friends.enc) AS enc
                    FROM info
                    LEFT JOIN db2.open_chat_member
                        ON open_chat_member.user_id = info.user_id
                    LEFT JOIN db2.friends
                        ON friends.id = info.user_id;
                """
        else:
            query = f"SELECT name, enc FROM db2.friends WHERE id = ?"
        data = send_query(query, bind=[user_id], bot_url=self.BOT_URL) # Use the outside function
        if data is None:
            return None
        try:
            for row in data:
                row_name = row[0]
                enc = row[1]
                dec_row_name = self.decrypt(enc, row_name)
                return dec_row_name
        except Exception as e:
            print(f"Error processing get_name_of_user_id data: {e}")
            return None

    def get_user_info(self, chat_id, user_id):
        if user_id == self.BOT_ID:
            sender = self.BOT_NAME
        else:
            sender = self.get_name_of_user_id(user_id)
        query = f"SELECT name FROM db2.open_link WHERE id = (SELECT link_id FROM chat_rooms WHERE id = ?)"
        data = send_query(query, bind=[chat_id], bot_url=self.BOT_URL) # Use the outside function
        if data is None:
            room = sender
        else:
            try:
                if data:
                    room = data[0][0]
                else:
                    room = sender
            except Exception as e:
                print(f"Error processing get_user_info data: {e}")
                room = sender
        return (room, sender)

    def get_row_from_log_id(self, log_id):
        query = f"SELECT * FROM chat_logs WHERE id = ?"
        data = send_query(query, bind=[log_id], bot_url=self.BOT_URL) # Use the outside function
        if data is None:
            return None
        try:
            if data:
                return data[0]
            else:
                return None
        except Exception as e:
            print(f"Error processing get_row_from_log_id data: {e}")
            return None

    def clean_chat_logs(self, days):
        try:
            days = float(days)
            now = time.time()
            days_before_now = round(now - days * 24 * 60 * 60)
            query = f"delete from chat_logs where created_at < ?"
            send_query(query, bind=[days_before_now], bot_url=self.BOT_URL) # Use the outside function
            res = f"{days:g}일 이상 지난 데이터가 삭제되었습니다."
        except Exception:
            res = "요청이 잘못되었거나 에러가 발생하였습니다."
        return res

    def log_to_dict(self, log_id):
        query = f"select * from chat_logs where id = ?"
        data = send_query(query, bind=[log_id], bot_url=self.BOT_URL) # Use the outside function
        if data is None:
            return {}
        try:
            if not data:
                return {}
            rows = data
            descriptions_query = f"PRAGMA table_info(chat_logs)"
            descriptions_data = send_query(descriptions_query, bot_url=self.BOT_URL) # Use the outside function
            if descriptions_data is None:
                return {}
            if not descriptions_data:
                return {}
            descriptions_list = descriptions_data
            descriptions = [d[1] for d in descriptions_list]
            row = rows[0]
            return {descriptions[i]: row[i] for i in range(len(descriptions))}
        except Exception as e:
            print(f"Error processing log_to_dict data: {e}")
            return {}

    def check_new_db(self):
        query = "SELECT name FROM db2.sqlite_master WHERE type='table' AND name='open_chat_member'"
        data = send_query(query, bot_url=self.BOT_URL) # Use the outside function
        if data is None:
            return False
        try:
            return bool(data)
        except Exception as e:
            print(f"Error processing check_new_db data: {e}")
            return False

    def decrypt(self, encType, b64_ciphertext, user_id=None):
        decrypt_endpoint = "/decrypt"
        url = self.BOT_URL + decrypt_endpoint
        headers = {'Content-Type': 'application/json'}
        if user_id is None:
            user_id = self.BOT_ID
        payload = {
            "enc": encType,
            "b64_ciphertext": b64_ciphertext,
            "user_id": user_id
        }
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            response_json = response.json()
            if response_json.get("plain_text"):
                return response_json.get("plain_text")
            else:
                print(f"Decrypt request failed: {response_json}") # print full response for debugging
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error during decrypt HTTP request: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON response from decrypt service.")
            return None


def get_config():
    with open('config.json','r') as fo:
        config = json.loads(fo.read())
    return config