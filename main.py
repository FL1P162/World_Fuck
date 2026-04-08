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
import webbrowser
import dns.reversename
import dns.resolver
import phonenumbers


# Check for dnspython
try:
    import dns.resolver
    import dns.reversename
except ImportError:
    print("\033[91m[ERROR] Module 'dnspython' not found.\033[0m")
    print("Install it using: pip install dnspython")
    sys.exit(1)

try:
    import phonenumbers
    from phonenumbers import carrier, geocoder, timezone
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False

# Global flag to skip splash screens
skip_flag = False

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_skip():
    """Thread function to wait for Enter press."""
    global skip_flag
    input()
    skip_flag = True

def mining_animation():
    global skip_flag
    current = 0.04
    end = 0.18
    step = 0.01
    print("\033[91mWARNING: Mining start, stay on your PC\033[0m")
    print("(Press Enter to skip)\n")
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
    print("\033[91mPress Enter to skip the text splash screen...\033[0m")
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
        input("\nPress Enter to continue...")
    clear_console()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Could not determine IP"

def run_script(script_path):
    """Run an external Python script and output errors if file not found."""
    try:
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\033[91mError executing script {script_path}: {e}\033[0m")
    except FileNotFoundError:
        print(f"\033[91mScript {script_path} not found.\033[0m")
        print("Make sure the 'data' folder exists and contains the required files.")

def ip_information():
    """
    Submenu with two columns in a blue frame (same style as main menu):
    - Left: Telegram bots (links to bots)
    - Right: .py program (info about Python scripts)
    """
    while True:
        clear_console()
        show_ascii_art()

        left_width = 40
        right_width = 35
        color = "\033[96m"
        reset = "\033[0m"

        corner_tl = "┌"
        corner_tr = "┐"
        corner_bl = "└"
        corner_br = "┘"
        vertical = "│"
        border_char = "─"

        def make_line(left_text, right_text, is_top=False, is_bottom=False):
            if is_top:
                left = corner_tl + border_char * (left_width + 2) + corner_tr
            elif is_bottom:
                left = corner_bl + border_char * (left_width + 2) + corner_br
            else:
                left_text_filled = left_text.ljust(left_width)
                left = f"{vertical} {left_text_filled} {vertical}"
            if is_top:
                right = corner_tl + border_char * (right_width + 2) + corner_tr
            elif is_bottom:
                right = corner_bl + border_char * (right_width + 2) + corner_br
            else:
                right_text_filled = right_text.ljust(right_width)
                right = f"{vertical} {right_text_filled} {vertical}"
            return f"{color}{left}{reset}  {color}{right}{reset}"

        print(make_line("", "", is_top=True))
        print(make_line(" Telegram bots ", " .py program "))
        print(make_line("", ""))
        left_items = [
            "1. Sherlock (Telegram bot)",
            "2. 2ip whois",
            "0. Back to main menu"
        ]
        right_items = [
            "In development...",
            "Python scripts",
            "will be added later"
        ]
        max_rows = max(len(left_items), len(right_items))
        for i in range(max_rows):
            left_txt = left_items[i] if i < len(left_items) else ""
            right_txt = right_items[i] if i < len(right_items) else ""
            print(make_line(left_txt, right_txt))
        print(make_line("", "", is_bottom=True))

        choice = input(f"\n{color}Select a number from the left menu (0-2): {reset}").strip()
        if choice == "1":
            webbrowser.open("https://t.me/He_rlokbot?start=_ref_85i7qn35Y_FtiF66U6T")
            print(f"{color}Opened Telegram bot Sherlock.{reset}")
            input("\nPress Enter to continue...")
        elif choice == "2":
            webbrowser.open("https://2ip.ru/whois/")
            print(f"{color}Opened 2ip whois service.{reset}")
            input("\nPress Enter to continue...")
        elif choice == "0":
            break
        else:
            print(f"{color}Invalid choice. Try again.{reset}")
            input("\nPress Enter...")

def email_information():
    print("\n=== Email Address Information ===")
    run_script("data/emailsearch.py")
    input("\nPress Enter to continue...")

def phone_number_info():
    print("\n=== Phone Number Information ===")
    run_script("data/phonesearch.py")
    input("\nPress Enter to continue...")

def hosts_search():
    print("\n=== Hosts Search ===")
    run_script("data/hostssearch.py")
    input("\nPress Enter to continue...")

def exploit_cve():
    print("\n=== Exploit CVE ===")
    cve_id = input("Enter CVE identifier (e.g. CVE-2021-44228): ").strip().upper()
    if not re.match(r'CVE-\d{4}-\d{4,}', cve_id):
        print("Invalid CVE format. Example: CVE-2021-44228")
        input("\nPress Enter to continue...")
        return
    try:
        url = f"https://cve.circl.lu/api/cve/{cve_id}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'id' in data:
                print(f"ID: {data['id']}")
                print(f"Description: {data.get('summary', 'No description')[:500]}...")
                print(f"CVSS v2: {data.get('cvss', 'not specified')}")
                print(f"Publication date: {data.get('Published', 'unknown')}")
            else:
                print("CVE information not found.")
        else:
            print("Error querying API.")
    except Exception as e:
        print(f"Error: {e}")
    input("\nPress Enter to continue...")

def dns_lookup():
    print("\n=== DNS Lookup ===")
    domain = input("Enter domain: ").strip()
    record_types = ['A', 'AAAA', 'MX', 'TXT']
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            print(f"\n{rtype} records:")
            for ans in answers:
                print(f"  {ans}")
        except dns.resolver.NoAnswer:
            print(f"\n{rtype} records: none")
        except Exception as e:
            print(f"\n{rtype} records: error - {e}")
    input("\nPress Enter to continue...")

def dns_reverse():
    print("\n=== DNS Reverse ===")
    ip = input("Enter IP address: ").strip()
    try:
        rev_name = dns.reversename.from_address(ip)
        ptr = dns.resolver.resolve(rev_name, "PTR")
        print(f"PTR record: {ptr[0]}")
    except Exception as e:
        print(f"Failed to get PTR record: {e}")
    input("\nPress Enter to continue...")

def email_searcher():
    print("\n=== Email Searcher ===")
    print("To search email addresses by domain, the Hunter.io API is used (requires key).")
    api_key = input("Enter your Hunter.io API key (or leave empty for demo): ").strip()
    domain = input("Enter domain: ").strip()
    if not api_key:
        print("Demo mode: search impossible without API key.")
        print("Register at hunter.io and get a free key.")
    else:
        try:
            url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                emails = data.get('data', {}).get('emails', [])
                if emails:
                    print(f"Found {len(emails)} email addresses:")
                    for e in emails:
                        print(f"  {e['value']} (source: {e.get('sources', [{}])[0].get('domain', 'unknown')})")
                else:
                    print("No email addresses found.")
            else:
                print(f"API error: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
    input("\nPress Enter to continue...")

def telegram_tools():
    """
    Telegram Tools: open user profile, search channels, documentation, etc.
    """
    while True:
        clear_console()
        show_ascii_art()
        print("\n\033[96m=== Telegram Tools ===\033[0m")
        print("1. Open Telegram user profile (by username)")
        print("2. Search channels / chats (tgstat.ru)")
        print("3. Telegram API documentation")
        print("4. Open Telegram Web")
        print("0. Back to main menu")
        
        choice = input("\n\033[94mSelect an option (0-4): \033[0m").strip()
        
        if choice == "1":
            username = input("Enter Telegram username (without @): ").strip()
            if username:
                url = f"https://t.me/{username}"
                webbrowser.open(url)
                print(f"\033[92mOpened profile: {url}\033[0m")
            else:
                print("\033[91mNo username entered.\033[0m")
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            webbrowser.open("https://tgstat.ru/search")
            print("\033[92mOpened tgstat.ru search for channels/chats.\033[0m")
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            webbrowser.open("https://core.telegram.org/api")
            print("\033[92mOpened Telegram API documentation.\033[0m")
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            webbrowser.open("https://web.telegram.org")
            print("\033[92mOpened Telegram Web.\033[0m")
            input("\nPress Enter to continue...")
        
        elif choice == "0":
            break
        
        else:
            print("\033[91mInvalid choice. Try again.\033[0m")
            input("\nPress Enter...")

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
        ("Telegram Tools", "9"),
        ("Exit program", "10")
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
    title = " AVAILABLE FUNCTIONS "
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
    clear_console()
    mining_animation()
    flash_text()
    show_ascii_art()
    while True:
        show_menu()
        choice = input("\033[94mSelect function (1-10): \033[0m").strip()
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
            telegram_tools()
        elif choice == "10":
            print("Exiting program. Goodbye!")
            break
        else:
            print("\033[91mFunction in development or invalid number. Try again.\033[0m")
            input("\nPress Enter to continue...")
        clear_console()
        show_ascii_art()

if __name__ == "__main__":
    main()
