from const import *
import re, copy, json
import telebot
import yahoo_fin.stock_info as si

import datetime as dt

bot = telebot.TeleBot(API_KEY)

def add_user(time, id, msg):
    with open(JSON_PATH, 'r+') as f:
        data = json.load(f)

        time_str = dt.datetime.strftime(time, "%d/%m/%y %H:%M:%S")
        if time in data.keys():
            data[time_str][id] = msg
        else:
            data[time_str] = {id : msg}

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

def remove_user(id, user_time=False):
    with open(JSON_PATH, 'r+') as f:
        data = json.load(f)

        message = []
        for time, users in copy.deepcopy(list(data.items())):
            for user, msg in users.items():
                if int(user) == id:
                    if user_time == False or time == dt.datetime.strftime(user_time, "%d/%m/%y %H:%M:%S"):
                        data[time].pop(user)

                        if data[time] == {}:
                            data.pop(time)
                        message.append(msg)

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

        return message

def valid_time(time):
    p = re.compile("^([01]?[0-9]|2[0-3]):[0-5][0-9]$")

    return bool(re.search(p, time))

def create_request(message):
    request = message.text.split(" ", 2)
    if len(request) == 3 and request[0] == '/create' and valid_time(request[1]) and request[2][0] == '"' and request[2][-1] == '"':
        return True
    return False

#/start 0:00 "YOUR MESSAGE"
@bot.message_handler(func=create_request)
def create(message):
    request = message.text.split(" ", 2)[1:]
    time = request[0].split(":")
    time = dt.datetime.combine(dt.date.today(), dt.time(int(time[0]), int(time[1])))

    add_user(time, message.chat.id, request[1][1:-1])

    return_msg = f"{message.from_user.first_name} {message.from_user.last_name} to be notified \"{request[1][1:-1]}\" at {time.strftime('%I:%M%p')}."

    print(return_msg)
    bot.send_message(message.chat.id, return_msg)

def stop_request(message):
    request = message.text.split()
    if len(request) == 2 and request[0] == '/stop' and valid_time(request[1]):
        return True
    return False

#/stop 0:00
@bot.message_handler(func=stop_request)
def stop(message):
    request = message.text.split()
    time = request[1].split(":")
    time = dt.datetime.combine(dt.date.today(), dt.time(int(time[0]), int(time[1])))

    msg = remove_user(message.chat.id, time)

    return_msg = ""
    if msg:
        return_msg = f"Alert stopped, {message.from_user.first_name} {message.from_user.last_name}.\n\n"+msg[0]
    else:
        return_msg = f"{message.from_user.first_name} {message.from_user.last_name} you don't have any alerts started."

    print("stop:", return_msg)
    bot.send_message(message.chat.id, return_msg)

@bot.message_handler(commands=['stopall'])
def stopall(message):
    msg = remove_user(message.chat.id)

    return_msg = ""
    if msg:
        return_msg = f"All alerts stopped, {message.from_user.first_name} {message.from_user.last_name}.\n\n"
        for i, m in enumerate(msg):
            return_msg += f"{i+1}. {m}\n"
    else:
        return_msg = f"{message.from_user.first_name} {message.from_user.last_name} you don't have any alerts started."

    print("stopall:", return_msg)
    bot.send_message(message.chat.id, return_msg)

@bot.message_handler(commands=['tas'])
def get_stocks(message):
    stocks = si.get_day_most_active()[0:STOCK_LENGTH].reindex(columns = COLUMNS)
    stocks.rename(columns = {'Price (Intraday)':'Price'}, inplace = True)

    print(stocks.to_string(index=False))

    bot.send_message(message.chat.id, "<pre>"+stocks.to_string(index=False)+'</pre>', "HTML")

bot.polling()