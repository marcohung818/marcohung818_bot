import os
import telebot
from telebot import types
import time, threading, schedule

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)
users = []
freeid = None
question_list = []
prepared_question =["abc","bbb","777","888"]
qProvider = 'Provider'
qContent = 'Content'
counter_down_minutes = 5
game_time = None
startcount = 0
findcount = 0

class Question:
  def __init__(self, qprovider, qcontent):
    self.qprovider = qprovider
    self.qcontent = qcontent

class User:
  def __init__(self, name):
    self.name = name

'''Time'''
#Reduce minutes
def count_down():
  global game_time
  game_time -= 1
  if (game_time % 1 == 0):
    bot.send_message(users[0], text='Time Remain: ' + str(game_time) + "mins")
    bot.send_message(users[1], text='Time Remain: ' + str(game_time) + "mins")

#Set the timer
@bot.message_handler(commands=['set']) 
def set_timer(message):
    global game_time
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        game_time = int(args[1])
    else:
        bot.reply_to(message, 'Usage: /set <minutes>')         

def start_timer():
  schedule.every(1).minutes.do(count_down).tag("timer")
  bot.send_message(users[0], text='Time Remain: ' + str(game_time) + "mins")
  bot.send_message(users[1], text='Time Remain: ' + str(game_time) + "mins")
  
#Cancel the counting
@bot.message_handler(commands=['unset']) 
def unset_timer(message):
    schedule.clear("timer")

#Show remain time
@bot.message_handler(commands=['showt']) 
def show_time(message):
  global game_time
  if game_time != None:
    bot.send_message(message.chat.id, game_time)
  else:
    bot.send_message(message.chat.id, "Time not set yet")

'''Time'''

'''Gameplay'''
@bot.message_handler(commands=['start'])
def greet(message):
  global startcount
  if(startcount < 2):
    bot.send_message(message.chat.id, "如果想玩尋找迷路的Marco遊戲\n請輸入 /find")
    startcount += 1
  else:
    bot.send_message(message.chat.id, "Game was started already!!!")

@bot.message_handler(commands=['find'])
def find(message):
  global findcount
  if(findcount < 2):
    msg = bot.send_message(message.chat.id, "Please input your name")
    findcount += 1
    bot.register_next_step_handler(msg, matching)
  else:
    bot.send_message(message.chat.id, "Game was started already!")

def matching(message):
  global findcount
  global freeid
  try:
    name = message.text
    if name in ['ellie', 'marco', 'Ellie', 'Marco']:
      chat_id = message.chat.id
      print(chat_id)
      if chat_id not in users:
        users.append(chat_id)
        if(len(users) == 2):
          bot.send_message(users[0], "Founded!")
          bot.send_message(users[1], "Founded!")
          start_timer()
        else:  
          bot.send_message(message.chat.id, "Finding...")
      else:
        bot.send_message(message.chat.id, "你已經排緊隊啦")
        findcount -= 1
    else:
      bot.send_message(message.chat.id, "依個遊戲只可以比好中意Marco既人玩(Hints: E)")
      findcount -= 1
      return
  except Exception as e:
    bot.send_message(message.chat.id, "something error")
'''Gameplay'''

'''Question'''
#Add prepared question into 
for i in range(len(prepared_question)):
  if(i % 2 == 0):
    question = Question(prepared_question[i], prepared_question[i+1])
    question_list.append(question)
    
@bot.message_handler(commands=['listq'])
def listq(message):
  if not question_list:
    bot.send_message(message.chat.id, "The question list is empty")
  else:
    for question in question_list:
      bot.send_message(message.chat.id, "QProvider: " + question.qprovider + " Question: " + question.qcontent)   
'''Question'''

'''Help'''
bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "Start the game"),
        telebot.types.BotCommand("find", "Find Marco!!!!!"),
        telebot.types.BotCommand("showt", "Show remain time"),
        telebot.types.BotCommand("help", "List all the command"),
    ],
)
cmd = bot.get_my_commands(scope=None, language_code=None)
print([c.to_json() for c in cmd])

@bot.message_handler(commands=['help'])
def help(message):
  bot.send_message(message.chat.id, "Please input admin password")
  bot.register_next_step_handler(message, list_full_menu)

def list_full_menu(message):
  if(message.text == "123"):
    bot.send_message(message.chat.id, "/listq - List out all the questions\n/start - Start the game\n/set - Time setting\n/showt - Show remain time\n/unset - Pause the timer")
  else:
    bot.send_message(message.chat.id, "Wrong password")
'''Help'''

if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)

#bot.polling()
