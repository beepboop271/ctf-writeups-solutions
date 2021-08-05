import string
from pwn import *

# > The flag only contains uppercase and lowercase letters,
# > underscores, and braces (curly brackets)
# we will loop through this alphabet to brute force each
# character
alphabet = string.ascii_letters+"_{}"

r = remote("mercury.picoctf.net", 2431)

guess = "picoCTF{"
while 1:
    # "\n".join(["picoCTF{a", "picoCTF{b", "picoCTF{c", ...])
    # use sendline to add a "\n" on the last element
    r.sendline("\n".join([guess+c for c in alphabet]))

    lengths = []
    for c in alphabet:
        r.recvline()
        r.recvline()
        # length of the encrypted data
        length = int(r.recvline())
        lengths.append((length, c))

    # python tuple comparison works like string comparison,
    # sorted by their first element, then by their second, etc.
    # which is why the length is put in the first element,
    # we want the shortest length

    # print(sorted(lengths))
    guess += min(lengths)[1]
    print(guess)
