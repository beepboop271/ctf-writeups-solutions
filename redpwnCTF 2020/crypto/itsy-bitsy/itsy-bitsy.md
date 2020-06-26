# itsy-bitsy

> The itsy-bitsy spider climbed up the water spout...
>
> `nc 2020.redpwnc.tf 31284`

Provided files: `itsy-bitsy.py`<sup id="a1">[1](#f1)</sup>

Prerequisite topics: [Binary, bits, powers of 2](https://www.mathsisfun.com/binary-number-system.html), [Boolean operations like XOR, NOT](http://www.ee.surrey.ac.uk/Projects/CAL/digital-logic/gatesfunc/index.html), [Bitwise operations](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Bitwise_Operators)

## Reading the code

The key things to notice when reading (aside from getting a general understanding of what the functions are doing):

```python
# line 43, main()
for c in flag:
    i = ord(c)
    assert i in range(2**6,2**7)
```

Each character is in the interval [2\*\*6, 2\*\*7), meaning that we're trying to find a sequence containing many characters, all of which are 7 bits long.

```python
# line 52, main()
encrypted_bits = bit_str_xor(flag_bits,random_bits)
```

The string that is printed out of the program is our flag, bitwise XORred with a stream of supposedly random bits as long as our flag. If this was a truly random non-repeating stream, it would be a [one-time pad](https://en.wikipedia.org/wiki/One-time_pad), and we wouldn't be able to solve it. However...

```python
# line 47, main()
i,j = recv_input()
lb = 2**i
ub = 2**j - 1
n = len(flag_bits)
random_bits = generate_random_bits(lb,ub,n)
```

The random bits this function generates are not actually truly random. It repeatedly generates numbers in the interval [`lb`, `ub`] until `n` bits have been produced. The key to solving this problem lies in the fact that all numbers between `2**n` and `(2**(n+1)) - 1` (inclusive) are all `n+1` bits long. Example: `2**5 = 10 0000` and `2**6 - 1 = 11 1111`. Notice that the first bit is `1`. Of course, *every possible random number in this range will have the first bit as `1`.*

## Reasoning

If we can predictably produce a `1` in the random stream, that means we can solve for the original bit from the XOR operation, as `b XOR 1 = 0` means that `b` must be `1`, and `b XOR 1 = 1` means that `b` must be `0`. For each bit in the random stream that we know to be `1`, the corresponding flag bit will be equal to the NOT of the corresponding ciphertext bit.

Then, the question is how to produce a `1` bit for each possible bit in the flag.
> all numbers between `2**n` and `(2**(n+1)) - 1` (inclusive) are all `n+1` bits long

If the first bit of our random number is `1`, and we can create random numbers of any length `n` just by inputting `i = n-1` and `j = n`, that means we can place a `1` almost<sup id="a2">[2](#f2)</sup> anywhere in the stream. By choosing our `i` and `j` values.

Examples:

```text
i = 3, j = 4  =>  [8, 15]  =>  n = 4
all possible random numbers:
1000  1001  1010  1011
1100  1101  1110  1111
known rand bits: 1...1...1...1...1...1...

i = 4, j = 5  =>  [16, 31]  =>  n = 5
all possible random numbers:
10000  10001  10010  10011  10100  10101
10110  10111  11000  11001  11010  11011
11100  11101  11110  11111
known rand bits: 1....1....1....1....1....
```

## Solution

As quickly as possible, it's basically the [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes) but instead of finding primes and filling in multiples of the prime, it's finding known `1` bits and filling in multiples (because the known `1`s repeat).

To find the flag, we need to repeatedly interact with the program to get the ciphertext with our known `1` bit placed in each position. To do this, I will use [socket](https://docs.python.org/3/library/socket.html), part of the Python standard library. Create a socket with `sock = socket.socket()`, connect to the program using information from the netcat command: `sock.connect(("2020.redpwnc.tf", 31284))`, then use `sock.recv(n)` to wait for a message and accept up to `n` bytes, as well as `sock.send(bytes)` to send information.

Running the netcat command in a shell once just to see the output, we find that the ciphertext, and thus the flag, is 301 bits long.

We could just continually increment a counter, and make requests with `i=1,j=2`; `i=2,j=3`; `i=3,j=4`; `i=4,j=5`; `...`; `i=300,j=301`. However, I don't like that because it is unoptimal. Since we know the guaranteed `1` bit will regularly repeat, we only need to make requests for patterns with prime lengths, filling in the composite numbers with the repeated known `1`s.

For each request we make, we just need to find what the ciphertext is at each of our known `1` bits, then record the opposite of the ciphertext's bit. Bit by bit, we can fill in the flag.

---

<b id="f1">1</b> For those unaware, the import `Crypto` comes from the package [pycryptodome](https://pypi.org/project/pycryptodome/) [↩](#a1)

<b id="f2">2</b> The code restricts `i > 0` so that we can't just input `i = 0 j = 1` and produce a string of only `1`. This means that the second bit of the flag is not retrievable, because if we wanted the beginning of our random number (our guaranteed `1` bit) to land on the second bit, we'd need a 1 bit number just before it, which isn't possible. However, this isn't important, as we can already fill in `flag{` which gives us the first `7*5 = 35` bits. [↩](#a2)
