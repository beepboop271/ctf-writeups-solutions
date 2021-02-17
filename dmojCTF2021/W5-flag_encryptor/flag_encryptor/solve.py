import time
import requests

chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&"
flag = ["c"]

for i in range(1, len(chars)):
    key = chars[:i] + "A" + chars[i+1:]

    res = requests.post("http://dctf21.larry.science:5000/encrypt", data={"key": key})

    t = res.text.strip("'")
    flag.append(t)
    print(t)
    time.sleep(1)

print("".join(flag))



#flag = "ctf{00000000000000000000000000000000000000}"
flag = "ctf{l4ngu4g3s_4r3_w31rd_s0m3t1m3s_3b234_ae}"
def enc(key):
    key = key.upper()
    
    mapping = {}
    freq = {}

    i = 0
    for flag_ch in flag:
        key_ch = key[i]

        mapping[ord(key_ch)] = flag_ch

        if flag_ch in freq:
            freq[flag_ch] += 1
        else:
            freq[flag_ch] = 1

        i += 1

    output = []

    for i in range(len(key)):
        key_ord = ord(key[i])
        flag_ch = mapping[key_ord]

        output.append(hash(str(ord(flag_ch) * freq[flag_ch]) + flag_ch + key[i]))

        if freq[flag_ch] - 1 == 0:
            del freq[flag_ch]
        else:
            freq[flag_ch] -= 1

    return output

key = "abcdefghijklmnopqrstuvwxyz0123456789!@#A%^&"
for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_":
    flag = flag[:39] + c + flag[40:]
    try:
        print(c, enc(key))
    except KeyError as e:
        print(c, e)
