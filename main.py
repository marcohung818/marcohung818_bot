import os
import telebot
from telebot import types
import time, threading, schedule

API_KEY = "5019621877:AAE3yt2xi2gRcJQQEamHMYi173hD1MLIWjE"
bot = telebot.TeleBot(API_KEY)
users = []
question_list = []
prepared_question = [
    "ellie", "ellie 中意咩野色", "marco", "第一次見面係邊日", "ellie", "第一日錫錫既日子"
]
bonus_list = ["xbk_icon.png", "Nutanix-AHV.png", "c.png"]
public_counter = {
    "game_time": 90,
    "count_down": 3,
    "playercount": 0,
    "questioncount": 0,
    "ans0": None,
    "ans1": None,
    "anscount": 0,
    "gpslock": 0,
    "question_time": 2
}


class Question:
    def __init__(self, qprovider, qcontent):
        self.qprovider = qprovider
        self.qcontent = qcontent


'''Time'''


#Reduce minutes
def count_down():
    global public_counter
    public_counter['game_time'] -= 1
    if (public_counter['game_time'] %
            public_counter['count_down'] == 0):  #15Minus announce once
        boardcast_announcement('遊戲時間餘下: ' + str(public_counter['game_time']) +
                               "分鐘")
        send_question()
    if (public_counter['game_time'] % 90 == 0):
        boardcast_announcement("遊戲完結，希望你已經搵到你中意既人啦")
        schedule.clear("timer")
        return 0


#Start timer
def start_timer():
    schedule.every(1).minutes.do(count_down).tag("timer")
    boardcast_announcement('遊戲時間餘下: ' + str(public_counter['game_time']) +
                           "分鐘")
    send_question()


#Show remain time
@bot.message_handler(commands=['showtime'])
def show_time(message):
    global public_counter
    bot.send_message(message.chat.id, public_counter['game_time'])


#Reduce question minutes
def question_count_down():
    global public_counter
    print("question_count_down")
    public_counter['question_time'] -= 1
    if (public_counter['question_time'] == 1):
        boardcast_announcement("問題只餘下1分鐘，請盡快回答")
    if (public_counter['question_time'] == 0):
        public_counter['ans0'] = "drop"
        public_counter['ans1'] = "drop"
        drop_reply()
        


#Start timer
def question_timer_start(message):
    print("debug")

    return


'''Time'''
'''Gameplay'''


@bot.message_handler(commands=['start'])
def greet(message):
    help(message)
    bot.send_message(message.chat.id, "如果明白遊戲玩法既話，請輸入/find，你的伴侶正在等你。")


@bot.message_handler(commands=['find'])
def find(message):
    global public_counter
    if (public_counter['playercount'] < 2):
        msg = bot.send_message(message.chat.id, "請輸入你的名字")
        bot.register_next_step_handler(msg, matching)
    else:
        bot.send_message(message.chat.id, "遊戲已經開始咗!!!")


def matching(message):
    global public_counter
    try:
        name = message.text
        if name in ['ellie', 'marco', 'Ellie', 'Marco', 'E', 'm']:
            chat_id = message.chat.id
            print(chat_id)
            if chat_id not in users:
                users.append(chat_id)
                public_counter['playercount'] += 1
                if (len(users) == 2):
                    bot.send_message(users[0], "It's a match!")
                    bot.send_message(users[1], "It's a match!")
                    start_timer()
                else:
                    bot.send_message(message.chat.id, "Waiting for a match...")
            else:
                bot.send_message(message.chat.id, "你已經排緊隊啦 唔好咁心急啦")
        else:
            bot.send_message(message.chat.id,
                             "依個遊戲只可以比好中意Marco既人玩(Hints: E) \n請重新輸入/find")
            return
    except Exception as e:
        bot.send_message(message.chat.id, "something error")


def send_question():
    global public_counter
    schedule.every(1).minutes.do(question_count_down).tag("qtimer")
    questionPos = public_counter['questioncount']
    if (questionPos + 1 >= len(prepared_question)):
        boardcast_announcement("沒有問題了")
        return
    else:
        question = "問題: " + question_list[questionPos].qcontent
        public_counter['questioncount'] += 1
        boardcast(question)


def boardcast_announcement(message_text):
    bot.send_message(users[0], text=message_text)
    bot.send_message(users[1], text=message_text)


#Send message to both sides
def boardcast(message_text):
    bot.send_message(users[0], text=message_text)
    msg_1 = bot.send_message(users[0], text="請回答")
    bot.register_next_step_handler(msg_1, store_reply)
    bot.send_message(users[1], text=message_text)
    msg_2 = bot.send_message(users[1], text="請回答")
    bot.register_next_step_handler(msg_2, store_reply)


def store_reply(message):
    global public_counter
    if (message.chat.id == users[0]):
        public_counter['ans0'] = message.text
        public_counter['anscount'] += 1
    else:
        public_counter['ans1'] = message.text
        public_counter['anscount'] += 1
    if (public_counter['ans0'] in ["Yes", "No"]
            and public_counter['ans1'] in ["Yes", "No"]):
        release_response()
    else:
        release_reply()


def release_reply():
    global public_counter
    if public_counter['anscount'] == 2 and public_counter[
            'ans0'] is not None and public_counter['ans1'] is not None:
        bot.send_message(users[0], "你Match的回答是\n" + public_counter['ans1'])
        bot.send_message(users[1], "你Match的回答是\n" + public_counter['ans0'])
        schedule.clear("qtimer")
        public_counter['anscount'] = 0  #Reset value
        public_counter['ans0'] = None
        public_counter['ans1'] = None
        store_response()

def drop_reply():
  global public_counter
  if public_counter['ans0'] == "drop" or public_counter['ans1'] == "drop":
    schedule.clear("qtimer")
    public_counter['anscount'] = 0  #Reset value
    public_counter['ans0'] = None
    public_counter['ans1'] = None
    bot.clear_step_handler_by_chat_id(chat_id=users[0])
    bot.clear_step_handler_by_chat_id(chat_id=users[1])
    public_counter['questioncount'] += 1
    boardcast_announcement("問題已drop 請等下個問題")

def store_response():
    global public_counter
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                         resize_keyboard=True)
    item_yes = types.KeyboardButton('Yes')
    item_no = types.KeyboardButton('No')
    keyboard.row(item_yes, item_no)
    response1 = bot.send_message(users[0],
                                 '認同大家答案是相同嗎?',
                                 reply_markup=keyboard)
    response2 = bot.send_message(users[1],
                                 '認同大家答案是相同嗎?',
                                 reply_markup=keyboard)
    bot.register_next_step_handler(response1, store_reply)
    bot.register_next_step_handler(response2, store_reply)


def release_response():
    global public_counter
    if (public_counter['ans0'] == 'Yes' and public_counter['ans1'] == 'Yes'):
        boardcast_announcement("大家都認同對方的答案")
        release_bonus()
    else:
        boardcast_announcement("雙方未有統一同意")
    public_counter['anscount'] = 0  #Reset value
    public_counter['ans0'] = None
    public_counter['ans1'] = None


def release_bonus():
    release_pic()
    release_location()


def release_pic():
    global public_counter
    global bonus_list
    print(public_counter['questioncount'] - 1)
    boardcast_announcement("這是獎勵的圖片")
    photo1 = open(bonus_list[public_counter['questioncount'] - 1], 'rb')
    photo2 = open(bonus_list[public_counter['questioncount'] - 1], 'rb')
    bot.send_photo(users[0], photo1)
    bot.send_photo(users[1], photo2)


def release_location():
    global public_counter
    location_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                  resize_keyboard=True)
    item_location = types.KeyboardButton(text='分享位置', request_location=True)
    location_keyboard.row(item_location)
    bot.send_message(users[0], "請分享位置", reply_markup=location_keyboard)
    bot.send_message(users[1], "請分享位置", reply_markup=location_keyboard)
    public_counter["gpslock"] = 2


'''Gameplay'''
'''Question'''
#Add prepared question into
for i in range(len(prepared_question)):
    if (i % 2 == 0):
        question = Question(prepared_question[i], prepared_question[i + 1])
        question_list.append(question)


@bot.message_handler(commands=['listq'])
def listq(message):
    if not question_list:
        bot.send_message(message.chat.id, "現時沒有任何問題")
    else:
        for question in question_list:
            bot.send_message(
                message.chat.id,
                "問題提供者: " + question.qprovider + "\n問題: " + question.qcontent)
    return


'''Question'''
'''Help'''
bot.set_my_commands(commands=[
    telebot.types.BotCommand("find", "開始尋找你的對象"),
    telebot.types.BotCommand("showtime", "顯示餘下時間"),
    telebot.types.BotCommand("help", "幫助"),
    telebot.types.BotCommand("admin", "遊戲管理員功能"),
], )
cmd = bot.get_my_commands(scope=None, language_code=None)
print([c.to_json() for c in cmd])


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(
        message.chat.id,
        "******遊戲方法******\n玩家可以用此bot尋找對象，而match到之後系統每10分鐘會問你們一個問題，你們需要答自己心目中的答案，然後大家去睇是否接受對方的答案，如果雙方都接受的話，就會得到一個獎勵，同埋可以分享自己的位置，如果雙方都分享自己的位置先會得到對方GPS既位置。除咗答問題時間外，大家都睇唔到對方同bot之間的對話。遊玩時間有1.5小時，如果有限時間內搵到對方的話就會有bonus，但搵唔到既話都冇懲罰既\n\n^^^^^^注意事項^^^^^^\n1. 交通安全好重要，記住睇路！遊戲依啲野好少事。\n2. 當問題發出後，請在5分鐘內完成問題，否則個問題係會drop既\n3. 請不要在答問題期間用任何Function 如/find, /showtime等等\n基於此交友App是測試階段，求求你跟番個instruction去玩，如果9玩有好大機會會中bug的...如果有任何問題，請致電我們的客服熱線90947184,thx"
    )
    return


@bot.message_handler(commands=['skipq'])
def skipq(message):
    global public_counter
    value = message.text.split()[1:]
    if value:
        public_counter['questioncount'] += int(value[0])
        public_counter['game_time'] -= (int(value[0]) *
                                        public_counter['count_down'])
        bot.send_message(
            message.chat.id,
            "Questioncount = " + str(public_counter['questioncount']) +
            "\n下一條問題是第" + str(public_counter['questioncount'] + 1) + "條")
    else:
        bot.send_message(message.chat.id, "請輸入 /shipq [value]")
    return


@bot.message_handler(commands=['admin'])
def admin(message):
    bot.send_message(message.chat.id, "Please input admin password")
    bot.register_next_step_handler(message, list_admin_menu)
    return


def list_admin_menu(message):
    if (message.text == "ellie&marco"):
        bot.send_message(
            message.chat.id,
            "/listq - List out all the questions\n/skipq - Skip the amount of question"
        )
    else:
        bot.send_message(message.chat.id, "密碼錯誤")
    return


'''Help'''


@bot.message_handler(content_types='location')
def sendlocation(message):
    global public_counter
    del_keyboard_markup = types.ReplyKeyboardRemove(selective=True)
    if (public_counter["gpslock"] > 0):
        if (message.chat.id == users[0]):
            bot.send_message(users[1], "對方現在的位置在")
            bot.send_location(users[1], message.location.latitude,
                              message.location.longitude)
            bot.send_message(users[0],
                             "你的位置已發送",
                             reply_markup=del_keyboard_markup)
        else:
            bot.send_message(users[0], "對方現在的位置在")
            bot.send_location(users[0], message.location.latitude,
                              message.location.longitude)
            bot.send_message(users[1],
                             "你的位置已發送",
                             reply_markup=del_keyboard_markup)
        public_counter["gpslock"] -= 1
        print(public_counter["gpslock"])

@bot.message_handler(commands=['askloc'])
def request_location(message):
    global public_counter
    location_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                  resize_keyboard=True)
    item_location = types.KeyboardButton(text='分享位置', request_location=True)
    location_keyboard.row(item_location)
    if(message.chat.id == users[0]):
      bot.send_message(users[1], "Admin要求你分享位置", reply_markup=location_keyboard)
    else:
      bot.send_message(users[0], "Admin要求你分享位置", reply_markup=location_keyboard)
    public_counter["gpslock"] = 1

@bot.message_handler(commands=['reset'])
def reset(message):
  global public_counter
  global users
  public_counter["game_time"] = 90
  public_counter["count_down"] = 3
  public_counter["playercount"] = 0
  public_counter["questioncount"] = 0
  public_counter["ans0"] = None
  public_counter["ans1"] = None
  public_counter["anscount"] = 0
  public_counter["gpslock"] = 0
  public_counter["question_time"] = 2
  schedule.clear("timer")
  boardcast_announcement("遊戲重置了 如果要重新進入遊戲的話，請再次輸入/find")
  users.clear()

if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling,
                     name='bot_infinity_polling',
                     daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)
