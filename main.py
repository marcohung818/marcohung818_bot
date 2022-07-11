import os
import telebot
from telebot import types
import time, threading, schedule

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)
users = []
freeid = None
question_list = []
prepared_question =["provider1","bbb","provider2","888"]
bonus_list = ["a.png", "b.png", "c.png"]
qProvider = 'Provider'
qContent = 'Content'
counter_down_minutes = 15
game_time = 180
startcount = 0
findcount = 0
questioncount = 0
bonuscount = 0
reply_times = 0
player0ans = None
player1ans = None
ans_count = 0

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
  if (game_time % counter_down_minutes == 0): #15Minus announce once
    bot.send_message(users[0], text='Time Remain: ' + str(game_time) + "mins")
    bot.send_message(users[1], text='Time Remain: ' + str(game_time) + "mins")
    send_question()
  if (game_time % 180 == 0):
    return 0

#Start timer
def start_timer():
  schedule.every(1).minutes.do(count_down).tag("timer")
  bot.send_message(users[0], text='Time Remain: ' + str(game_time) + "mins")
  bot.send_message(users[1], text='Time Remain: ' + str(game_time) + "mins")
  send_example_question()

#Show remain time
@bot.message_handler(commands=['showt']) 
def show_time(message):
  global game_time
  bot.send_message(message.chat.id, game_time)
'''Time'''

'''Gameplay'''
@bot.message_handler(commands=['start'])
def greet(message):
  global startcount
  if(startcount < 2):
    bot.send_message(message.chat.id, "如果想玩Marco交友app既\n請輸入 /find")
    bot.send_message(message.chat.id, "求求你跟番個遊戲規矩玩，依個交友app如果亂答會好易中bug的...如果需要睇遊戲玩法既\n請輸入 /help")
    startcount += 1
  else:
    bot.send_message(message.chat.id, "Game was started already!!!")

@bot.message_handler(commands=['find'])
def find(message):
  global findcount
  if(findcount < 2):
    msg = bot.send_message(message.chat.id, "Please input your name")
    bot.register_next_step_handler(msg, matching)
  else:
    bot.send_message(message.chat.id, "Game started already!")

def matching(message):
  global findcount
  global freeid
  try:
    name = message.text
    if name in ['ellie', 'marco', 'Ellie', 'Marco', 'E', 'm']:
      chat_id = message.chat.id
      print(chat_id)
      if chat_id not in users:
        users.append(chat_id)
        if(len(users) == 2):
          bot.send_message(users[0], "It's a match!")
          bot.send_message(users[1], "It's a match!")
          start_timer()
        else:  
          bot.send_message(message.chat.id, "Matching...")
          findcount += 1
      else:
        bot.send_message(message.chat.id, "你已經排緊隊啦 唔好咁心急啦")
    else:
      bot.send_message(message.chat.id, "依個遊戲只可以比好中意Marco既人玩(Hints: E)")
      return
  except Exception as e:
    bot.send_message(message.chat.id, "something error")

def send_question():
  global questioncount
  question = "問題by: " + question_list[questioncount].qprovider + " 問題: " + question_list[questioncount].qcontent
  boardcast(question)
  questioncount += 1
def send_example_question():
  question = "這一條是example，但成功都會有獎勵的\n問題by: Example" + " 問題: " + "孔繁昕女朋友係邊個"
  boardcast(question)
#Send message to both sides
def boardcast(message_text):
  bot.send_message(users[0], text=message_text)
  msg_1 = bot.send_message(users[0], text="Please input your response")
  bot.register_next_step_handler(msg_1, store_reply)
  bot.send_message(users[1], text=message_text)
  msg_2 = bot.send_message(users[1], text="Please input your response")
  bot.register_next_step_handler(msg_2, store_reply)

def store_reply(message):
  global player0ans
  global player1ans
  global ans_count
  if(message.chat.id == users[0]):
    player0ans = message.text
    ans_count += 1
  else:
    player1ans = message.text
    ans_count += 1
  if(player0ans in ["yes", "Yes", "YES", "No", "no", "NO"] and player1ans in ["yes", "Yes", "YES", "No", "no", "NO"]):
    release_ans()
  else:
    release_reply()
  
def release_reply():
  global ans_count
  global player0ans
  global player1ans

  if ans_count == 2 and player0ans is not None and player1ans is not None:
    bot.send_message(users[0], "你Match的Answer是\n" + player1ans)
    bot.send_message(users[1], "你Match的Answer是\n" + player0ans)
    ans_count = 0 #Reset value
    player0ans = None
    player1ans = None
    boardcast("同意答案一樣的請回答yes，否則回答no")

def release_ans():
  global ans_count
  global player0ans
  global player1ans
  if ans_count == 2 and player0ans is not None and player1ans is not None:
    bot.send_message(users[0], "你Match的回答是\n" + player1ans)
    bot.send_message(users[1], "你Match的回答是\n" + player0ans)
    if(player0ans in ["yes", "Yes", "YES"] and player1ans in ["yes", "Yes", "YES"]):
      bot.send_message(users[0], "Both answer Yes")
      bot.send_message(users[1], "Both answer Yes")
      release_bonus()
    else:
      bot.send_message(users[0], "未能達到雙方同意")
      bot.send_message(users[1], "未能達到雙方同意")

def release_bonus():
  release_pic()
  #release_location
  
def release_pic():
  global bonuscount
  print(bonuscount)
  #photo = open(bonus_list[bonuscount], 'rb')
  #bot.send_photo(users[0], photo)
  #bot.send_photo(users[1], photo)
  bonuscount += 1
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
      bot.send_message(message.chat.id, "問題by: " + question.qprovider + " 問題: " + question.qcontent)   
'''Question'''

'''Help'''
bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("find", "Find a match!!!"),
        telebot.types.BotCommand("showtime", "Show remain time"),
        telebot.types.BotCommand("help", "Show the game play method"),
        telebot.types.BotCommand("admin", "List all the admin command"),
    ],
)
cmd = bot.get_my_commands(scope=None, language_code=None)
print([c.to_json() for c in cmd])

@bot.message_handler(commands=['help'])
def help(message):
  bot.send_message(message.chat.id, "玩家要先輸入/find尋求自己潛在對象，而match到之後系統就會問你們一樣的問題，你們需要答自己心目中既答案，然後大家去睇是否接受對方的答案，如果兩邊都接受的話，就會得到對方的GPS位置和一個獎勵。如果接受遊戲的話，請現在輸入/find，你的伴侶正在等你。\n基於此交友App是測試階段，求求你跟番個instruction去玩，如果9玩有好大機會會中bug的...如果有任何問題，請致電我們的客服熱線90947184,thx")

@bot.message_handler(commands=['skipq'])
def skipq(message):
  global questioncount
  global bonuscount
  questioncount += 1
  bonuscount += 1
  bot.send_message(message.chat.id, "The Questioncount equal to " + str(questioncount))
  bot.send_message(message.chat.id, "The Bonuscount equal to " + str(bonuscount))

@bot.message_handler(commands=['admin'])
def admin(message):
  bot.send_message(message.chat.id, "Please input admin password")
  bot.register_next_step_handler(message, list_admin_menu)

def list_admin_menu(message):
  if(message.text == "ellie&marco"):
    bot.send_message(message.chat.id, "/listq - List out all the questions\n/getloc - Get opportent location\n/skipq - Skip the amount of question")
  else:
    bot.send_message(message.chat.id, "Wrong password")
'''Help'''

@bot.message_handler(commands=['pic'])
def pic(message):
  photo = open('Nutanix-AHV.png', 'rb')
  bot.send_photo(message.chat.id, photo)

if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)
