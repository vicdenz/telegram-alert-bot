from const import *

import datetime as dt
from time import sleep

import os, copy, json
import telebot

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

bot = telebot.TeleBot(API_KEY)

path = os.getcwd()
sending = False
users = {}

def load_users():
    global users, sending
    data = json.load(open(JSON_PATH))

    existing_times = []
    for time_str, user in data.items():
        time = dt.datetime.strptime(time_str, "%d/%m/%y %H:%M:%S")
        if not time in users.keys():
            users[time] = {}
            for id, msg in user.items():
                users[time][int(id)] = msg
        existing_times.append(time)
    
    for key in copy.copy(list(users.keys())):
        if key not in existing_times:
            users.pop(key)
    users = dict(sorted(users.items()))

    if len(users) > 0:
        sending = True
    else:
        sending = False
    print("Updated users")

class UserChanged(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.replace(path+"/", "") == JSON_PATH:
            load_users()

event_handler = UserChanged()
observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()

running = True
load_users()
try:
    while running:
        if sending:
            now = dt.datetime.now()
            for time, user in users.items():
                if now >= time:
                    if now.second == 0:
                        if (now - time).seconds % 60 == 0:
                            for id, msg in user.items():
                                print("Message sent to", id, " :", msg)
                                bot.send_message(id, "Alert sent: <b>\""+msg+"\"</b>", parse_mode="HTML")
                        sleep(1)
                else:
                    break
        sleep(0.1)
except KeyboardInterrupt:
    observer.stop()
observer.join()