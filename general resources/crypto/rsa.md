# RSA

## What is RSA?

RSA is an algorithm used to encrypt messages such that only the intended recipient of a message can read it.

RSA is an [asymmetric encryption algorithm](https://en.wikipedia.org/wiki/Public-key_cryptography), which means that there are two distinct keys created in tandem: one for the sender, and one for the receiver (as opposed to a symmetric algorithm which uses the same key used by both the sender and receiver).

The sender uses a public key for encrypting messages, and the receiver uses a private key to decrypt. The public key's messages can only be decrypted with the exact corresponding private key, and the private key can only decrypt messages encrypted with the exact corresponding public key.

The public key is shared with everyone, so that everyone can send the receiver an encrypted message that only the receiver can read.

The receiver is the only person who can read the messages because they are (hopefully) the only one with the private key.

For example, if a server wants its clients to send it messages that nobody but the server can read, they could create an RSA key pair. The public key would be available to all the clients, and they would keep their own private key. That way, all the clients could encrypt a message with the public key and only the server (assuming they keep the key secret) could decrypt the messages with their private key<sup id="a1">[1](#f1)</sup>.

## Calculating necessary values

RSA involves sending your whole message in one big number. Usually, to send a string, you just concatenate every byte in the message into one very long number, and send that number.

E.g. to send the message `"Hello, World!"`:

```text
Message as string: Hello, World!
Message as bytes : 1001000 1100101 1101100 1101100 1101111 0101100 0100000 1010111 1101111 1110010 1101100 1100100 0100001
Message prepared : 1001000110010111011001101100110111101011000100000101011111011111110010110110011001000100001 (binary)
Message prepared : 1408073740711211456312062497 (decimal)
```

We call this number `m`, for `message` (specifically, plaintext message).

Then, we need to pick 2 random prime numbers, `p` and `q`, and multiply them together to produce `n = pq`. Then, `n` is made publicly available to encrypt messages (public key). The key length (e.g. 1024 bit, 2048 bit) is the number of bits in `n`, so `p` and `q` should be chosen randomly but such that `n` has the desired bit length.

Then, we need to calculate totient(n). In my limited experience with CTFs, beginner RSA problems usually use Euler's totient function, `totient(n) = (p-1)*(q-1)` for two primes. However, there is also Carmichael's totient function, `totient(n) = lcm(p-1, q-1)`<sup id="a2">[2](#f2)</sup>.

We also need a number `e` for the public and private keys that is less than and coprime to `totient(n)`. A value of `e = 65537` is commonly used.

Then, the private key `d` will be equal to `inverse(e, totient(n))`, where `inverse(x, n)`<sup id="a3">[3](#f3)</sup> is the [modular multiplicative inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) of x mod n (`de ≡ 1 (mod totient(n))`).

Essentially what that operation means is solving a value of `d` (pretty sure there are infinite, they all work, so just pick the lowest) in this equation: `de mod totient(n) = 1 mod totient(n)` which is essentially the same as `de mod totient(n) = 1` (the triple bar equals and writing mod in brackets on the right side is just the notation for this, they mean the same thing).

Summary:

- `m = `concatenated binary encoding of the message
- `n = pq` (where p and q are random primes)
- `totient(n)`
  - Euler's `totient(n) = (p-1)*(q-1)`
  - Carmichael's `totient(n) = lcm(p-1, q-1)`<sup id="a4">[4](#f4)</sup>
- `e = 65537` (most commonly, but can be any number less than and coprime to whichever `totient(n)` is used)
- `d = inverse(e, totient(n))`

## Encryption

As mentioned earlier, `n` and `e` are available to everyone as the public key. To encrypt the message `m`, all you need to do is find the number `c = pow(m, e, n)`<sup id="a5">[5](#f5)</sup> (c for "ciphertext").

## Decryption

`p`, `q`, `totient(n)`, and `d` are all kept secret (because knowing any one of them would allow you to decrypt messages), but `d` is the only value used in decrypting. Decryption is as simple as another modular exponent: `m = pow(c, d, n)`. Then, you just need to convert `m` back to binary and recover the original string.

## RSA challenges in CTFs

Since RSA is actually used in the real world for encryption, CTF challenges usually involve some form of RSA crafted with an exploitable flaw.

### Leaked values

`n` and `e` are the only values that are supposed to be known, and a challenge may give you `c`, the encrypted message. If any other value (`p`, `q`, `totient(n)`, `d`) is given, you can ultimately solve for `d` and decrypt the message.

- `d` leak: just decrypt the message, `m = pow(c, d, n)`
- `totient(n)` leak: calculate `d = inverse(e, totient(n))`
- `p` or `q` leak: divide `n` by the known factor to find the other factor. Calculate `totient(n)` (you may need to try using both Euler and Carmichael's functions), then `d`.

### Small values or trivially factorable `n`

A small `n` or `e` can both be exploited.

If `n` is too small, half an hour running an integer factoring calculator might be able to find `p` and `q` for you. Alternatively, there might be some other mistake which allows you to factor `n`. For example, knowing that `n` was made by multiplying many primes instead of just two could mean an easier time factoring, or knowing that `n` was made by very close primes means that `p` and `q` must be close to `sqrt(n)`.

If `e` is too small, say `3`, and `m` is also small, calculating `c = m`<sup>`3`</sup>` mod n` might result in the power `m`<sup>`3`</sup> being smaller than `n`, which means that no mod was applied, and the original message can be recovered just by taking the cube root. In addition, if `e` is too small, and `d` is too small, you could try [Wiener's attack](https://en.wikipedia.org/wiki/Wiener%27s_attack) (just find some implementation in a language of your choice).

[More possible attacks](https://math.boisestate.edu/~liljanab/ISAS/course_materials/AttacksRSA.pdf).

---

<b id="f1">1</b> You might wonder, how can the server securely communicate back to the client, unless the client also has a public and private key? Well, the answer is that, for something like HTTPS, the server and client actually start the conversation by agreeing on one random and unique key to use in a [*symmetric* encryption](https://en.wikipedia.org/wiki/Symmetric-key_algorithm) algorithm like [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) (symmetric encryption meaning that instead of using one key to encrypt and one key to decrypt, the same key is used and kept secret by both the sender and receiver). Once both sides have the same symmetric key, they can continue the conversation by encrypting all their messages with the agreed-upon key. The client can use RSA to securely send the server a symmetric key they generated (RSA works because you only need one-way communcation to send a key, then continue with AES), or instead use [Diffie-Hellman key exchange](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange) to mutually agree on a symmetric key. [See this StackOverflow question for more (note it is a bit old but the concept is there)](https://stackoverflow.com/questions/24747716/how-it-https-secure-cant-anyone-decrypt-the-responses). For information on what algorithms are currently used for key exchange and what algorithms are currently used for encryption/decryption in TLS (used for HTTPS), [see the tables here](https://en.wikipedia.org/wiki/Transport_Layer_Security#Algorithm) [↩](#a1)

<b id="f2">2</b> [For those into number theory, I guess.](https://crypto.stackexchange.com/questions/29591/lcm-versus-phi-in-rsa) [↩](#a2)

<b id="f3">3</b> `inverse(x, n)` from [pycryptodome](https://pypi.org/project/pycryptodome/)'s `Crypto.Util.number` (`from Crypto.Util.number import inverse`) [↩](#a3)

<b id="f4">4</b> Since everything else has Python functions, I might as well provide implementations for this too:

- Python 3.9 (still beta at time of writing)
  - `math.lcm(p-1, q-1)`
- Python >=3.5
  - `(p-1)*(q-1) // math.gcd(p-1, q-1)` (technically should use abs of the first part, but we know `p` and `q` are already positive)
- Other
  - `(p-1)*(q-1) // fractions.gcd(p-1, q-1)` [↩](#a4)

<b id="f5">5</b> The Python builtin function `pow(a, b)` raises `a` to the `b`th power, but actually has a third optional parameter for the modulus. `pow(a, b, n)` computes `a`<sup>`b`</sup>` mod n`. Note: calculating the exponent first and then taking the mod will take a *very long time* because raising a number hundreds of digits long to the power of 65537 will produce a *very big number*. There are efficient algorithms specifically for calculating exponents with mod, which is why the optional third argument exists. [↩](#a5)
