#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import os
import requests
from typing import Dict, Optional, List, Any

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_console()

# ----------------------------------------------------------------------
# ANSI для Windows
# ----------------------------------------------------------------------
def enable_ansi() -> None:
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

# ----------------------------------------------------------------------
# Градиентный ASCII-арт
# ----------------------------------------------------------------------
def print_gradient_ascii(ascii_art: str) -> None:
    lines = ascii_art.splitlines()
    if not lines:
        return
    num_lines = len(lines)
    for idx, line in enumerate(lines):
        ratio = idx / (num_lines - 1) if num_lines > 1 else 0.0
        color_code = int(52 + ratio * (196 - 52))
        print(f"\033[38;5;{color_code}m{line}\033[0m")

# ----------------------------------------------------------------------
# Валидация email и домена
# ----------------------------------------------------------------------
def is_valid_domain(domain: str) -> bool:
    if len(domain) > 253:
        return False
    labels = domain.split('.')
    for label in labels:
        if len(label) > 63 or not label:
            return False
    return True

def parse_email(email: str) -> Optional[Dict[str, str]]:
    pattern = r'^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$'
    match = re.match(pattern, email)
    if not match:
        return None
    domain = match.group(1)
    if not is_valid_domain(domain):
        return None
    local, domain = email.split('@', 1)
    return {'local': local, 'domain': domain}

# ----------------------------------------------------------------------
# MX через DNS-over-HTTPS (Google)
# ----------------------------------------------------------------------
def get_mx_records(domain: str) -> List[str]:
    url = f"https://dns.google/resolve?name={domain}&type=MX"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        mx_list = []
        for answer in data.get('Answer', []):
            if answer.get('type') == 15:
                mx_data = answer.get('data', '')
                mx_list.append(mx_data.rstrip('.'))
        if not mx_list:
            return ["MX-записи не найдены"]
        return mx_list
    except Exception as e:
        return [f"Ошибка получения MX: {str(e)}"]

# ----------------------------------------------------------------------
# RDAP (WHOIS-замена) – без дополнительных библиотек
# ----------------------------------------------------------------------
def get_domain_info_via_rdap(domain: str) -> Dict[str, Any]:
    url = f"https://rdap.org/domain/{domain}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return {'error': f'RDAP ответил {resp.status_code}'}
        data = resp.json()
        
        # Извлекаем нужные поля
        info = {}
        # Регистратор
        entities = data.get('entities', [])
        registrar = None
        for ent in entities:
            if ent.get('roles') and 'registrar' in ent['roles']:
                registrar = ent.get('vcardArray', [None, {}])[1].get('fn', [None])[0]
                break
        info['registrar'] = registrar or data.get('registrar', 'н/д')
        
        # Даты
        events = data.get('events', [])
        creation = None
        expiration = None
        for ev in events:
            if ev.get('eventAction') == 'registration':
                creation = ev.get('eventDate')
            if ev.get('eventAction') == 'expiration':
                expiration = ev.get('eventDate')
        info['creation_date'] = creation
        info['expiration_date'] = expiration
        
        # NS
        nameservers = data.get('nameservers', [])
        info['name_servers'] = [ns.get('ldhName') for ns in nameservers if ns.get('ldhName')]
        
        # Организация (из vcard владельца)
        org = None
        for ent in entities:
            if ent.get('roles') and 'registrant' in ent['roles']:
                vcard = ent.get('vcardArray', [None, {}])[1]
                org = vcard.get('org', [None])[0]
                break
        info['org'] = org or 'н/д'
        
        # Страна (также из vcard)
        country = None
        for ent in entities:
            if ent.get('roles') and 'registrant' in ent['roles']:
                vcard = ent.get('vcardArray', [None, {}])[1]
                adr = vcard.get('adr', [None, {}])[0]
                if adr and isinstance(adr, list) and len(adr) > 5:
                    country = adr[5]
                break
        info['country'] = country or 'н/д'
        
        return info
    except Exception as e:
        return {'error': str(e)}

# ----------------------------------------------------------------------
# HIBP (остаётся)
# ----------------------------------------------------------------------
def check_hibp(email: str, api_key: Optional[str] = None) -> Optional[Dict]:
    if not api_key:
        return None
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {'hibp-api-key': api_key, 'User-Agent': 'EmailInfoTool/1.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            breaches = resp.json()
            return {'breached': True, 'breaches': [b['Name'] for b in breaches]}
        elif resp.status_code == 404:
            return {'breached': False, 'breaches': []}
        else:
            return {'error': f"HTTP {resp.status_code}"}
    except Exception as e:
        return {'error': str(e)}

# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main():
    enable_ansi()
    ascii_art = r"""
 __      __            .__       .___ ___________             __    
/  \    /  \___________|  |    __| _/ \_   _____/_ __   ____ |  | __
\   \/\/   /  _ \_  __ \  |   / __ |   |    __)|  |  \_/ ___\|  |/ /
 \        (  <_> )  | \/  |__/ /_/ |   |     \ |  |  /\  \___|    < 
  \__/\  / \____/|__|  |____/\____ |   \___  / |____/  \___  >__|_ \
       \/                         \/       \/              \/     \/
"""
    print_gradient_ascii(ascii_art)
    print("\n" + "=" * 60)

    email_input = input("Введите email-адрес: ").strip().lower()
    if not email_input:
        print("Ошибка: пустой ввод.")
        return

    email_parts = parse_email(email_input)
    if not email_parts:
        print("❌ Неверный формат email или слишком длинный домен.")
        return

    domain = email_parts['domain']
    print(f"\n📧 Email: {email_input}")
    print(f"🌐 Домен: {domain}")
    print("=" * 60)

    # 1. MX записи
    print("\n📬 MX-записи домена (через Google DNS):")
    mx_records = get_mx_records(domain)
    for mx in mx_records:
        print(f"   {mx}")

    # 2. RDAP информация
    print("\n📄 Информация о домене (RDAP):")
    rdap_data = get_domain_info_via_rdap(domain)
    if 'error' in rdap_data:
        print(f"   ❌ Ошибка: {rdap_data['error']}")
    else:
        print(f"   Регистратор: {rdap_data.get('registrar', 'н/д')}")
        print(f"   Организация: {rdap_data.get('org', 'н/д')}")
        print(f"   Страна:      {rdap_data.get('country', 'н/д')}")
        print(f"   Дата создания: {rdap_data.get('creation_date', 'н/д')}")
        print(f"   Истекает:      {rdap_data.get('expiration_date', 'н/д')}")
        ns = rdap_data.get('name_servers')
        if ns:
            ns_str = ', '.join(ns[:3]) + ('...' if len(ns) > 3 else '')
            print(f"   NS-серверы:   {ns_str}")

    # 3. HIBP
    print("\n🔒 Проверка утечек паролей (Have I Been Pwned):")
    api_key = input("   Введите API ключ HIBP (оставьте пустым для пропуска): ").strip()
    if api_key:
        hibp_result = check_hibp(email_input, api_key)
        if hibp_result is None:
            print("   ⚠️ Проверка не выполнена (нет ключа).")
        elif 'error' in hibp_result:
            print(f"   ❌ Ошибка: {hibp_result['error']}")
        else:
            if hibp_result['breached']:
                breaches = ', '.join(hibp_result['breaches'])
                print(f"   🚨 Email найден в утечках: {breaches}")
            else:
                print("   ✅ Email не обнаружен в известных утечках.")
    else:
        print("   Пропущено (требуется API ключ).")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()