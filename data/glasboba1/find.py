import sqlite3
import time
import os
from random import choice
from telebot import TeleBot
from telebot.types import InlineKeyboardButton as btn
from telebot import types
from threading import Thread
from phone_variable import phone_variables


asd = '<'
sda = '>'
na = ')'
an = '('

class find():
    def __init__(self) -> None:
        '''Class for find data from databases'''
        self.dbs = os.listdir('databases')
        self.phone_dbs = []
        self.email_dbs = []
        self.id_dbs = []
        self.username_dbs = []
        self.db_c = len(self.dbs)
        for db in self.dbs:
            if 'phone' in db:
                self.phone_dbs.append(db)
            if 'email' in db:
                self.email_dbs.append(db)
            if 'id' in db:
                self.id_dbs.append(db)
            if 'username' in db:
                self.username_dbs.append(db)
        self.dbs_data = {'phone_databases': self.phone_dbs,
                'email_databases': self.email_dbs,
                'id_databases': self.id_dbs,
                'username_databases': self.id_dbs}
   

    def __getitem__(self, item):
        return self.dbs_data[item]


    def __str__(self) -> str:
        return str({'phone_databases': self.phone_dbs,
                'email_databases': self.email_dbs,
                'id_databases': self.id_dbs,
                'username_databases': self.id_dbs})
    

    def db_count(self):
        return str(self.db_c * 2)


    def id_find(self, f_id: str, bot: TeleBot, id: str):
        re_con = sqlite3.connect('databases/res_count.db', check_same_thread=False)
        rcur = re_con.cursor()
        rcur.execute('SELECT * FROM requests WHERE request=?', (f_id,))
        reqs = rcur.fetchone()
        if reqs is None:
            rcur.execute('INSERT INTO requests (request, count) VALUES (?,?)', (f_id, str(1)))
            req = 1
        else:
            rcur.execute('UPDATE requests SET count=? WHERE request=?', (str(int(reqs[-1]) + 1), f_id))
            req = int(reqs[-1]) + 1
        re_con.commit()
        re_con.close()
        start_time = time.time()
        result = {}
        for db in self.id_dbs:
            con = sqlite3.connect(f'databases/{db}', check_same_thread=False)
            cursor1 = con.cursor()
            cursor1.execute("""select * from sqlite_master
    where type = 'table'""")
            tables = cursor1.fetchall()
            for table in tables:
                result[table[1]] = {}
                cursor1.execute(f'PRAGMA table_info({table[1]})')
                cols = [z[1] for z in cursor1.fetchall()]
                try:
                    cursor1.execute(f"SELECT * FROM '{table[1]}' WHERE ID=?", (f_id,))
                except:
                    continue
                res = cursor1.fetchone()
                if not res is None:
                    for i in range(len(cols)):
                        result[table[1]][cols[i]] = res[i]
        text = ''
        result_len = 0
        r_l = ['🔴','🟡','🟢','🔵','🟣','⚫️','⚪️', '🔘','🀄️','◽️','♦️','🎴', '🔶','🔹','🔸','🔻','🔺']
        for db, resp in result.items():
            if resp == {}:
                continue
            unknown = 'неизвестно'
            text += f'{db}:\n'
            for column, value in resp.items():
                text += f'\t\t{choice(r_l)} {column}: <code>{str(value if not value is None else unknown).replace(asd, an).replace(sda, na)}</code>\n'
            result_len += 1
        con.close()
        c = sqlite3.connect('databases/idusernamephone_botik.db', check_same_thread=False)
        cursor = c.cursor()
        cursor.execute('SELECT * FROM bot_users WHERE ID=?', (id,))
        data1 = cursor.fetchone()
        if text != '':
            if data1[5] == 'admin': # .replace(huy, pizda).replace(dot, dot2)
                text = f'📛Результаты поиска по запросу <code>{f_id}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд:\n\n{text}\n\n🔍Интересовались: {req}'
                bot.send_message(id, text, parse_mode="HTML")
            elif int(data1[4]) > 0:
                text = f'📛Результаты поиска по запросу <code>{f_id}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд:\n\n{text}\n\n🔍Интересовались: {req}'
                cursor.execute('UPDATE bot_users SET requests=? WHERE ID=?', (int(data1[4]) - 1, id))
                c.commit()
                bot.send_message(id, text, parse_mode="HTML")
            else:
                text = ""
                for db, resp in result.items():
                    if resp == {}:
                        continue
                    for column, value in resp.items():
                        text += f'\t\t{choice(r_l)} {column}: <code>найдено</code>\n'
                    result_len += 1
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(btn('Купить запросы💳', callback_data='balance'))
                bot.send_message(id, f'📛Результаты поиска по запросу <code>{f_id}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд\n\n{text}\n\n🔍Интересовались: {req}\nНедостаточно запросов, чтобы открыть результаты, купите запросы по кнопке ниже⬇️', reply_markup=keyboard, parse_mode='HTML')
        else:
            bot.send_message(id, f'📛Результаты поиска по запросу <code>{f_id}</code>:\n❌Найдено 0 результатов\nЗапрос не был потрачен', parse_mode='HTML')
        c.close()
        
    
    def username_find(self, username: str, bot: TeleBot, id: str):
        re_con = sqlite3.connect('databases/res_count.db', check_same_thread=False)
        rcur = re_con.cursor()
        rcur.execute('SELECT * FROM requests WHERE request=?', (username,))
        reqs = rcur.fetchone()
        if reqs is None:
            rcur.execute('INSERT INTO requests (request, count) VALUES (?,?)', (username, str(1)))
            req = 1
        else:
            rcur.execute('UPDATE requests SET count=? WHERE request=?', (str(int(reqs[-1]) + 1), username))
            req = int(reqs[-1]) + 1
        re_con.commit()
        re_con.close()
        start_time = time.time()
        result = {}
        for db in self.username_dbs:
            con = sqlite3.connect(f'databases/{db}', check_same_thread=False)
            cursor1 = con.cursor()
            cursor1.execute("""select * from sqlite_master
    where type = 'table'""")
            tables = cursor1.fetchall()
            for table in tables:
                result[table[1]] = {}
                cursor1.execute(f'PRAGMA table_info({table[1]})')
                cols = [z[1] for z in cursor1.fetchall()]
                try:
                    cursor1.execute(f"SELECT * FROM '{table[1]}' WHERE username=?", (username,))
                except:
                    continue
                res = cursor1.fetchone()
                if not res is None:
                    for i in range(len(cols)):
                        result[table[1]][cols[i]] = res[i]
        text = ''
        result_len = 0
        r_l = ['🔴','🟡','🟢','🔵','🟣','⚫️','⚪️', '🔘','🀄️','◽️','♦️','🎴', '🔶','🔹','🔸','🔻','🔺']
        for db, resp in result.items():
            if resp == {}:
                continue
            unknown = 'неизвестно'
            text += f'{db}:\n'
            for column, value in resp.items():
                text += f'\t\t{choice(r_l)} {column}: <code>{str(value if not value is None else unknown).replace(asd, an).replace(sda, na)}</code>\n'
            result_len += 1
        con.close()
        c = sqlite3.connect('databases/idusernamephone_botik.db', check_same_thread=False)
        cursor = c.cursor()
        cursor.execute('SELECT * FROM bot_users WHERE ID=?', (id,))
        data1 = cursor.fetchone()
        if text != '':
            if data1[5] == 'admin': # .replace(huy, pizda).replace(dot, dot2)
                text = f'📛Результаты поиска по запросу <code>{username}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд:\n\n{text}\n\n🔍Интересовались: {req}'
                bot.send_message(id, text, parse_mode="HTML")
            elif int(data1[4]) > 0:
                text = f'📛Результаты поиска по запросу <code>{username}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд:\n\n{text}\n\n🔍Интересовались: {req}'
                cursor.execute('UPDATE bot_users SET requests=? WHERE ID=?', (int(data1[4]) - 1, id))
                c.commit()
                bot.send_message(id, text, parse_mode="HTML")
            else:
                text = ""
                for db, resp in result.items():
                    if resp == {}:
                        continue
                    for column, value in resp.items():
                        text += f'\t\t{choice(r_l)} {column}: <code>найдено</code>\n'
                    result_len += 1
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(btn('Купить запросы💳', callback_data='balance'))
                bot.send_message(id, f'📛Результаты поиска по запросу <code>{username}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд\n\n{text}\n\n🔍Интересовались: {req}\n\nНедостаточно запросов, чтобы открыть результаты, купите запросы по кнопке ниже⬇️', reply_markup=keyboard, parse_mode='HTML')
        else:
            bot.send_message(id, f'📛Результаты поиска по запросу <code>{username}</code>:\n❌Найдено 0 результатов\nЗапрос не был потрачен', parse_mode='HTML')
        c.close()


    def email_find(self, email: str, bot: TeleBot, id: str):
        re_con = sqlite3.connect('databases/res_count.db', check_same_thread=False)
        rcur = re_con.cursor()
        rcur.execute('SELECT * FROM requests WHERE request=?', (email,))
        reqs = rcur.fetchone()
        if reqs is None:
            rcur.execute('INSERT INTO requests (request, count) VALUES (?,?)', (email, str(1)))
            req = 1
        else:
            rcur.execute('UPDATE requests SET count=? WHERE request=?', (str(int(reqs[-1]) + 1), email))
            req = int(reqs[-1]) + 1
        re_con.commit()
        re_con.close()
        start_time = time.time()
        result = {}
        for db in self.email_dbs:
            con = sqlite3.connect(f'databases/{db}', check_same_thread=False)
            cursor1 = con.cursor()
            cursor1.execute("""select * from sqlite_master
    where type = 'table'""")
            tables = cursor1.fetchall()
            for table in tables:
                result[table[1]] = {}
                cursor1.execute(f'PRAGMA table_info({table[1]})')
                cols = [z[1] for z in cursor1.fetchall()]
                try:
                    cursor1.execute(f'SELECT * FROM {table[1]} WHERE email=?', (email,))
                except:
                    continue
                res = cursor1.fetchone()
                if not res is None:
                    for i in range(len(cols)):
                        result[table[1]][cols[i]] = res[i]
        text = ''
        result_len = 0
        r_l = ['🔴','🟡','🟢','🔵','🟣','⚫️','⚪️', '🔘','🀄️','◽️','♦️','🎴', '🔶','🔹','🔸','🔻','🔺']
        for db, resp in result.items():
            if resp == {}:
                continue
            unknown = 'неизвестно'
            text += f'{db}:\n'
            for column, value in resp.items():
                text += f'\t\t{choice(r_l)} {column}: <code>{str(value if not value is None else unknown).replace(asd, an).replace(sda, na)}</code>\n'
            result_len += 1
        con.close()
        c = sqlite3.connect('databases/idusernamephone_botik.db', check_same_thread=False)
        cursor = c.cursor()
        cursor.execute('SELECT * FROM bot_users WHERE ID=?', (id,))
        data1 = cursor.fetchone()
        if text != '':
            if data1[5] == 'admin': # .replace(huy, pizda).replace(dot, dot2)
                text = f'📛Результаты поиска по запросу <code>{email}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд:\n\n{text}\n\n🔍Интересовались: {req}'
                bot.send_message(id, text, parse_mode="HTML")
            elif int(data1[4]) > 0:
                text = f'📛Результаты поиска по запросу <code>{email}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд:\n\n{text}\n\n🔍Интересовались: {req}'
                cursor.execute('UPDATE bot_users SET requests=? WHERE ID=?', (int(data1[4]) - 1, id))
                c.commit()
                bot.send_message(id, text, parse_mode="HTML")
            else:
                text = ""
                for db, resp in result.items():
                    if resp == {}:
                        continue
                    for column, value in resp.items():
                        text += f'\t\t{choice(r_l)} {column}: <code>найдено</code>\n'
                    result_len += 1
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(btn('Купить запросы💳', callback_data='balance'))
                bot.send_message(id, f'📛Результаты поиска по запросу <code>{email}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд:\n\n{text}\n\n🔍Интересовались: {req}\n\nНедостаточно запросов, чтобы открыть результаты, купите запросы по кнопке ниже⬇️', reply_markup=keyboard, parse_mode='HTML')
        else:
            bot.send_message(id, f'📛Результаты поиска по запросу <code>{email}</code>:\n❌Найдено 0 результатов\nЗапрос не был потрачен', parse_mode='HTML')
        c.close()
    
    def phone_find(self, phone_variable: list, bot: TeleBot, id: str):
        re_con = sqlite3.connect('databases/res_count.db', check_same_thread=False)
        rcur = re_con.cursor()
        rcur.execute('SELECT * FROM requests WHERE request=?', (phone_variable[0],))
        reqs = rcur.fetchone()
        if reqs is None:
            rcur.execute('INSERT INTO requests VALUES (?,?)', (str(phone_variable[0]), str(1)))
            req = 1
        else:
            rcur.execute('UPDATE requests SET count=? WHERE request=?', (str(int(reqs[-1]) + 1), phone_variable[0]))
            req = int(reqs[-1]) + 1
        re_con.commit()
        re_con.close()
        start_time = time.time()
        result = {}
        text =''
        for db in self.phone_dbs:
            con = sqlite3.connect(f'databases/{db}', check_same_thread=False)
            cursor1 = con.cursor()
            cursor1.execute("""select * from sqlite_master
    where type = 'table'""")
            tables = cursor1.fetchall()
            for table in tables:
                result[table[1]] = {}
                cursor1.execute(f'PRAGMA table_info({table[1]})')
                cols = [z[1] for z in cursor1.fetchall()]
                for phone in phone_variable:
                    #================
                    try:
                        cursor1.execute(f'select * from {table[1]} where work_phone=?', (phone,))
                        res = cursor1.fetchone()
                        if not res is None:
                            for i in range(len(cols)):
                                result[table[1]][cols[i]] = res[i]
                    except:
                        pass
                    try:
                        cursor1.execute(f'select * from {table[1]} where home_phone=?', (phone,))
                        res = cursor1.fetchone()
                        if not res is None:
                            for i in range(len(cols)):
                                result[table[1]][cols[i]] = res[i]
                    except:
                        pass
                    try:
                        cursor1.execute(f'select * from {table[1]} where mobile_phone=?', (phone,))
                        res = cursor1.fetchone()
                        if not res is None:
                            for i in range(len(cols)):
                                result[table[1]][cols[i]] = res[i]
                    except:
                        pass
                    try:
                        cursor1.execute(f'select * from {table[1]} where phone_number=?', (phone,))
                        res = cursor1.fetchone()
                        if not res is None:
                            for i in range(len(cols)):
                                result[table[1]][cols[i]] = res[i]
                    except:
                        pass
        result_len = 0
        r_l = ['🔴','🟡','🟢','🔵','🟣','⚫️','⚪️', '🔘','🀄️','◽️','♦️','🎴', '🔶','🔹','🔸','🔻','🔺']
        for db, resp in result.items():
            if resp == {}:
                continue
            unknown = 'неизвестно'
            text += f'{db}:\n'
            for column, value in resp.items():
                text += f'\t\t{choice(r_l)} {column}: <code>{str(value if not value is None else unknown).replace(asd, an).replace(sda, na)}</code>\n'
            result_len += 1
        con.close()
        c = sqlite3.connect('databases/idusernamephone_botik.db', check_same_thread=False)
        cursor = c.cursor()
        cursor.execute('SELECT * FROM bot_users WHERE ID=?', (id,))
        data1 = cursor.fetchone()
        if text != '':
            if data1[5] == 'admin': # .replace(huy, pizda).replace(dot, dot2)
                text = f'📛Результаты поиска по запросу <code>{phone_variable[0]}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд:\n\n{text}\n\n🔍Интересовались: {req}'
                bot.send_message(id, text, parse_mode="HTML")
            elif int(data1[4]) > 0:
                text = f'📛Результаты поиска по запросу <code>{phone_variable[0]}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд:\n\n{text}\n\n🔍Интересовались: {req}'
                cursor.execute('UPDATE bot_users SET requests=? WHERE ID=?', (int(data1[4]) - 1, id))
                c.commit()
                bot.send_message(id, text, parse_mode="HTML")
            else:
                text = ""
                for db, resp in result.items():
                    if resp == {}:
                        continue
                    for column, value in resp.items():
                        text += f'\t{choice(r_l)} {column}: <code>найдено</code>\n'
                    result_len += 1
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(btn('Купить запросы💳', callback_data='balance'))
                bot.send_message(id, f'📛Результаты поиска по запросу <code>{phone_variable[0]}</code>:\n✅Найдено {result_len} результатов за {str(int(time.time() - start_time))} секунд:\n\n{text}\n\n🔍Интересовались: {req}\n\nНедостаточно запросов, чтобы открыть результаты, купите запросы по кнопке ниже⬇️', reply_markup=keyboard, parse_mode='HTML')
        else: 
            bot.send_message(id, f'📛Результаты поиска по запросу <code>{phone_variable[0]}</code>:\n❌Найдено 0 результатов\nЗапрос не был потрачен', parse_mode='HTML')
        c.close()


if __name__ == '__main__':
    f = find()
    # f.phone_find(phone_variables('+78129192232'), TeleBot('6305880681:AAHKtOJQtZOoM70Db9QJX0fLY_hqPVu-tzo'), '6345005626')
    f.username_find('CTPAX_DEAHOHEPOB', TeleBot('6305880681:AAHKtOJQtZOoM70Db9QJX0fLY_hqPVu-tzo'), '6345005626')
