#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import sys
import socket
import re
import subprocess
import threading
import requests
import json
import webbrowser

# Проверка наличия dnspython
try:
    import dns.resolver
    import dns.reversename
except ImportError:
    print("\033[91m[ОШИБКА] Модуль 'dnspython' не найден.\033[0m")
    print("Установите его командой: pip install dnspython")
    sys.exit(1)

try:
    import phonenumbers
    from phonenumbers import carrier, geocoder, timezone
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False

# Двоичный код пароля "admin"
ENCODED_PASSWORD = "0110000101100100011011010110100101101110"

# Глобальный флаг для пропуска заставок
skip_flag = False

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_skip():
    """Потоковая функция для ожидания нажатия Enter."""
    global skip_flag
    input()
    skip_flag = True

def mining_animation():
    global skip_flag
    current = 0.04
    end = 0.18
    step = 0.01
    print("\033[91mWARNING: Mining start, stay on your PC\033[0m")
    print("(Нажмите Enter, чтобы пропустить)\n")
    skip_flag = False
    skip_thread = threading.Thread(target=wait_for_skip, daemon=True)
    skip_thread.start()

    while current <= end + 0.0001 and not skip_flag:
        formatted = f"{current:.2f}".rstrip('0').rstrip('.')
        print(f"BTC: {formatted}+")
        time.sleep(0.5)
        current += step
        if abs(current - end) < 0.0001:
            break
    clear_console()

def rgb_gradient_text(text, steps=None):
    lines = text.strip('\n').split('\n')
    if not lines:
        return text
    result = []
    for i, line in enumerate(lines):
        t = i / max(1, len(lines) - 1)
        if t < 0.5:
            r = int(255 * (1 - t * 2))
            g = int(255 * (t * 2))
            b = 0
        else:
            t2 = (t - 0.5) * 2
            r = 0
            g = int(255 * (1 - t2))
            b = int(255 * t2)
        color = f"\033[38;2;{r};{g};{b}m"
        result.append(f"{color}{line}\033[0m")
    return '\n'.join(result)

def show_ascii_art():
    art = r"""
 __      __            .__       .___ ___________             __    
/  \    /  \___________|  |    __| _/ \_   _____/_ __   ____ |  | __
\   \/\/   /  _ \_  __ \  |   / __ |   |    __)|  |  \_/ ___\|  |/ /
 \        (  <_> )  | \/  |__/ /_/ |   |     \ |  |  /\  \___|    < 
  \__/\  / \____/|__|  |____/\____ |   \___  / |____/  \___  >__|_ \
       \/                         \/       \/              \/     \/
"""
    colored_art = rgb_gradient_text(art, None)
    print(colored_art)
    print()
    clean_lines = art.strip('\n').split('\n')
    max_len = max(len(line) for line in clean_lines)
    line = "─" * max_len
    print(f"\033[92m{line}\033[0m")
    print(f"version: 0.1.0")
    print(f"creator: liquid, fucklife")

def flash_text():
    global skip_flag
    words = [
        "bayrut", "hulsea", "orissa", "abipon", "aeolid", "anchor", "anukit",
        "aspace", "assoil", "avenin", "awhile", "azande", "cackle", "carest",
        "carrie", "cashew", "cebine", "cletch", "clique", "dapico", "darkly",
        "debile", "dentin", "doomer", "dugway", "dungan", "easter", "etymic",
        "figure", "figury", "fitful", "gabion", "gifola", "gradal", "gradin",
        "grimme", "hallel", "hyenic", "kinkle", "kronen", "kudrun", "lierre",
        "loment", "lunule", "medius", "milsey", "minder", "mutule", "nongas",
        "nubble", "numero", "orchel", "orgeat", "parode", "patera", "phocal",
        "podsol", "porose", "rabbet", "radula", "randia", "rebute", "relume",
        "remuda", "repour", "revote", "rickey", "rudolf", "ruskin", "sander",
        "savant", "secern", "setule", "smethe", "solace", "sozzle", "spoffy",
        "surfle", "swathy", "tanbur", "tandem", "thrift", "thulir", "tidely",
        "trapes", "unprop", "unspun", "untrig", "uphand", "uplock", "upmove",
        "usward", "valley", "values", "vernal", "voidee", "wagaun", "wedged"
    ]
    print("\033[91mНажмите Enter, чтобы пропустить текстовую заставку...\033[0m")
    skip_flag = False
    skip_thread = threading.Thread(target=wait_for_skip, daemon=True)
    skip_thread.start()

    for word in words:
        if skip_flag:
            break
        sys.stdout.write(f"\033[91m{word}\033[0m\n")
        sys.stdout.flush()
        time.sleep(0.03)
    time.sleep(0.3)
    if not skip_flag:
        input("\nНажмите Enter для продолжения...")
    clear_console()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Не удалось определить IP"

# ========== НОВАЯ ФУНКЦИЯ ДЛЯ ЗАПУСКА ВНЕШНИХ СКРИПТОВ ==========
def run_script(script_path):
    """Запускает внешний Python-скрипт и выводит ошибки, если файл не найден."""
    try:
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\033[91mОшибка при выполнении скрипта {script_path}: {e}\033[0m")
    except FileNotFoundError:
        print(f"\033[91mСкрипт {script_path} не найден.\033[0m")
        print("Убедитесь, что папка 'data' существует и в ней лежат нужные файлы.")

# === ЗАМЕНЁННЫЕ ФУНКЦИИ (ЗАПУСК ВНЕШНИХ СКРИПТОВ) ===
def ip_information():
    """
    Подменю с двумя колонками в голубой рамке (стиль как в главном меню):
    - Левая: Telegram bots (ссылки на ботов)
    - Правая: .py program (информация о Python-скриптах)
    """
    while True:
        clear_console()
        show_ascii_art()

        # Ширина каждой рамки
        left_width = 40
        right_width = 35
        color = "\033[96m"      # голубой цвет рамок
        reset = "\033[0m"

        # Символы псевдографики
        corner_tl = "┌"
        corner_tr = "┐"
        corner_bl = "└"
        corner_br = "┘"
        vertical = "│"
        border_char = "─"

        def make_line(left_text, right_text, is_top=False, is_bottom=False):
            # Левая рамка
            if is_top:
                left = corner_tl + border_char * (left_width + 2) + corner_tr
            elif is_bottom:
                left = corner_bl + border_char * (left_width + 2) + corner_br
            else:
                left_text_filled = left_text.ljust(left_width)
                left = f"{vertical} {left_text_filled} {vertical}"
            # Правая рамка
            if is_top:
                right = corner_tl + border_char * (right_width + 2) + corner_tr
            elif is_bottom:
                right = corner_bl + border_char * (right_width + 2) + corner_br
            else:
                right_text_filled = right_text.ljust(right_width)
                right = f"{vertical} {right_text_filled} {vertical}"
            # Объединяем с цветом и пробелом между рамками
            return f"{color}{left}{reset}  {color}{right}{reset}"

        # Верхняя линия
        print(make_line("", "", is_top=True))
        # Заголовки
        print(make_line(" Telegram bots ", " .py program "))
        # Пустая строка-разделитель
        print(make_line("", ""))
        # Содержимое
        left_items = [
            "1. Sherlock (Telegram bot)",
            "2. 2ip whois",
            "0. Назад в главное меню"
        ]
        right_items = [
            "В разработке...",
            "Скрипты Python",
            "будут добавлены позже"
        ]
        max_rows = max(len(left_items), len(right_items))
        for i in range(max_rows):
            left_txt = left_items[i] if i < len(left_items) else ""
            right_txt = right_items[i] if i < len(right_items) else ""
            print(make_line(left_txt, right_txt))
        # Нижняя линия
        print(make_line("", "", is_bottom=True))

        choice = input(f"\n{color}Выберите номер из левого меню (0-2): {reset}").strip()
        if choice == "1":
            webbrowser.open("https://t.me/He_rlokbot?start=_ref_85i7qn35Y_FtiF66U6T")
            print(f"{color}Открыт Telegram-бот Sherlock.{reset}")
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "2":
            webbrowser.open("https://2ip.ru/whois/")
            print(f"{color}Открыт сервис 2ip whois.{reset}")
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "0":
            break
        else:
            print(f"{color}Неверный выбор. Попробуйте снова.{reset}")
            input("\nНажмите Enter...")

def email_information():
    print("\n=== Email Address Information ===")
    run_script("data/emailsearch.py")
    input("\nНажмите Enter, чтобы продолжить...")

def phone_number_info():
    print("\n=== Phone Number Information ===")
    run_script("data/phonesearch.py")
    input("\nНажмите Enter, чтобы продолжить...")

def hosts_search():
    print("\n=== Hosts Search ===")
    run_script("data/hostssearch.py")
    input("\nНажмите Enter, чтобы продолжить...")

# === ОСТАЛЬНЫЕ ФУНКЦИИ (НЕ ИЗМЕНЕНЫ) ===
def exploit_cve():
    print("\n=== Exploit CVE ===")
    cve_id = input("Введите идентификатор CVE (например CVE-2021-44228): ").strip().upper()
    if not re.match(r'CVE-\d{4}-\d{4,}', cve_id):
        print("Неверный формат CVE. Пример: CVE-2021-44228")
        input("\nНажмите Enter, чтобы продолжить...")
        return
    try:
        url = f"https://cve.circl.lu/api/cve/{cve_id}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'id' in data:
                print(f"ID: {data['id']}")
                print(f"Описание: {data.get('summary', 'Нет описания')[:500]}...")
                print(f"CVSS v2: {data.get('cvss', 'не указан')}")
                print(f"Дата публикации: {data.get('Published', 'неизвестно')}")
            else:
                print("Информация по CVE не найдена.")
        else:
            print("Ошибка при запросе к API.")
    except Exception as e:
        print(f"Ошибка: {e}")
    input("\nНажмите Enter, чтобы продолжить...")

def dns_lookup():
    print("\n=== DNS Lookup ===")
    domain = input("Введите домен: ").strip()
    record_types = ['A', 'AAAA', 'MX', 'TXT']
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            print(f"\n{rtype} записи:")
            for ans in answers:
                print(f"  {ans}")
        except dns.resolver.NoAnswer:
            print(f"\n{rtype} записи: нет")
        except Exception as e:
            print(f"\n{rtype} записи: ошибка - {e}")
    input("\nНажмите Enter, чтобы продолжить...")

def dns_reverse():
    print("\n=== DNS Reverse ===")
    ip = input("Введите IP-адрес: ").strip()
    try:
        rev_name = dns.reversename.from_address(ip)
        ptr = dns.resolver.resolve(rev_name, "PTR")
        print(f"PTR запись: {ptr[0]}")
    except Exception as e:
        print(f"Не удалось получить PTR запись: {e}")
    input("\nНажмите Enter, чтобы продолжить...")

def email_searcher():
    print("\n=== Email Searcher ===")
    print("Для поиска email адресов по домену используется API Hunter.io (требуется ключ).")
    api_key = input("Введите ваш API ключ Hunter.io (или оставьте пустым для демо): ").strip()
    domain = input("Введите домен: ").strip()
    if not api_key:
        print("Демо-режим: без API ключа поиск невозможен.")
        print("Зарегистрируйтесь на hunter.io и получите бесплатный ключ.")
    else:
        try:
            url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                emails = data.get('data', {}).get('emails', [])
                if emails:
                    print(f"Найдено {len(emails)} email адресов:")
                    for e in emails:
                        print(f"  {e['value']} (источник: {e.get('sources', [{}])[0].get('domain', 'неизвестно')})")
                else:
                    print("Email адреса не найдены.")
            else:
                print(f"Ошибка API: {response.status_code}")
        except Exception as e:
            print(f"Ошибка: {e}")
    input("\nНажмите Enter, чтобы продолжить...")

def spam_with_html():
    """
    Спам словами и последовательное открытие трех HTML-файлов с автозакрытием.
    """
    print("\n=== Спам словами + HTML-файлы ===")
    spam_words = [
        "spam", "word", "exploit", "hack", "bypass", "overflow", "injection",
        "xss", "csrf", "rdp", "ssh", "ftp", "malware", "ransomware", "payload",
        "backdoor", "rootkit", "keylogger", "trojan", "worm", "phishing"
    ]
    print("\033[91mНачинается спам словами...\033[0m")
    for _ in range(5):
        for w in spam_words:
            sys.stdout.write(f"{w} ")
            sys.stdout.flush()
            time.sleep(0.02)
        print()
    print("\n\033[92mСпам завершён.\033[0m")

    base_path = "data"
    html_files = [os.path.join(base_path, f"{i}.html") for i in range(1, 4)]

    missing = [f for f in html_files if not os.path.isfile(f)]
    if missing:
        print(f"\033[91mОшибка: следующие файлы не найдены: {', '.join(missing)}\033[0m")
        print("Убедитесь, что папка 'data' существует и в ней лежат файлы 1.html, 2.html, 3.html")
        input("\nНажмите Enter, чтобы продолжить...")
        return

    print("\n\033[93mОткрытие HTML-файлов в браузере...\033[0m")
    for i, file_path in enumerate(html_files, 1):
        print(f"Открываю {i}.html...")
        webbrowser.open(f"file://{os.path.abspath(file_path)}")
        time.sleep(1.5)

    print("\n\033[93mФайлы открыты. Через 5 секунд браузеры будут автоматически закрыты.\033[0m")
    time.sleep(5)

    if os.name == 'nt':
        browsers = ["chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe"]
        killed = 0
        for proc in browsers:
            try:
                subprocess.run(f"taskkill /f /im {proc}", shell=True, capture_output=True)
                killed += 1
            except:
                pass
        print(f"\033[92mЗавершены процессы браузеров (попытка закрыть {killed} процессов).\033[0m")
    else:
        print("\033[93mАвтоматическое закрытие браузеров поддерживается только в Windows.\033[0m")
        print("Пожалуйста, закройте вкладки браузера вручную.")

    print("\n\033[92mОперация завершена.\033[0m")
    input("\nНажмите Enter, чтобы продолжить...")

def show_menu():
    menu_items = [
        ("IP address information", "1"),
        ("Email address information", "2"),
        ("Phone number information", "3"),
        ("Hosts Search", "4"),
        ("Exploit CVE", "5"),
        ("DNS lookup", "6"),
        ("DNS reverse", "7"),
        ("Email searcher", "8"),
        ("Spam with words + open HTML", "9"),
        ("Выход из программы", "10")
    ]
    width = 40
    border_char = "─"
    corner_tl = "┌"
    corner_tr = "┐"
    corner_bl = "└"
    corner_br = "┘"
    vertical = "│"
    top_line = corner_tl + border_char * (width + 2) + corner_tr
    bottom_line = corner_bl + border_char * (width + 2) + corner_br

    print("\033[96m" + top_line + "\033[0m")
    title = " ДОСТУПНЫЕ ФУНКЦИИ "
    print(f"\033[96m{vertical}\033[0m {title.center(width + 1)}\033[96m{vertical}\033[0m")
    print("\033[96m" + vertical + border_char * (width + 2) + vertical + "\033[0m")
    for item_text, num in menu_items:
        colored_num = f"\033[94m{num}\033[0m"
        line = f"{colored_num}. {item_text}"
        padding = width - len(f"{num}. {item_text}") + 1
        if padding < 0:
            padding = 0
        print(f"\033[96m{vertical}\033[0m {line}{' ' * padding}\033[96m{vertical}\033[0m")
    print("\033[96m" + bottom_line + "\033[0m")

def main():
    print("Добро пожаловать!")
    user_input = input("Введите пароль для входа: ")

    binary_input = ''.join(format(ord(c), '08b') for c in user_input)

    if binary_input == ENCODED_PASSWORD:
        clear_console()
        mining_animation()
        flash_text()
        show_ascii_art()
        while True:
            show_menu()
            choice = input("\033[94mВыберите функцию (1-10): \033[0m").strip()
            if choice == "1":
                ip_information()
            elif choice == "2":
                email_information()
            elif choice == "3":
                phone_number_info()
            elif choice == "4":
                hosts_search()
            elif choice == "5":
                exploit_cve()
            elif choice == "6":
                dns_lookup()
            elif choice == "7":
                dns_reverse()
            elif choice == "8":
                email_searcher()
            elif choice == "9":
                spam_with_html()
            elif choice == "10":
                print("Выход из программы. До свидания!")
                break
            else:
                print("\033[91mФункция в разработке или неверный номер. Попробуйте снова.\033[0m")
                input("\nНажмите Enter, чтобы продолжить...")
            clear_console()
            show_ascii_art()
    else:
        print("\033[91mНеверный пароль. Доступ запрещён.\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()