from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot import TeleBot
import asyncio
import sqlite3
import os
from config import CRYPTO_TOKEN, BOT_TOKEN, BOT_USERNAME
from find import find
from phone_variable import phone_variables
from threading import Thread
from telebot.types import InlineKeyboardButton as btn
from captcha.image import ImageCaptcha
from random import choice as ch 
from crypto_pay_api_sdk import cryptopay
symbols = 'qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM1234567890!@#$%^&*()'
Crypto = cryptopay.Crypto(CRYPTO_TOKEN, False)
bot = AsyncTeleBot(BOT_TOKEN)

'''main_DB'''

connection = sqlite3.connect('databases/idusernamephone_botik.db', isolation_level=None, check_same_thread=False)
cursor = connection.cursor()
con = sqlite3.connect("databases/phone_id_username.db", check_same_thread=False)
cursor1 = con.cursor()

def data_checker(message):
    #(ID, username, name, captcha, requests, status, captcha_verified, phone_number, refferer)
    cursor.execute('SELECT * FROM bot_users WHERE id=?', (message.from_user.id,))
    data = cursor.fetchone()
    if data is None:
        return
    if data[1] != message.from_user.id:
        cursor.execute('UPDATE bot_users SET username=? WHERE id=?', (message.from_user.username, message.from_user.id))
        cursor1.execute('UPDATE users SET username=? WHERE id=?', (message.from_user.username, message.from_user.id))
    if data[2] != message.from_user.first_name:
        cursor.execute('UPDATE bot_users SET name=? WHERE id=?', (message.from_user.first_name, message.from_user.id))
        cursor1.execute('UPDATE users SET first_name=? WHERE id=?', (message.from_user.first_name, message.from_user.id))
    connection.commit()
    con.commit()

@bot.message_handler(commands=['help'])
async def help(call):
    data_checker(call)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(btn('Назад◀️', callback_data='back'))
    f = find()
    databases = []
    for db in f.dbs:
        con = sqlite3.connect(f'databases/{db}', check_same_thread=False)
        cur = con.cursor()
        cur.execute("""select * from sqlite_master
    where type = 'table'""")
        tables = cur.fetchall()
        for table in tables:
            databases.append(table[1])
    n = '\n\t👾'
    dbs = [f'\t{db}' for db in databases[:25:-1]]
    dbs.sort()
    await bot.send_message(call.from_user.id, f'Ответы на часто-задаваемые вопросы:\nКак скрыть номер телефона?\n\tНапишите /start, и нажмите кнопку: скрыть данные\n\nКак осуществляется поиск?\n\tПоиск осуществляется по:\n\tНомеру телефона(В международном формате +79999999999)\n\tЭлектронной почте\n\tТелеграм ID(Отправьте команду `/u <ID>`)\n\tЮзернэйму (Строка начинающаяся на @)\n\nКоличество баз данных: {len(databases)}: \n\t👾{n.join(dbs)}...\n\nНачинайте поиск!')


@bot.message_handler(commands=['referer']) 
async def referer(call):
    data_checker(call)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(btn('Назад◀️', callback_data='back'))
    cursor.execute('SELECT refferer FROM bot_users WHERE refferer=?', (call.from_user.id,))
    refs = cursor.fetchall()
    try:
        re_l = len(refs)
    except:
        re_l = 0
    await bot.send_message(call.from_user.id, f'В нашем боте существует система рефералов, если по вашей ссылке в бота заходит человек, то вы получаете 1 запроса\nВаша реферальная ссылка:\nhttps://t.me/{BOT_USERNAME}?start={call.from_user.id}\n\nКол-во ваших рефералов: {re_l}', reply_markup=keyboard)

@bot.message_handler(commands=['online'])
async def online(call):
    data_checker(call)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(btn('Назад◀️', callback_data='back'))
    cursor.execute('select id from bot_users')
    just_users = len(cursor.fetchall())
    cursor1.execute('select id from users')
    phone_verified = len(cursor1.fetchall())
    await bot.send_message(call.from_user.id, f'Всего пользователей: {just_users}\nПользователей, подтвердивших номер телефона: {phone_verified}', reply_markup=keyboard)
    

@bot.message_handler(commands=['profile'])
async def profile(call):
    data_checker(call)
    cursor.execute('SELECT * FROM bot_users WHERE id=?', (str(call.from_user.id),))
    data = cursor.fetchone()
    star = '*'
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(btn('Профиль🫵', callback_data='profile'), btn('Реферальная система🤝', callback_data='refferal'))
    keyboard.row(btn('Купить запросы💳', callback_data='balance'))
    keyboard.row(btn('Онлайн бота☺️', callback_data='online'))
    vanihed = 'Скрыт'
    await bot.send_message(call.from_user.id, f'Ваш профиль в боте выглядит так:\nID: <code>{data[0]}</code>\nUsername: <b>@{data[1]}</b>\nКол-во запросов: <code>{data[4]}</code>\nСтатус в проекте: <code>{data[5]}</code>\nНомер телефона: <code>{data[-2][:7] + 5 * star if data[-2] != vanihed else vanihed}</code>\n\nНачинайте поиск!', reply_markup=keyboard, parse_mode='HTML')


@bot.message_handler(commands=['market'])
async def balance(call):
    data_checker(call)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(btn('20', callback_data='20'), btn('50', callback_data='50'))
    keyboard.row(btn('100', callback_data='100'), btn('200', callback_data='200'))
    keyboard.row(btn('500', callback_data='500'), btn('750', callback_data='750'))
    keyboard.row(btn('1000', callback_data='1000'))
    keyboard.row(btn('Назад◀️', callback_data='back'))
    await bot.send_message(call.from_user.id, f'Вы попали на меню покупки запросов, выберите сколько запросов вы хотите купить:', reply_markup=keyboard)


@bot.message_handler(commands=['give_requests'])
async def give_requests(message):
    data_checker(message)
    cursor.execute('SELECT * FROM bot_users WHERE id=?', (str(message.from_user.id),))
    data = cursor.fetchone()
    if data[5] == 'user':
        await bot.send_message(message.from_user.id, 'Команда доступна только для администраторов проекта')
        return
    try:
        user_id = message.text.split()[1]
        new_requests = message.text.split()[2]
    except:
        await bot.send_message(message.from_user.id, f'Отправь команду с таким синтаксисом: `/give_requests <тг айди> <количество>')
        return
    try:
        cursor.execute('SELECT * FROM bot_users WHERE ID=?', (user_id,))
        user_data = cursor.fetchone()
        cursor.execute('UPDATE bot_users SET requests=? WHERE ID=?', (int(new_requests) + int(user_data[4]), user_id))
        await bot.send_message(user_id, f'Позравляю, администратор {message.from_user.id}>{message.from_user.first_name} выдал вам {new_requests} запросов!')
        await bot.send_message(message.chat.id, f'Успешная выдача, {new_requests} запросов для: {user_id}!')
    except:
        await bot.send_message(message.chat.id, f'Ошибка, кажется человек с ID: {user_id} не зарегистрирован в системе(')
    connection.commit()


@bot.message_handler(content_types=['contact'])
async def contact_check(message):
    data_checker(message)
    cursor.execute('select * from bot_users where id=?', (message.from_user.id,))
    d = cursor.fetchone()
    if d[7] is None:
        cursor1.execute('INSERT INTO users (ID, username, first_name, phone_number) VALUES (?,?,?,?)', (message.from_user.id, message.from_user.username, message.from_user.first_name, f'+{message.contact.phone_number}' if '+' not in message.contact.phone_number else message.contact.phone_number))
    else:
        await bot.send_message(message.from_user.id, 'Вы уже подтверждали свой номер телефона')
        return
    con.commit()
    cursor.execute('UPDATE bot_users SET phone_number=? WHERE ID=?', (f'+{message.contact.phone_number}', message.from_user.id))
    await bot.send_message(message.chat.id, 'Спасибо за подтверждение номера телефона, перезапустите бота по команде /start')
    connection.commit()


@bot.message_handler(commands=['start'])
async def start(message):
    data_checker(message)
    cursor.execute('SELECT * FROM bot_users WHERE ID=?', (str(message.from_user.id),))
    data = cursor.fetchone()
    try:
        refferer = message.text.split()[1]
    except:
        refferer = None
    if data == None:
        keyboard = types.InlineKeyboardMarkup()
        captcha_list = [f'{ch(symbols)}{ch(symbols)}{ch(symbols)}{ch(symbols)}{ch(symbols)}{ch(symbols)}' for _ in range(4)]
        user_captcha = ch(captcha_list)
        image = ImageCaptcha(width=400, height=130)
        data = image.generate_image(user_captcha)
        path = f'{message.from_user.id}.png'
        data = image.generate(user_captcha)
        image.write(user_captcha, path)
        keyboard.row(btn(captcha_list[0], callback_data=captcha_list[0]), btn(captcha_list[1], callback_data=captcha_list[1]))
        keyboard.row(btn(captcha_list[2], callback_data=captcha_list[2]), btn(captcha_list[3], callback_data=captcha_list[3]))
        cursor.execute('INSERT INTO bot_users (ID, username, name, captcha, requests, status, captcha_verified, phone_number, refferer) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (message.from_user.id, message.from_user.username, message.from_user.first_name, user_captcha, 0, 'user', False, None, refferer))
        await bot.send_photo(message.chat.id, open(path, 'rb'), caption=f'Здравствуйте, {message.from_user.first_name}, пожалуйста пройдите капчу, чтобы начать пользоваться данным ботом', reply_markup=keyboard)
        os.remove(f'{message.from_user.id}.png')
        if not refferer is None:
            cursor.execute('SELECT * FROM bot_users WHERE ID=?', (refferer,))
            t = cursor.fetchone()
            if not t is None:
                await bot.send_message(refferer, f'{t[2]},Поздравляю, у вас новый реферал: {message.from_user.first_name}')
    elif not data[-3]:
        await bot.send_message(message.chat.id, 'Пожалуйста, решите капчу')
    elif data[-2] == None:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(types.KeyboardButton('Подтвердить номер телефона✅', True))
        await bot.send_message(message.chat.id, 'Пожалуйста, подтвердите номер телефона', reply_markup=keyboard)
    else:
        if not refferer is None:
            if data[-1] is None:
                cursor.execute('UPDATE bot_users SET refferer=? WHERE id=?', (refferer, message.from_user.id))
                cursor.execute('SELECT * FROM bot_users WHERE id=?', (refferer,))
                t = cursor.fetchone()
                cursor.execute('UPDATE bot_users SET requests=? WHERE id=?', (int(t[4]) + 1, refferer))
                await bot.send_message(refferer, f'{t[2]},Поздравляю, у вас новый реферал: {message.from_user.first_name}')
            else:
                await bot.send_message(message.chat.id, 'Вы уже являетесь рефералом.')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(btn('Профиль🫵', callback_data='profile'), btn('Реферальная система🤝', callback_data='refferal'))
        keyboard.row(btn('Купить запросы💳', callback_data='balance'))
        keyboard.row(btn('Онлайн бота☺️', callback_data='online'))
        await bot.send_message(message.chat.id, f'Добро пожаловать в нашего бота для пробива\n\nВыберите пункт ниже, что бы начать поиск.', reply_markup=keyboard)
    
    connection.commit()


@bot.callback_query_handler(func=lambda x: True)
async def inline_buttons(call):
    data_checker(call)
    try:
        cursor.execute('SELECT * FROM bot_users WHERE id=?', (call.from_user.id,))
        data = cursor.fetchone()

        #=====================================

        if call.data == '20':
            con = sqlite3.connect('invoice_checking.db', isolation_level=None, check_same_thread=False)
            cursor1 = con.cursor()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(btn('Проверить оплату✅', callback_data='b_check'))
            pay_d = Crypto.createInvoice('USDT', '1.0', {'description': 'Нажимая кнопку ниже, вы купите 20 запросов для телеграм бота @EyeOfBudda_robot\nПосле покупки, нажмите: подтвердить оплату в боте', 'allow_anonymous': False, 'expires_in': '2678400'})
            link = pay_d['result']['pay_url']
            await bot.send_message(call.from_user.id, f'{call.from_user.first_name} Вы собираетесь купить 20 запросов, это будет стоить 1$\nМожете оплатить заказ по ссылке ниже:\n\n{link}', reply_markup=keyboard)
            cursor1.execute('select * from data where id=?', (call.from_user.id,))
            if cursor1.fetchone() != None:
                cursor1.execute('update data set invoice_id=? where id=?', (pay_d['result']['invoice_id'], call.from_user.id))
                cursor1.execute('update data set r=? where id=?', ('20', call.from_user.id))
            else:
                cursor1.execute('insert into data (ID, invoice_id, r) values (?, ?, ?)', (call.from_user.id, pay_d['result']['invoice_id'], '20'))
            con.commit()
        elif call.data == '50':
        #=====================================
            con = sqlite3.connect('invoice_checking.db', isolation_level=None, check_same_thread=False)
            cursor1 = con.cursor()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(btn('Проверить оплату✅', callback_data='b_check'))
            pay_d = Crypto.createInvoice('USDT', '2.5', {'description': 'Нажимая кнопку ниже, вы купите 20 запросов для телеграм бота @EyeOfBudda_robot\nПосле покупки, нажмите: подтвердить оплату в боте', 'allow_anonymous': False, 'expires_in': '2678400'})
            link = pay_d['result']['pay_url']
            await bot.send_message(call.from_user.id, f'{call.from_user.first_name} Вы собираетесь купить 50 запросов, это будет стоить 2.5$\nМожете оплатить заказ по ссылке ниже:\n\n{link}', reply_markup=keyboard)
            cursor1.execute('select * from data where id=?', (call.from_user.id,))
            if cursor1.fetchone() != None:
                cursor1.execute('update data set invoice_id=? where id=?', (pay_d['result']['invoice_id'], call.from_user.id))
                cursor1.execute('update data set r=? where id=?', ('20', call.from_user.id))
            else:
                cursor1.execute('insert into data (ID, invoice_id, r) values (?, ?, ?)', (call.from_user.id, pay_d['result']['invoice_id'], '20'))
            con.commit()
        elif call.data == '100':
        #=====================================
            con = sqlite3.connect('invoice_checking.db', isolation_level=None, check_same_thread=False)
            cursor1 = con.cursor()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(btn('Проверить оплату✅', callback_data='b_check'))
            pay_d = Crypto.createInvoice('USDT', '4.5', {'description': 'Нажимая кнопку ниже, вы купите 20 запросов для телеграм бота @EyeOfBudda_robot\nПосле покупки, нажмите: подтвердить оплату в боте', 'allow_anonymous': False, 'expires_in': '2678400'})
            link = pay_d['result']['pay_url']
            await bot.send_message(call.from_user.id, f'{call.from_user.first_name} Вы собираетесь купить 100 запросов, это будет стоить 4.5$\nМожете оплатить заказ по ссылке ниже:\n\n{link}', reply_markup=keyboard)
            cursor1.execute('select * from data where id=?', (call.from_user.id,))
            if cursor1.fetchone() != None:
                cursor1.execute('update data set invoice_id=? where id=?', (pay_d['result']['invoice_id'], call.from_user.id))
                cursor1.execute('update data set r=? where id=?', ('20', call.from_user.id))
            else:
                cursor1.execute('insert into data (ID, invoice_id, r) values (?, ?, ?)', (call.from_user.id, pay_d['result']['invoice_id'], '20'))
            con.commit()
        elif call.data == '200':
        #=====================================
            con = sqlite3.connect('invoice_checking.db', isolation_level=None, check_same_thread=False)
            cursor1 = con.cursor()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(btn('Проверить оплату✅', callback_data='b_check'))
            pay_d = Crypto.createInvoice('USDT', '8.0', {'description': 'Нажимая кнопку ниже, вы купите 20 запросов для телеграм бота @EyeOfBudda_robot\nПосле покупки, нажмите: подтвердить оплату в боте', 'allow_anonymous': False, 'expires_in': '2678400'})
            link = pay_d['result']['pay_url']
            await bot.send_message(call.from_user.id, f'{call.from_user.first_name} Вы собираетесь купить 200 запросов, это будет стоить 8$\nМожете оплатить заказ по ссылке ниже:\n\n{link}', reply_markup=keyboard)
            cursor.execute('select * from data where id=?', (call.from_user.id,))
            if cursor1.fetchone() != None:
                cursor1.execute('update data set invoice_id=? where id=?', (pay_d['result']['invoice_id'], call.from_user.id))
                cursor1.execute('update data set r=? where id=?', ('20', call.from_user.id))
            else:
                cursor1.execute('insert into data (ID, invoice_id, r) values (?, ?, ?)', (call.from_user.id, pay_d['result']['invoice_id'], '20'))
            con.commit()
        elif call.data == '500':
        #=====================================
            con = sqlite3.connect('invoice_checking.db', isolation_level=None, check_same_thread=False)
            cursor1 = con.cursor()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(btn('Проверить оплату✅', callback_data='b_check'))
            pay_d = Crypto.createInvoice('USDT', '15.0', {'description': 'Нажимая кнопку ниже, вы купите 20 запросов для телеграм бота @EyeOfBudda_robot\nПосле покупки, нажмите: подтвердить оплату в боте', 'allow_anonymous': False, 'expires_in': '2678400'})
            link = pay_d['result']['pay_url']
            await bot.send_message(call.from_user.id, f'{call.from_user.first_name} Вы собираетесь купить 500 запросов, это будет стоить 15$\nМожете оплатить заказ по ссылке ниже:\n\n{link}', reply_markup=keyboard)
            cursor1.execute('select * from data where id=?', (call.from_user.id,))
            if cursor1.fetchone() != None:
                cursor1.execute('update data set invoice_id=? where id=?', (pay_d['result']['invoice_id'], call.from_user.id))
                cursor1.execute('update data set r=? where id=?', ('20', call.from_user.id))
            else:
                cursor1.execute('insert into data (ID, invoice_id, r) values (?, ?, ?)', (call.from_user.id, pay_d['result']['invoice_id'], '20'))
            con.commit()
        elif call.data == '750':
        #=====================================
            con = sqlite3.connect('invoice_checking.db', isolation_level=None, check_same_thread=False)
            cursor1 = con.cursor()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(btn('Проверить оплату✅', callback_data='b_check'))
            pay_d = Crypto.createInvoice('USDT', '20.0', {'description': 'Нажимая кнопку ниже, вы купите 20 запросов для телеграм бота @EyeOfBudda_robot\nПосле покупки, нажмите: подтвердить оплату в боте', 'allow_anonymous': False, 'expires_in': '2678400'})
            link = pay_d['result']['pay_url']
            await bot.send_message(call.from_user.id, f'{call.from_user.first_name} Вы собираетесь купить 750 запросов, это будет стоить 20$\nМожете оплатить заказ по ссылке ниже:\n\n{link}', reply_markup=keyboard)
            cursor1.execute('select * from data where id=?', (call.from_user.id,))
            if cursor1.fetchone() != None:
                cursor1.execute('update data set invoice_id=? where id=?', (pay_d['result']['invoice_id'], call.from_user.id))
                cursor1.execute('update data set r=? where id=?', ('20', call.from_user.id))
            else:
                cursor1.execute('insert into data (ID, invoice_id, r) values (?, ?, ?)', (call.from_user.id, pay_d['result']['invoice_id'], '20'))
            con.commit()
        elif call.data == '1000':
        #=====================================
            con = sqlite3.connect('invoice_checking.db', isolation_level=None, check_same_thread=False)
            cursor1 = con.cursor()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(btn('Проверить оплату✅', callback_data='b_check'))
            pay_d = Crypto.createInvoice('USDT', '23.0', {'description': 'Нажимая кнопку ниже, вы купите 20 запросов для телеграм бота @EyeOfBudda_robot\nПосле покупки, нажмите: подтвердить оплату в боте', 'allow_anonymous': False, 'expires_in': '2678400'})
            link = pay_d['result']['pay_url']
            await bot.send_message(call.from_user.id, f'{call.from_user.first_name} Вы собираетесь купить 1000 запросов, это будет стоить 23$\nМожете оплатить заказ по ссылке ниже:\n\n{link}', reply_markup=keyboard)
            cursor.execute('select * from data where id=?', (call.from_user.id,))
            if cursor1.fetchone() != None:
                cursor1.execute('update data set invoice_id=? where id=?', (pay_d['result']['invoice_id'], call.from_user.id))
                cursor1.execute('update data set r=? where id=?', ('20', call.from_user.id))
            else:
                cursor1.execute('insert into data (ID, invoice_id, r) values (?, ?, ?)', (call.from_user.id, pay_d['result']['invoice_id'], '20'))
            con.commit()
        #=====================================
        elif call.data == 'profile' or call.data == 'back':
            await profile(call)
        elif call.data == 'refferal':
            await referer(call)
        elif call.data == 'balance':
            await balance(call)
        elif call.data == 'online':
            await online(call)
        elif call.data == 'b_check':
            con1 = sqlite3.connect('invoice_checking.db', isolation_level=None, check_same_thread=False)
            cursor1 = con1.cursor()
            cursor1.execute('select * from data where id=?', (call.from_user.id,))
            t = cursor1.fetchone()
            if t[1] is None:
                await bot.send_message(call.from_user.id, 'Счёт уже оплачен✅')
                return
            else:
                if Crypto.getInvoices({'invoice_ids': t[1]})['result']['items'][0]['status'] == 'paid':
                    await bot.send_message(call.from_user.id, 'Спасибо за покупку запросов в нашем боте, можете начинать поиск')
                    r = data[4]
                    if not r == '♾':
                        cursor.execute('update bot_users set requests=? where id=?', (int(r) + int(t[-1]), call.from_user.id))
                    cursor1.execute('update data set invoice_id=? where ID=?', (None, call.from_user.id))
                else:
                    await bot.send_message(call.from_user.id, 'Вы не оплатили счёт, оплатите, и повторите снова')
            con1.commit()
        elif call.data == data[3]:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard.add(types.KeyboardButton('Подтвердить номер телефона✅', True))
            cursor.execute('UPDATE bot_users SET captcha_verified=? WHERE ID=?', (True, call.from_user.id))
            connection.commit()
            await bot.send_message(call.from_user.id, f'Капча пройдена успешна, подтвердите номер телефона по кнопке ниже:\n\n*Ваши данные останутся приватными, в любой момент в разделе аккаунт вы можете запросить удаление данных', reply_markup=keyboard)
        else:
            await bot.send_message(call.from_user.id, f'Капча не пройдена, попробуйте заново')
        #==========================================
        connection.commit()
    except Exception as e:
        await bot.send_message(call.from_user.id, str(e))


@bot.message_handler(commands=['send'])
async def hehe(message):
    data_checker(message)
    cursor.execute('SELECT * FROM bot_users WHERE ID=?', (message.from_user.id,))
    data = cursor.fetchone()
    if data[5] == 'admin':
        msg = message.text[6:]
        cursor.execute('select id from bot_users')
        ids = cursor.fetchall()
        good = 0
        bad = 0
        for id in ids:
            try:
                await bot.send_message(id[0], msg)
                good += 1
            except:
                bad += 1
        await bot.send_message(message.from_user.id, f'Сообщения были отправлены всем активным пользователям:\nАктивных пользователей:{good}\nНеактивных пользователей: {bad}\n\nНеактивный пользователь-человек, который заблокировал бота/несуществующий аккаунт\n\nВсе неактивные пользователи были удалены из БД.')
    else:
        await bot.send_message(message.from_user.id, 'Для этого нужно быть админом🤓')


@bot.message_handler(commands=['u'])
@bot.message_handler(func=lambda s: True)
async def ind(message):
    data_checker(message)
    try:
        cursor.execute('SELECT * FROM bot_users WHERE ID=?', (message.from_user.id,))
        data = cursor.fetchone()
        if data is None:
            await bot.send_message(message.from_user.id, 'Пожалуйста, пройдите верификацию в боте по команде /start')
        if not data[-3]:
            await bot.send_message(message.chat.id, 'Пожалуйста, решите капчу⬆️')
            return
        elif data[-2] is None:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard.add(types.KeyboardButton('Подтвердить номер телефона✅', True))
            await bot.send_message(message.chat.id, 'Пожалуйста, подтвердите номер телефона⬆️', reply_markup=keyboard)
            return
        f = find()
        if message.text.startswith('@'):
            print(message.text, 'username')
            Thread(target=f.username_find, args=(message.text[1:], TeleBot(BOT_TOKEN), str(message.from_user.id))).start()
        elif '@' in message.text:
            print(message.text, 'email')
            Thread(target=f.email_find, args=(message.text, TeleBot(BOT_TOKEN), str(message.from_user.id))).start()
        elif message.text.startswith('+') and (len(message.text) == 12 or len(message.text) == 13 or len(message.text) == 14):
            print(message.text, 'phone_number')
            Thread(target=f.phone_find, args=(phone_variables(message.text), TeleBot(BOT_TOKEN), str(message.from_user.id))).start()
        elif message.text.startswith('/u'):
            print(message.text, 'uid')
            Thread(target=f.id_find, args=(message.text[3:], TeleBot(BOT_TOKEN), str(message.from_user.id))).start()
        else:
            return
        #======================
    except Exception as e:
        await bot.reply_to(message, e)

        
try:
    asyncio.run(bot.infinity_polling())
except:
    pass