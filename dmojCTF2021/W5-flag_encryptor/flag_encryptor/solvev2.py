import time
import requests

url = "http://dctf21.larry.science:5000/encrypt"

chars = "bcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
flag = ["c"]

for i in range(0, len(chars)-1):
    key = chars[:i] + "aA" + chars[i+2:]

    res = requests.post(url, data={"key": key})

    t = res.text.strip("'")
    flag.append(t)
    print(t)

    time.sleep(1)

print("".join(flag))
