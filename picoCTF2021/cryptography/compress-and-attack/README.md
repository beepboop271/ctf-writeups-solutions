# Compress and Attack

picoCTF 2021 - Cryptography - 130 points

> Your goal is to find the flag.
>
> Hints:
>
> - The flag only contains uppercase and lowercase letters, underscores, and braces (curly brackets)

Provided file: `compress_and_attack.py`

---

If we look at the provided server script, which is rather short, we can see what is happening when we connect to the challenge.

```py
def main():
    while True:
        usr_input = input("Enter your text to be encrypted: ")
        compressed_text = compress(flag + usr_input)
        encrypted = encrypt(compressed_text)

        nonce = encrypted[:8]
        encrypted_text =  encrypted[8:]
        print(nonce)
        print(encrypted_text)
        print(len(encrypted_text))
```

We can repeatedly give the server text. This text is concatenated with the flag, compressed, and the resulting bytes are then sent through a cipher.

```py
def encrypt(plaintext):
    secret = os.urandom(32)
    cipher = Salsa20.new(key=secret)
    return cipher.nonce + cipher.encrypt(plaintext)
```

The cipher is something called Salsa20, imported from pycryptodome with `from Crypto.Cipher import Salsa20`. The key is generated with `os.urandom`. This doesn't seem like a feasible way to attack the challenge, because a trusted library is being used in a pretty straightforward way, and the random number is not insecure in any way.

Essentially, the fact that this `encrypt` function is very simple and relies entirely on libraries shows that there's no weird "I implemented my own ___ and I'm sure it's completely secure" sort of vulnerability.

On the other hand, the `compress` function is more interesting.

```py
def compress(text):
    return zlib.compress(bytes(text.encode("utf-8")))
```

There's nothing wrong with this compression function: it just uses zlib. However, what matters is the data being compressed.

```py
usr_input = input("Enter your text to be encrypted: ")
compressed_text = compress(flag + usr_input)
encrypted = encrypt(compressed_text)
```

Our input is concatenated to the flag first. Since the library is zlib, the Deflate compression algorithm is being used. The way that the data is compressed is:

1. Duplicate strings close to each other in the data are deduped by inserting a reference. For example, `picoCTF{hello}abcdpicoCTF{hello}` repeats the string `picoCTF{hello}`, so it would be compressed into the following instructions for the computer: "First, write the string `picoCTF{hello}abcd`. Then, go back 18 bytes and copy the next 14 bytes."
2. Huffman coding is used to map the 8 bit long ASCII bytes into shorter codes. For example, if a byte like `a` is used more frequently than other values, it would be more efficient to give a short bit code like `101` compared to the `01100001` in ASCII.

[More info about Deflate](https://zlib.net/feldspar.html).

The challenge server even hints us towards what we need to pay attention to:

```py
print(nonce)
print(encrypted_text)
print(len(encrypted_text))
```

Why would it give us the length of the encrypted text if we could just read the previous line and find the length? Clearly we need to pay attention at the length of the output. The solution here seems to be that the deduplication process will produce a shorter compressed text when our own user input is identical to the flag, because the data compressed is `compress(flag + usr_input)`.

Another useful point of information to know is about the Salsa20 cipher being used. If we look at the [pycryptodome docs](https://pycryptodome.readthedocs.io/en/latest/src/cipher/cipher.html#symmetric-ciphers), here's what we see:

> **Symmetric ciphers**
>
> There are two types of symmetric ciphers:
>
> - **Stream ciphers**: the most natural kind of ciphers: they encrypt data one byte at a time. See [ChaCha20 and XChaCha20](https://pycryptodome.readthedocs.io/en/latest/src/cipher/chacha20.html) and [Salsa20](https://pycryptodome.readthedocs.io/en/latest/src/cipher/salsa20.html).
> - **Block ciphers**: ciphers that can only operate on a fixed amount of data. The most important block cipher is [AES](https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html), which has a block size of 128 bits (16 bytes).

The cipher used is a stream cipher, not a block cipher. This means that when the input to the cipher changes in length by a single byte, we will see a change in length by a single byte in the resulting ciphertext.

Block ciphers will always output a multiple of their block size, no matter what. Here's a concrete example, with a hypothetical stream and block cipher. The block cipher has a block size of 8 bytes. When the input is under 8 bytes long, the output will still be 8 bytes. Once it goes over, the output will suddenly be 16 bytes.

Stream||Block||
-|-|-|-
Input|Output|Input|Output
`aaaaa`|`12345`|`aaaaa`|`12345678`
`aaaaaa`|`123456`|`aaaaaa`|`23456789`
`aaaaaaaaa`|`123456789`|`aaaaaaaaa`|`1234567823456789`

## Solution

Starting with the flag as `picoCTF{`, we'll send our current flag guess + one extra character, and see how long the encrypted data is. Repeating this for every possible character (`picoCTF{a`, `picoCTF{b`, etc.) *should* give us a single character for which the compressed data is shorter. We will add this to our flag guess and brute force each character one by one.

According to the problem statement, only letters (upper and lower), underscores, and curly brackets are allowed. This is 55 characters. If we assume the flag is around 40 characters long, we'd only need to brute force 55\*40 = 2200 times. This is very small, so we'll go with it.

In addition, the server runs an infinite loop asking us for text to encrypt. This means we only need to open one connection, so we don't need to wait between attempts to avoid spamming the server with new connections.

The natural way to write the script might be something like:

1. Send `picoCTF{a\n`
2. Receive the length
3. Send `picoCTF{b\n`
4. Receive the length
5. etc.

Though this is what would happen if you were manually interacting with the server, this is incredibly inefficient, because we have to wait for network latency between every single brute force attempt. What we can do is send the input all at once, and then read the data back one by one, like so:

1. Send `picoCTF{a\npicoCTF{b\npicoCTF{c\npicoCTF{d`...
2. Receive the length for `picoCTF{a`
3. Receive the length for `picoCTF{b`
4. Receive the length for `picoCTF{c`
5. etc.

```py
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
    # which is why the length is put in the first element, we
    # want the shortest length

    # print(sorted(lengths))
    guess += min(lengths)[1]
    print(guess)
```

```txt
picoCTF{sheriff_you_solved_the_crime}
```

Note that the script will start looping the flag (`picoCTF{sheriff_you_solved_the_crime}picoCTF{sheriff_yo`...), because this would still be deduplicated and thus shorter.
