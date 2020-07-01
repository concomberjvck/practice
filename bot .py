from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
import string
import telebot
import random
from telebot import types

bot = telebot.TeleBot('1104348391:AAGR30CyVjtZz6RSyCV1-RQb-RS46ZMWm5A');

START = False

def read_text1(filename):
    res = []
    signes = ['.', '!', '?', ' ']
    with open(filename, mode='rt', encoding='utf-8') as file:
        text = file.read()
        sents = text.split('\n')[0:]
        for i in sents:
            ''.strip().join(i.rsplit('.', maxsplit=1))
            ''.strip().join(i.rsplit(';', maxsplit=1))
            list = [i]
            for v in signes:
                if list == [i]:
                    list = i.split(v, maxsplit=1)
                else: break
            if len(list) != 2 or list[0] == '' or list[1] == '' or list[1] == ' ' or list[1] == ') ':
                continue
            res.append([list[0], list[1].split(';')])
        return res

def read_text2(filename):
    res = []
    with open(filename, mode='rt', encoding='utf-8') as file:
        pattern = ''
        text = file.read()
        sents = text.strip().split('\n')[1:]
        for i in sents:
            i = i.split(',')
            if i[0] == '' or i[1] == '':
                continue
            if i[0] == pattern:
                res[len(res)-1][1].append(i[1])
            else: res.append([i[0], [i[1]]])
            pattern = i[0]
        return res

def to_str(list):
    string = ''
    for i in list:
        string += i + ' '
    return string.strip()

def get_key(words, value):
    for key, val in words.items():
        if val == value:
            return key

def aleut_translator(db, sequence):
    ans = {}
    if sequence in db.keys():
        return {sequence : db[sequence]}
    else:
        words = sequence.split(' ')
        length = len(words)
        for i in range(length):
            for j in reversed(range(i, length + 1)):
                skey = to_str(words[i:j])
                if skey in db.keys():
                    ans.update({ skey : db[skey]})
        return ans

def eng_translator(db, sequence):
    ans = {}
    items = db.items()
    for k, v in items:
        if sequence in v:
            #key = get_key(db, ans, value)
            if sequence not in ans.keys():
                ans.update({sequence : [k]})
            else:
                ans[sequence].append(k)
    if ans != {}:
        return ans
    words = sequence.split(' ')
    length = len(words)
    for i in range(length):
        for j in reversed(range(i, length + 1)):
            skey = to_str(words[i:j])
            for k, v in items:
                if skey in v:
                    #key = get_key(db, ans, value)
                    if skey not in ans.keys():
                        ans.update({skey : [k]})
                    elif k not in ans.values():
                        ans[skey].append(k)
    return ans

def clean(words, words2):
    for i in words.keys():
        if words2.get(i) != None:
            words2.pop(i)

def answer(sequence, ans):
    if len(ans.keys()) == 0:
        return "Извини, но перевод этого слова неизвестен..."
    answer = ""
    if sequence in ans.keys():
        for i in ans[sequence]:
            answer += i + "\r\n"
        return answer
    else:
        answer += "Может, ты имел ввиду следующее?\r\n"
        for i in ans.keys():
            answer += i + " имеет перевод:\r\n"
            for j in ans[i]:
                answer +=  j + "\r\n"
        return answer

def data():
	path1 = './ddd.txt'
	path2 = './dataset.csv'

	data1 = read_text1(path1)
	data2 = read_text2(path2)
	data = data1 + data2

	db = {val[0].strip().lower() : [s.strip().lower().translate(str.maketrans('', '', string.punctuation)) for s in val[1] if s != ' ' and s!= ''] for val in data}
	return db

@bot.message_handler(commands=['start'])
def start(message):
	global START
	bot.send_message(message.from_user.id, text="Привет, я помогу тебе в изучении алеутского языка!\n\nВводи слова на английском или алеутском языке :)")
	START = True
	keyboard = types.InlineKeyboardMarkup()
	key_yes = types.InlineKeyboardButton(text="Интересный факт", callback_data="facts")
	keyboard.add(key_yes)
	question = "Нажав на кнопку ниже, ты узнаешь интересные факты об этом языке :)"
	bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
	global START

	if not START:
	    bot.send_message(message.from_user.id, text="Чтобы начать введи /start")
	else: 
		mes = message.text.lower()
		db = data()
		ans = eng_translator(db, mes)
		if ans != {}:
			bot.send_message(message.from_user.id, text=answer(mes, ans))
		else:
			bot.send_message(message.from_user.id, text=answer(mes, aleut_translator(db, mes)))

		keyboard = types.InlineKeyboardMarkup()
		key_yes = types.InlineKeyboardButton(text="Интересный факт", callback_data="facts")
		keyboard.add(key_yes)
		question = "Введи следующее слово"
		bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
	if call.data == "facts": 
		data = list(open('facts.txt'))
		r = random.choice(data)
		bot.send_message(call.message.chat.id, text=r)
		keyboard = types.InlineKeyboardMarkup()
		key_yes = types.InlineKeyboardButton(text="Интересный факт", callback_data="facts")
		keyboard.add(key_yes)
		question = "Введи следующее слово"
		bot.send_message(call.message.chat.id, text=question, reply_markup=keyboard)

bot.polling(none_stop=True, interval=0)