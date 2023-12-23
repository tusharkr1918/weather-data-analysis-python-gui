import json
import sqlite3

# !TODO - Deleting the existing API keys

DATABASE = "weather.db"
JSON_FILE = "last_logged.json"


def create_weather_api_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_name TEXT UNIQUE,
            api_key TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()


def user_exists(user_name):
    conn = sqlite3.connect(DATABASE)
    result = conn.execute('SELECT user_name, password, api_key FROM users WHERE user_name = ?', (user_name,)).fetchone()
    conn.close()
    return [result is not None, result]


def save_api(user_wgt, api_wgt, pass_wgt):
    user_name, api_key, password = user_wgt.get(), api_wgt.get(), pass_wgt.get()
    if user_name and api_key and password:
        if user_exists(user_name)[0]:
            return "Username already exists.\n Please choose another."
        else:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (user_name, api_key, password) VALUES (?, ?, ?)',
                           (user_name, api_key, password))
            conn.commit()
            conn.close()
            return "Data saved successfully."
    else:
        return "Please fill in all fields."


def fetch_data(user_wgt, pass_wgt, context):
    user_name = user_wgt.get()
    password = pass_wgt.get()
    result = user_exists(user_name)
    if result[0] and result[1][1] == password:
        context.current_user = {"user_name": result[1][0], "api_key": result[1][2]}
        save_to_json(context.current_user)
        return "Successfully logged"
    else:
        return "No data found for the provided \n user_name and password."


def save_to_json(user_data):
    with open(JSON_FILE, "w") as json_file:
        json.dump(user_data, json_file, indent=2)


def load_from_json(context):
    try:
        with open(JSON_FILE, "r") as json_file:
            context.current_user = json.load(json_file)
    except FileNotFoundError:
        pass
