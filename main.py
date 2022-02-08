import os
import telebot
from telebot import types

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)
user_dict = {}
question_list = []
qProvider = 'Provider'
qContent = 'Content'

class Question:
  def __init__(self, qprovider, qcontent):
    self.qprovider = qprovider
    self.qcontent = qcontent

class User:
  def __init__(self, name):
    self.name = name

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

@bot.message_handler(commands=['listq'])
def listq(message):
  if not question_list:
    bot.send_message(message.chat.id, "The question list is empty")
  else:
    for question in question_list:
      bot.send_message(message.chat.id, "QProvider: " + question.qprovider + " Question: " + question.qcontent)    

bot.polling()