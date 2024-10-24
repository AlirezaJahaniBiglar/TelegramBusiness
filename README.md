# Telegram Business Manager

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/flask-WSGI%20ready-green)
![MySQL](https://img.shields.io/badge/mysql-Connector-red)

## Overview

**IOTAnswerBot** is a customizable Telegram bot designed to interact with business accounts, manage user connections, and provide dynamic message handling using custom emojis. The bot operates via a webhook setup and utilizes a MySQL database to store user sessions, messages, and conversations.

A demo version of the bot is available at [@IOTAnswerBot](https://t.me/iotanswerbot).

This repository includes:
- `app.py`: The primary bot logic handling incoming webhook requests, message processing, and database interactions.
- `config.py`: Configuration file for database, bot token, and message templates.
- `main.py`: Handles the database setup and webhook configuration for the bot.

## Features
- Dynamic message handling using Telegram’s custom emojis.
- Webhook integration with Flask and WSGI.
- Persistent session management via MySQL.
- Modular configuration for easy adjustments.
  
## Prerequisites

Ensure the following dependencies are installed:
- Python 3.9+
- MySQL Server
- Flask
- `mysql-connector-python`

### Python Dependencies
Install the required Python packages via pip:
```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `Flask`
- `requests`
- `mysql-connector-python`

## Setup

### 1. Configuration

1. Clone the repository:
   ```bash
   git clone https://github.com/AlirezaJahaniBiglar/TelegramBusiness.git
   cd TelegramBusiness
   ```

2. Edit the `config.py` file:
   - **TOKEN**: Add your bot's Telegram API token.
   - **DB_CONFIG**: Update with your MySQL credentials.
   - **Error Logging**: Set the error log file path if needed.

   ```python
   TOKEN = "your-telegram-bot-token"
   DB_CONFIG = {
       'user': 'your_db_user',
       'password': 'your_db_password',
       'host': 'localhost',
       'database': 'your_database_name'
   }
   ```

3. Ensure that your MySQL server is running.

### 2. WSGI Deployment

To deploy this bot using WSGI, follow these steps:

1. Ensure your server has a WSGI-compatible server such as **uWSGI** or **Gunicorn** installed.

2. Set up your WSGI entry point. Here’s an example using Gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:8000 app:app
   ```

3. You’ll need to configure your web server (e.g., **Nginx** or **Apache**) to forward requests to your WSGI application.

#### Example `app.py` for WSGI
```python
from flask import Flask
from app import app

# The Flask app object from `main.py` is imported and used in WSGI.
```

4. Configure your environment variables:
   ```bash
   export FLASK_ENV=production
   export FLASK_APP=app.py
   ```

5. Make sure to restart your WSGI server to apply changes.

### 3. Final Setup

1. Open `config.py` and set the `WEBHOOK_URL` to the correct URL for your server where Telegram will send updates. For example:
   ```python
   WEBHOOK_URL = "https://yourdomain.com/webhook"
   ```

2. After updating the webhook URL, run `main.py` to set up the database and configure the webhook:
   ```bash
   python main.py
   ```

This will configure the webhook and set up your database. Make sure to use a WSGI server for production environments.

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
