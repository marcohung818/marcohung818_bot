import os
import telebot
from telebot import types
import time, threading, schedule

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)
user_dict = {}
question_list = []
prepared_question =["abc","bbb","777","888"]
qProvider = 'Provider'
qContent = 'Content'
counter_down_minutes = 5
game_time = 1

class Question:
  def __init__(self, qprovider, qcontent):
    self.qprovider = qprovider
    self.qcontent = qcontent

class User:
  def __init__(self, name):
    self.name = name

for i in range(len(prepared_question)):
  if(i % 2 == 0):
    question = Question(prepared_question[i], prepared_question[i+1])
    question_list.append(question)
'''Time Related'''

def beep(chat_id) -> None:
  global game_time
  game_time -= counter_down_minutes
  bot.send_message(chat_id, text='Time Remain: ' + str(game_time))

@bot.message_handler(commands=['set']) #Set the timer
def set_timer(message):
    global game_time
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        game_time = int(args[1])
        schedule.every(counter_down_minutes).minutes.do(beep, message.chat.id).tag(message.chat.id)
    else:
        bot.reply_to(message, 'Usage: /set <minutes>')         

@bot.message_handler(commands=['unset']) #Cancel the counting
def unset_timer(message):
    schedule.clear(message.chat.id)

@bot.message_handler(commands=['show_time']) #Show remain time
def show_time(message):
  global game_time
  bot.send_message(message.chat.id, game_time)
  
'''Time Related'''
@bot.message_handler(commands=['start'])
def greet(message):
  msg = bot.send_message(message.chat.id, "Please input your name")
  bot.register_next_step_handler(msg, name_processing_step)

@bot.message_handler(commands=['listq'])
def listq(message):
  if not question_list:
    bot.send_message(message.chat.id, "The question list is empty")
  else:
    for question in question_list:
      bot.send_message(message.chat.id, "QProvider: " + question.qprovider + " Question: " + question.qcontent)   






#Game play part
def name_processing_step(message):
  try:
    name = message.text
    if name in ['ellie', 'marco', 'Ellie', 'Marco']:
      chat_id = message.chat.id
      print(chat_id)
      user = User(name)
      user_dict[chat_id] = user
    else:
      bot.send_message(message.chat.id, "This game is not for you")
      return
  except Exception as e:
    bot.send_message(message.chat.id, "something error")
    
 
if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)
#bot.polling()
'''
@bot.message_handler(commands=['setq'])
def setq(message):
  msg = bot.send_message(message.chat.id, "Input the question provider and the question with a spacebar, Input \"end\" when finish input")
  bot.register_next_step_handler(msg, question_provider_step)

def question_provider_step(message):
  try:
    args = message.text.split()
    print(args)
    if len(args) == 1 or args[0] == 'end':
      bot.send_message(message.chat.id, "The questions input was done!")
      return
    else:
      question = Question(args[0], args[1])
      question_list.append(question)
      print(question_list)
      setq(message)
  except Exception as e:
    bot.send_message(message.chat.id, "something error")
'''
