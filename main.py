import mysql.connector
import requests
from config import TOKEN, DB_CONFIG, WEBHOOK_URL, BOT_MESSAGE_ENTITIES


def init_db():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        entities_json = str(BOT_MESSAGE_ENTITIES).replace("'", '"')

        create_users_table = f"""
        CREATE TABLE IF NOT EXISTS users (
            id varchar(255) PRIMARY KEY,
            user_id varchar(100) NOT NULL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            entities JSON DEFAULT '{entities_json}',
            `step` VARCHAR(20)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        cursor.execute(create_users_table)

        create_conversations_table = f"""
        CREATE TABLE IF NOT EXISTS conversations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id varchar(100) NOT NULL,
            conn_id VARCHAR(255) NOT NULL,
            admin_reply BOOLEAN DEFAULT TRUE,
            edit BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
            entities JSON DEFAULT '{entities_json}'
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        cursor.execute(create_conversations_table)

        db.commit()
        print("Database initialized successfully!")
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        db.close()


def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    response = requests.post(url, json={"url": WEBHOOK_URL})

    if response.status_code == 200:
        print("Webhook set successfully!")
    else:
        print(f"Failed to set webhook: {response.text}")


if __name__ == "__main__":
    init_db()
    set_webhook()
