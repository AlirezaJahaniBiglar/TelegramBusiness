from flask import Flask, request
import requests
import logging
from logging.handlers import RotatingFileHandler
import mysql.connector
import json
from config import *

app = Flask(__name__)


db = mysql.connector.connect(**DB_CONFIG)
cursor = db.cursor(dictionary=True)

def send_custom_emoji_message(channel_id, message, custom_emoji=None, connect_id=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": channel_id,
        "text": message
    }

    if connect_id:
        payload["business_connection_id"] = connect_id
    
    if custom_emoji:
        payload["entities"] = custom_emoji

    response = requests.post(url, json=payload)
    error_log.info(response.text + str(payload))
    
    return response.json()

def save_new_connection(connection_id, user_id):
    query = "SELECT id FROM users WHERE id = %s"
    cursor.execute(query, (connection_id,))
    result = cursor.fetchone()

    if not result:
        query = "INSERT INTO users (id, user_id, message) VALUES (%s, %s, %s);"
        cursor.execute(query, (connection_id, user_id, BOT_MESSAGE + "\n\nNo message has been set"))
        db.commit()

def get_chat_by_connection_id(connection_id, chat_id):
    query = "SELECT admin_reply, message, entities FROM conversations WHERE user_id = %s and conn_id = %s"
    cursor.execute(query, (chat_id, connection_id))
    return cursor.fetchone()

def update_admin_reply_status(connection_id, chat_id, status):
    query = "UPDATE conversations SET admin_reply = %s WHERE user_id = %s and conn_id = %s"
    cursor.execute(query, (status, chat_id, connection_id))
    db.commit()

def save_new_chat(connection_id, user_id):
    select_query = """
        SELECT u.message, u.entities
        FROM users u
        WHERE u.id = %s;
    """
    
    cursor.execute(select_query, (connection_id,))
    result = cursor.fetchone()
    
    if result:
        message = result["message"] 
        entities = result["entities"]
        
        insert_query = """
            INSERT INTO conversations (user_id, conn_id, message, entities)
            VALUES (%s, %s, %s, %s);
        """
        
        cursor.execute(insert_query, (user_id, connection_id, message, entities))
        
        db.commit()

        return message, entities


def send_message(chat_id, text, reply_markup=None):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': json.dumps(reply_markup) if reply_markup else None,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    return response
        

def change_step(user_id, step):
    insert_query = """
    UPDATE users
    SET `step` = %s
    WHERE user_id = %s;
    """
    
    cursor.execute(insert_query, (step, user_id, ))
    
    db.commit()


@app.route("/webhook", methods=["POST"])
def main():
    data = request.get_json()

    if 'business_connection' in data:
        connection_info = data['business_connection']
        connection_id = connection_info['id']
        user_id = connection_info['user']['id']
        chat_id = connection_info['user_chat_id']

        save_new_connection(connection_id, user_id)

        return "Connection saved", 200

    if 'business_message' in data:
        message = data['business_message']
        connection_id = message['business_connection_id']
        user_id = message["from"]["id"]
        chat_id = message["chat"]["id"]

        if user_id != chat_id:
            update_admin_reply_status(connection_id, chat_id, True)
            return "OK"

        chat_data = get_chat_by_connection_id(connection_id, chat_id)

        if chat_data:
            admin_reply_status = chat_data["admin_reply"]
            admin_message = chat_data["message"]
            entities = chat_data["entities"]

            if admin_reply_status:
                send_custom_emoji_message(chat_id, admin_message, entities, connection_id)

                update_admin_reply_status(connection_id, chat_id, False)

        else:
            data_ = save_new_chat(connection_id, chat_id)
            send_custom_emoji_message(
                chat_id, 
                data_[0],
                data_[1],
                connection_id
            )

    if 'message' in data and 'text' in data["message"]:
        message = data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        user = message['from']
        user_id = user['id']
        first_name = user.get('first_name', '')

        if text.lower() == "/start":
            query = "SELECT id FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                change_step(user_id, "before_change")

                keyboard = {
                    "keyboard": [[{"text": "Change Text 💬"}]],
                    "resize_keyboard": True,
                    "one_time_keyboard": False
                }

                send_message(chat_id, f"Hello <a href=\"tg://user?id={user_id}\">{first_name}</a> ✋\n\nYou have an active session with id:\n<pre>{result['id']}</pre>", keyboard)

            else:
                send_message(chat_id, f"Hello <a href=\"tg://user?id={user_id}\">{first_name}</a> ✋\n\nPlease connect @IOTAnswerBot to your business account")

        else:
            select_query = """
                SELECT `step`
                FROM users
                WHERE user_id = %s;
            """
            
            cursor.execute(select_query, (user_id,))
            result = cursor.fetchone()
            if not result:
                return "ok"
            
            step = result["step"]

            if text == "Change Text 💬" and step == "before_change":
                keyboard = {
                    "keyboard": [[{"text": "Cancel ❌"}]],
                    "resize_keyboard": True,
                    "one_time_keyboard": False
                }
                
                send_message(chat_id, f"Please send me the new text. Feel free to use anything you like, including <b>Premium Emojis</b> 🌟✨", keyboard)
                change_step(user_id, "change")

            elif step == "change":
                if text == "Cancel ❌":
                    change_step(user_id, "home")
                    send_message(chat_id, "🏠", {"remove_keyboard": True})
                    return "ok"
            
                insert_query = """
                UPDATE users
                SET message = %s, entities = %s
                WHERE user_id = %s;
                """
                enti = []
                enti2 = message.get("entities", [])
                for entity in enti2:
                    updated_entity = entity.copy()
                    updated_entity['offset'] += 24
                    enti.append(updated_entity)
        
                entities = BOT_MESSAGE_ENTITIES + enti
                the_message = BOT_MESSAGE + "\n\n" + text
                cursor.execute(insert_query, (the_message, json.dumps(entities), user_id))
        
                query = "SELECT id FROM users WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                conn = result["id"]
        
                insert_query2 = """
                UPDATE conversations
                SET message = %s, entities = %s
                WHERE conn_id = %s and edit = TRUE;
                """
                cursor.execute(insert_query2, (the_message, json.dumps(entities), conn))
        
                db.commit()
        
                change_step(user_id, "home")
                send_message(chat_id, "Done! ✅", {"remove_keyboard": True})


    return "OK"

error_log = logging.getLogger('error_logger')
error_log.setLevel(logging.DEBUG)

error_handler = RotatingFileHandler(error_log_file, maxBytes=10485760, backupCount=5, encoding='utf-8')
error_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
error_handler.setFormatter(error_formatter)
error_log.addHandler(error_handler)
