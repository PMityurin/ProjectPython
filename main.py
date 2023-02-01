import telebot
from telebot import types
import sqlite3 as sql
from datetime import datetime

bot = telebot.TeleBot("5800628749:AAGNtnVSePdHho3R7dmryKKHyeXduPeHLc4")

@bot.message_handler(commands=['start'])
def start(message):
    mess = f"Привет, <b>{message.from_user.first_name} <u>{message.from_user.last_name}</u>!</b> " \
           f"\nОтправь сумму, cколько ты сейчас потратил."
    conn = sql.connect(f'{message.from_user.id}.sqlite')
    cur = conn.cursor()
    cur.execute(f""" CREATE TABLE IF NOT EXISTS  user{message.from_user.id} (
        id INTEGER PRIMARY KEY ,
        cost FLOAT,
        date INTEGER,
        category VARCHAR(50)
    ) """)
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, mess, parse_mode='html')
    with open("chatID.txt", "w") as txt:
        txt.write(str(message.chat.id))

@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id, message)

@bot.message_handler(content_types=['text'])
def get_user_text(message):
    if message.text.isdigit():
        # Число которое будет записано в таблицу, столбец cost
        conn = sql.connect(f'{message.from_user.id}.sqlite')
        cur = conn.cursor()
        cur.execute(f"INSERT INTO user{message.from_user.id} (cost, date) VALUES ("
                    f"{int(message.text)}, {message.date // 86400})")
        conn.commit()
        cur.close()
        conn.close()
        mess = f"В какую категорию записать данную сумму? <b>{int(message.text)}</b>"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        cat1 = types.KeyboardButton("Квартира")
        cat2 = types.KeyboardButton("Еда")
        cat3 = types.KeyboardButton("Магазин")
        cat4 = types.KeyboardButton("Кофе")
        cat5 = types.KeyboardButton("Прочее")
        del6 = types.KeyboardButton("Удалить последнюю запись")
        markup.add(cat1, cat2, cat3, cat4, cat5, del6)
        bot.send_message(message.chat.id, mess, reply_markup=markup, parse_mode='html')
    elif message.text in ["Квартира", "Еда", "Магазин", "Кофе", "Прочее"]:
        # Категория которая будет записана в таблицу, столбец category
        conn = sql.connect(f'{message.from_user.id}.sqlite')
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM user{message.from_user.id} ORDER BY id DESC LIMIT 1")
        id_number = int(cur.fetchone()[0])
        cur.execute(f"UPDATE user{message.from_user.id} SET category = '{message.text}' WHERE id = {id_number}")
        conn.commit()
        cur.close()
        conn.close()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        add1 = types.KeyboardButton("Добавить сумму")
        del2 = types.KeyboardButton("Удалить последнюю запись")
        all_info3 = types.KeyboardButton("Покажи мне мои расходы")
        total_day4 = types.KeyboardButton("Сколько потратил(a) за сегодня")
        markup.add(add1, del2, all_info3, total_day4)
        mess = f"Выбрана категория <b>{message.text}</b>"
        bot.send_message(message.chat.id, mess, parse_mode='html')
        bot.send_message(message.chat.id, "Хотите что-то добавить?", reply_markup=markup, parse_mode='html')
    elif message.text == "Добавить сумму":
        mess = f"Отправь сумму, cколько ты сейчас потратил."
        bot.send_message(message.chat.id, mess, parse_mode='html')
    elif message.text == "Удалить последнюю запись":
        conn = sql.connect(f'{message.from_user.id}.sqlite')
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM user{message.from_user.id} ORDER BY id DESC LIMIT 1")
        id_number = int(cur.fetchone()[0])
        cur.execute(f"DELETE FROM user{message.from_user.id} WHERE id = {id_number}")
        conn.commit()
        cur.close()
        conn.close()
        mess = f"Последняя запись удалена"
        bot.send_message(message.chat.id, mess, parse_mode='html')
    elif message.text == "Покажи мне мои расходы":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        exp1 = types.KeyboardButton("Расходы по категориям")
        exp2 = types.KeyboardButton("Сколько потратил(a) за сегодня")
        exp3 = types.KeyboardButton("Все расходы")
        markup.add(exp1, exp2, exp3)
        mess = "Какие расходы хотите увидеть?"
        bot.send_message(message.chat.id, mess, reply_markup=markup, parse_mode='html')
    elif message.text == "Все расходы":
        conn = sql.connect(f'{message.from_user.id}.sqlite')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM user{message.from_user.id}")
        dates = cur.fetchall()
        for date in dates:
            mess = f"Стоимость: {date[1]} | Категория: {date[3]} | Дата: " \
                   f"{datetime.fromtimestamp(date[2] * 86400).strftime('%m.%d.%Y')}"
            bot.send_message(message.chat.id, mess, parse_mode='html')
        conn.commit()
        cur.close()
        conn.close()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        add1 = types.KeyboardButton("Добавить сумму")
        del2 = types.KeyboardButton("Удалить последнюю запись")
        all_info3 = types.KeyboardButton("Покажи мне мои расходы")
        total_day4 = types.KeyboardButton("Сколько потратил(a) за сегодня")
        markup.add(add1, del2, all_info3, total_day4)
        bot.send_message(message.chat.id, "Хотите что-то добавить?", reply_markup=markup, parse_mode='html')
    elif message.text == "Расходы по категориям":
        conn = sql.connect(f'{message.from_user.id}.sqlite')
        cur = conn.cursor()
        for i in ["Квартира", "Еда", "Магазин", "Кофе", "Прочее"]:
            try:
                cur.execute(f"SELECT SUM(cost) FROM user{message.from_user.id} WHERE category = '{i}'")
                total = int(cur.fetchone()[0])
            except Exception:
                total = 0
            mess = f"В категории <b>{i}</b> сумма трат составила: <b>{total}</b>"
            bot.send_message(message.chat.id, mess, parse_mode='html')
        conn.commit()
        cur.close()
        conn.close()
    elif message.text == "Сколько потратил(a) за сегодня":
        conn = sql.connect(f'{message.from_user.id}.sqlite')
        cur = conn.cursor()
        cur.execute(f"SELECT SUM(cost) FROM user{message.from_user.id} WHERE date > {message.date // 86400 - 1}")
        total = int(cur.fetchone()[0])
        print(total)
        conn.commit()
        cur.close()
        conn.close()
        mess = f"За сегодня уже потратил(а): <b>{total}<b>"
        bot.send_message(message.chat.id, mess, parse_mode='html')
    else:
        mess = "Что-то я запутался.."
        bot.send_message(message.chat.id, mess, parse_mode='html')


# if datetime.now().strftime("%H:%M:%S") == "13:11:00":
#     with open("chatID.txt", "r") as txt:
#         for line in txt:
#             mess = "Уже вечер, хочешь записать свои траты за сегодня?"
#             bot.send_message(int(line), mess, parse_mode='html')


bot.polling(none_stop=True)