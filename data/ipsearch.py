#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import socket
import requests
import os

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_console()

# ----------------------------------------------------------------------
# Включение поддержки ANSI-цветов в Windows
# ----------------------------------------------------------------------
def enable_ansi() -> None:
    """Включает виртуальный терминал для Windows, если это необходимо."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass  # Если не удалось — просто продолжаем


# ----------------------------------------------------------------------
# Вывод ASCII-арта с градиентом от тёмно-красного к ярко-красному
# ----------------------------------------------------------------------
def print_gradient_ascii(ascii_art: str) -> None:
    """
    Печатает многострочный ASCII-арт, раскрашивая каждую строку в свой оттенок красного.
    Используются 256 цветов: от 52 (очень тёмный красный) до 196 (яркий красный).
    """
    lines = ascii_art.splitlines()
    if not lines:
        return
    num_lines = len(lines)
    for idx, line in enumerate(lines):
        # Коэффициент прогресса: 0.0 для первой строки, 1.0 для последней
        ratio = idx / (num_lines - 1) if num_lines > 1 else 0.0
        # Цвет в палитре 256: 52 (тёмный) → 196 (яркий)
        color_code = int(52 + ratio * (196 - 52))
        # Печатаем строку с цветом и сбрасываем форматирование
        print(f"\033[38;5;{color_code}m{line}\033[0m")


# ----------------------------------------------------------------------
# Получение информации об IP через публичное API
# ----------------------------------------------------------------------
def get_ip_info(ip_or_domain: str) -> dict:
    """
    Принимает IP-адрес или доменное имя.
    Возвращает словарь с данными о местоположении, провайдере и т.д.
    В случае ошибки возвращает {'error': '...'}.
    """
    # Пробуем преобразовать домен в IP
    try:
        socket.inet_aton(ip_or_domain)  # если это уже IPv4
    except socket.error:
        try:
            ip_or_domain = socket.gethostbyname(ip_or_domain)
            print(f"[*] Домен разрешён в IP: {ip_or_domain}")
        except socket.gaierror:
            return {"error": "Неверный IP-адрес или доменное имя"}

    # Запрос к ip-api.com (бесплатно, без ключа)
    url = f"http://ip-api.com/json/{ip_or_domain}?fields=status,message,country,regionName,city,zip,lat,lon,isp,org,as,query"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("status") == "success":
            return data
        else:
            return {"error": data.get("message", "Неизвестная ошибка")}
    except Exception as e:
        return {"error": str(e)}


# ----------------------------------------------------------------------
# Главная функция
# ----------------------------------------------------------------------
def main() -> None:
    enable_ansi()

    # ASCII-арт из условия
    ascii_art = r"""
 __      __            .__       .___ ___________             __    
/  \    /  \___________|  |    __| _/ \_   _____/_ __   ____ |  | __
\   \/\/   /  _ \_  __ \  |   / __ |   |    __)|  |  \_/ ___\|  |/ /
 \        (  <_> )  | \/  |__/ /_/ |   |     \ |  |  /\  \___|    < 
  \__/\  / \____/|__|  |____/\____ |   \___  / |____/  \___  >__|_ \
       \/                         \/       \/              \/     \/
"""

    print_gradient_ascii(ascii_art)
    print("\n" + "=" * 50)

    # Ввод IP / домена
    user_input = input("Введите IP-адрес или доменное имя: ").strip()
    if not user_input:
        print("Ошибка: пустой ввод.")
        return

    # Поиск информации
    info = get_ip_info(user_input)
    print("\n" + "=" * 50)

    if "error" in info:
        print(f"❌ Ошибка: {info['error']}")
    else:
        print(f"🌐 IP:        {info.get('query')}")
        print(f"📍 Страна:    {info.get('country')}")
        print(f"🏙️  Регион:    {info.get('regionName')}")
        print(f"🏠 Город:     {info.get('city')}")
        print(f"📮 Почтовый индекс: {info.get('zip')}")
        print(f"🗺️  Координаты: {info.get('lat')}, {info.get('lon')}")
        print(f"🔌 Провайдер: {info.get('isp')}")
        print(f"🏢 Организация: {info.get('org')}")
        print(f"🔢 AS:        {info.get('as')}")

    print("=" * 50)


if __name__ == "__main__":
    main()