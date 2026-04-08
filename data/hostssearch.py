#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import os
import socket
import requests
from typing import Dict, List, Any, Optional

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
# Проверка, является ли строка IP-адресом
# ----------------------------------------------------------------------
def is_ip_address(s: str) -> bool:
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, s):
        parts = s.split('.')
        return all(0 <= int(p) <= 255 for p in parts)
    return False

# ----------------------------------------------------------------------
# DNS-запросы через Google DoH
# ----------------------------------------------------------------------
def dns_query(domain: str, record_type: str) -> List[str]:
    url = f"https://dns.google/resolve?name={domain}&type={record_type}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        results = []
        for answer in data.get('Answer', []):
            if answer.get('type') == dns_type_to_int(record_type):
                results.append(answer.get('data', '').rstrip('.'))
        return results
    except Exception:
        return []

def dns_type_to_int(typ: str) -> int:
    types = {'A': 1, 'AAAA': 28, 'MX': 15, 'TXT': 16, 'NS': 2, 'CNAME': 5, 'SOA': 6}
    return types.get(typ, 0)

def get_all_dns_records(domain: str) -> Dict[str, List[str]]:
    records = {}
    for typ in ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'SOA']:
        records[typ] = dns_query(domain, typ)
    return records

# ----------------------------------------------------------------------
# WHOIS/RDAP информация о домене
# ----------------------------------------------------------------------
def get_domain_info_via_rdap(domain: str) -> Dict[str, Any]:
    url = f"https://rdap.org/domain/{domain}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return {'error': f'RDAP ответил {resp.status_code}'}
        data = resp.json()
        
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
        
        # Организация владельца
        org = None
        for ent in entities:
            if ent.get('roles') and 'registrant' in ent['roles']:
                vcard = ent.get('vcardArray', [None, {}])[1]
                org = vcard.get('org', [None])[0]
                break
        info['org'] = org or 'н/д'
        
        # Страна
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
# Геолокация IP (через ip-api.com)
# ----------------------------------------------------------------------
def ip_geo(ip: str) -> Dict[str, Any]:
    url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,lat,lon,isp,org,as,query"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('status') == 'success':
            return data
        else:
            return {'error': data.get('message', 'Ошибка геолокации')}
    except Exception as e:
        return {'error': str(e)}

# ----------------------------------------------------------------------
# Проверка по чёрным спискам DNSBL (через dnsbl.info API)
# ----------------------------------------------------------------------
def check_dnsbl(ip: str) -> List[str]:
    """
    Проверяет IP в нескольких популярных DNSBL.
    Используется публичный API dnsbl.info.
    """
    url = f"https://dnsbl.info/api/v1/check?ip={ip}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        blacklists = []
        for bl in data.get('blacklists', []):
            if bl.get('listed'):
                blacklists.append(f"{bl.get('name')} ({bl.get('url')})")
        return blacklists
    except Exception:
        return ["Ошибка при проверке DNSBL"]

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

    host = input("Введите домен или IP-адрес: ").strip().lower()
    if not host:
        print("Ошибка: пустой ввод.")
        return

    print(f"\n🔍 Хост: {host}")
    print("=" * 60)

    # Определяем, IP это или домен
    is_ip = is_ip_address(host)
    domain = host if not is_ip else None
    ip_addr = host if is_ip else None

    # Если домен – разрешаем в IP
    if domain:
        try:
            ip_addr = socket.gethostbyname(domain)
            print(f"\n🌐 IP-адрес домена: {ip_addr}")
        except socket.gaierror:
            ip_addr = None
            print("\n⚠️ Не удалось разрешить домен в IP.")

    # 1. DNS-записи (только для доменов)
    if domain:
        print("\n📡 DNS-записи:")
        records = get_all_dns_records(domain)
        for typ, values in records.items():
            if values:
                print(f"   {typ}:")
                for v in values:
                    print(f"      {v}")

    # 2. WHOIS/RDAP для домена
    if domain:
        print("\n📄 Информация о домене (RDAP):")
        rdap = get_domain_info_via_rdap(domain)
        if 'error' in rdap:
            print(f"   ❌ Ошибка: {rdap['error']}")
        else:
            print(f"   Регистратор: {rdap.get('registrar', 'н/д')}")
            print(f"   Организация: {rdap.get('org', 'н/д')}")
            print(f"   Страна:      {rdap.get('country', 'н/д')}")
            print(f"   Дата создания: {rdap.get('creation_date', 'н/д')}")
            print(f"   Истекает:      {rdap.get('expiration_date', 'н/д')}")
            ns = rdap.get('name_servers')
            if ns:
                ns_str = ', '.join(ns[:3]) + ('...' if len(ns) > 3 else '')
                print(f"   NS-серверы:   {ns_str}")

    # 3. Геолокация IP
    if ip_addr:
        print("\n🗺️ Геолокация IP:")
        geo = ip_geo(ip_addr)
        if 'error' in geo:
            print(f"   ❌ Ошибка: {geo['error']}")
        else:
            print(f"   Страна:    {geo.get('country', 'н/д')}")
            print(f"   Регион:    {geo.get('regionName', 'н/д')}")
            print(f"   Город:     {geo.get('city', 'н/д')}")
            print(f"   Почтовый индекс: {geo.get('zip', 'н/д')}")
            print(f"   Координаты: {geo.get('lat', 'н/д')}, {geo.get('lon', 'н/д')}")
            print(f"   Провайдер: {geo.get('isp', 'н/д')}")
            print(f"   Организация: {geo.get('org', 'н/д')}")
            print(f"   AS:        {geo.get('as', 'н/д')}")

    # 4. Проверка по чёрным спискам (только для IP)
    if ip_addr:
        print("\n🚫 Чёрные списки DNSBL:")
        blacklists = check_dnsbl(ip_addr)
        if blacklists and blacklists[0] != "Ошибка при проверке DNSBL":
            if blacklists:
                print("   ⚠️ IP обнаружен в следующих списках:")
                for bl in blacklists:
                    print(f"      {bl}")
            else:
                print("   ✅ IP не найден в проверенных чёрных списках.")
        else:
            print(f"   {blacklists[0]}")

    # 5. Поиск в интернете
    print("\n🔎 Поиск в интернете:")
    search_query = host
    if domain and ip_addr:
        search_query = f"{domain} {ip_addr}"
    search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
    print(f"   Откройте ссылку: {search_url}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()