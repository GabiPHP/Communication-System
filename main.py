import requests
import random
import time
import re
import os
import threading
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

githubURL = "https://raw.githubusercontent.com/GabiPHP/Communication-System/refs/heads/main/main.py"

url = "https://anonimo.chat/"
room = "597697b0fff04abcaa5fe2a95980" # Missing 4 numbers

roomID = ""
ID = {}

stop_flag = False

print("Checking for updates...")
remote = requests.get(url).text.replace("\r\n", "\n").strip()
with open(__file__,"r", encoding="utf-8-sig") as f:
    local = f.read().replace("\r\n", "\n").strip()
if(remote != local):
    open(__file__, "w").write(remote)
print("Updated, Re-Run The File.")


option = input("[1] Create Room | [2] Join Room: ")
username = input("Username: ")

messages = []

def generateID(url):
    session = requests.Session()
    response = session.get(url, verify=False)
    phpsessid = session.cookies.get("PHPSESSID")
    match = re.search(r'const\s+csrf\s*=\s*"([^"]+)"', response.text)
    return { "PHPSESSID": phpsessid, "CSRF": match.group(1) }

def getMessages(url,ID,room):
    cookies = {"PHPSESSID": ID["PHPSESSID"] }
    params = {"id": room}
    response = requests.get(url, params=params, cookies=cookies, verify=False)
    data = response.json()  
    messages_html = data["messages_html"]
    pattern = re.compile(r"\[(.*?) UTC\]\s*(?:<b>(.*?)</b>:)?\s*(.*?)</div>")
    matches = pattern.findall(messages_html)
    return matches

def sendMessage(url,ID,room,message):
    payload = {"message": message, "csrf": ID["CSRF"]}
    cookies = {"PHPSESSID": ID["PHPSESSID"] }
    params = {"id": room} 
    response = requests.post(url, params=params, json=payload, cookies=cookies, verify=False)
    return response
        

if option == "1":
    randomRoom = str(random.randint(1000,9999)) # Re added 4 numbers
    room = room + randomRoom
    ID = generateID(url+"chat")

    params = {"id": room }
    payload = {"message": username, "csrf": ID["CSRF"]}
    cookies = {"PHPSESSID": ID["PHPSESSID"] }
    response = requests.post(url+"api", params=params, json=payload, cookies=cookies, verify=False)

    print("Created Room:",randomRoom,"Response:",response.text)

if option == "2":
    roomID = input("Room ID: ")
    ID = generateID(url+room+roomID)
    params = {"id": room+roomID }
    payload = {"message": username, "csrf": ID["CSRF"]}
    cookies = {"PHPSESSID": ID["PHPSESSID"] }
    response = requests.post(url+"api", params=params, json=payload, cookies=cookies, verify=False)

    print("Joined Room:",roomID,"Response:",response.text)



def message_loop(): 
    while not stop_flag:
        response = getMessages(url+"api", ID, room + roomID)

        for date, user, message in response:
            user = user if user else "SYSTEM"
            message = message.strip()
            data = {"date": date, "user": user, "message": message}
            if data not in messages:
                messages.append(data)
                print(f"[{date}] {user} : {message}")

        time.sleep(2)


thread = threading.Thread(target=message_loop, daemon=True)
thread.start()

while True:
    msg = input("")
    response = sendMessage(url+"api",ID,room+roomID,msg)
    print(response.text)
