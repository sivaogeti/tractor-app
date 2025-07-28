# data.py
import json
from datetime import datetime

DB_FILE = "db.json"

def load_data():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"logs": []}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_log(entry):
    data = load_data()
    data["logs"].append(entry)
    save_data(data)

def get_user_logs(username):
    data = load_data()
    return [log for log in data["logs"] if log["employee"] == username]

def get_all_logs():
    return load_data()["logs"]
