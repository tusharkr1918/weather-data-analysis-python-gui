import os
import json
import sqlite3
import requests

# !TODO - Deleting the existing API keys


DATA_DIR = os.path.join(os.path.expanduser("~"), "WeatherDataAnalysis")
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE = os.path.join(DATA_DIR, "weather.db")
JSON_FILE = os.path.join(DATA_DIR, "last_logged.json")


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


def verify_api_key(api_key):
    try:
        response = requests.get(f'http://api.weatherapi.com/v1/current.json?key={api_key}&q=Ranchi')
        return (response.status_code == 200, None)
    except requests.exceptions.ConnectionError:
        return (False, 'Please check your internet connection.')

def save_api(user_wgt, api_wgt, pass_wgt):
    user_name, api_key, password = user_wgt.get(), api_wgt.get(), pass_wgt.get()
    if user_name and api_key and password:
        if user_exists(user_name)[0]:
            return f"Username [{user_name}] already exists.\n Please choose another."
        else:
            status, connection_msg = verify_api_key(api_key)

            if status:
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (user_name, api_key, password) VALUES (?, ?, ?)',
                           (user_name, api_key, password))
                conn.commit()
                conn.close()
                return f"Username [{user_name}]  saved successfully."
            else:
                return "Invalid API key, please try again!" if connection_msg == None else connection_msg
    else:
        return "Please fill in all fields."


def fetch_data(user_wgt, pass_wgt, context):
    user_name = user_wgt.get()
    password = pass_wgt.get()
    result = user_exists(user_name)
    if result[0] and result[1][1] == password:
        context.current_user = {"user_name": result[1][0], "api_key": result[1][2]}
        save_to_json(context.current_user)
        return [f"Welcome back {user_name}!",user_name]
    else:
        return [f"No data found for the provided \n username [{user_name}] and password.", None]


def save_to_json(user_data):
    with open(JSON_FILE, "w") as json_file:
        json.dump(user_data, json_file, indent=2)


def load_from_json():
    try:
        with open(JSON_FILE, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        pass
