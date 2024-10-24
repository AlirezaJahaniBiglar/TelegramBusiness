# config.py

# Telegram Bot Token
TOKEN = "<Bot-Token>"

# MySQL Database Configuration
DB_CONFIG = {
    'user': 'your-database-username',
    'password': 'your-database-password',
    'host': 'localhost',
    'database': 'your-database-name'
}

# Default log file
error_log_file = 'error.log'

# Default bot message and entities
BOT_MESSAGE = "From @IOTAnswerBot 👻:"
BOT_MESSAGE_ENTITIES = [
    {"offset": 5, "length": 13, "type": "mention"},
    {"offset": 19, "length": 2, "type": "custom_emoji", "custom_emoji_id": "4916016466035213359"}
]

# Webhook URL for the bot
WEBHOOK_URL = "https://yourdomain.com/webhook"
