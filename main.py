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

#Add prepared question into 
for i in range(len(prepared_question)):
  if(i % 2 == 0):
    question = Question(prepared_question[i], prepared_question[i+1])
    question_list.append(question)



bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "Start the game"),
        telebot.types.BotCommand("showt", "Show remain time"),
        telebot.types.BotCommand("help", "List all the command"),
    ],
)
cmd = bot.get_my_commands(scope=None, language_code=None)
print([c.to_json() for c in cmd])

'''Time'''
#Reduce minutes
def count_down(chat_id):
  global game_time
  game_time -= 1
  if (game_time % 5 == 0):
    bot.send_message(chat_id, text='Time Remain: ' + str(game_time))

#Set the timer
@bot.message_handler(commands=['set']) 
def set_timer(message):
    global game_time
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        game_time = int(args[1])
        schedule.every(1).minutes.do(count_down, message.chat.id).tag(message.chat.id)
        bot.reply_to(message, "Time remain: " + str(game_time) + "mins")
    else:
        bot.reply_to(message, 'Usage: /set <minutes>')         


#Cancel the counting
@bot.message_handler(commands=['unset']) 
def unset_timer(message):
    schedule.clear(message.chat.id)

#Show remain time
@bot.message_handler(commands=['showt']) 
def show_time(message):
  global game_time
  if game_time != 1:
    bot.send_message(message.chat.id, game_time)
  else:
    bot.send_message(message.chat.id, "Time not set yet")

'''Time'''

'''Gameplay'''
@bot.message_handler(commands=['start'])
def greet(message):
  msg = bot.send_message(message.chat.id, "Please input your name")
  bot.register_next_step_handler(msg, name_processing_step)

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



'''Question'''
@bot.message_handler(commands=['listq'])
def listq(message):
  if not question_list:
    bot.send_message(message.chat.id, "The question list is empty")
  else:
    for question in question_list:
      bot.send_message(message.chat.id, "QProvider: " + question.qprovider + " Question: " + question.qcontent)   
'''Question'''

'''Help'''
@bot.message_handler(commands=['help'])
def help(message):
  bot.send_message(message.chat.id, "Please input admin password")
  bot.register_next_step_handler(message, list_full_menu)

def list_full_menu(message):
  if(message.text == "123"):
    bot.send_message(message.chat.id, "/listq - List out all the questions\n/start - Start the game\n/set - Time setting\n/showt - Show remain time\n/unset - Pause the timer")
  else:
    bot.send_message(message.chat.id, "Wrong password")



if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)

#bot.polling()
