# primimity

> People claim that RSA with two 1024-bit primes is secure. But I trust no one. That's why I use three 1024-bit primes.
>
> I even created my own prime generator to be extra cautious!

Provided files: `primimity.py`<sup id="a1">[1](#f1)</sup>, `primimity-public-key.txt`

Prerequisite topics: [RSA](https://github.com/beepboop271/ctf-writeups-solutions/tree/master/general%20resources/crypto/rsa.md)

## Reading the code

The key thing to notice here and the whole reason why this challenge is possible is as follows:

```python
# line 19
def prime_gen():
    i = getRandomNBitInteger(1024)
    d = getRandomNBitInteger(8)
    for _ in range(d):
        i = find_next_prime(i)
    p = find_next_prime(i)
    d = getRandomNBitInteger(8)
    for _ in range(d):
        i = find_next_prime(i)
    q = find_next_prime(i)
    d = getRandomNBitInteger(8)
    for _ in range(d):
        i = find_next_prime(i)
    r = find_next_prime(i)
    return (p,q,r)
```

The prime generator first creates one random 1024 bit prime. If it created 3 random 1024 bit primes, this challenge would be *quite a bit* harder. However, notice that to find the second and third primes, it just "skips forward" a random number of primes. Specifically, it calls `find_next_prime` between 129 and 256 times, inclusive, to get the next factor of `n` for RSA.

## Reasoning

In normal RSA, using 3 primes `p`, `q`, and `r` works out basically the same as using two (`n = pqr`, `totient(n) = (p-1)*(q-1)*(r-1)`). However...

In the context of 1024 bit prime numbers, a gap of 256 primes doesn't sound like much. As it turns out, there are about 8.99 x 10<sup>307</sup> possible 1024 bit numbers, and we can [estimate](https://math.stackexchange.com/questions/263588/how-many-all-prime-numbers-p-with-length-of-bits-of-p-1024-bits) there to be about 1.26 x 10<sup>305</sup> 1024 bit primes, which means *on average*, there should be a prime about every 713 numbers. This means that even if the maximum gap size is chosen, we could expect a distance of roughly `713*256*2 = 365056` between the three primes, not a lot (relatively).

Given that our 3 prime factors `p`, `q`, and `r` are fairly close to each other, we could say they are all roughly equal, and that `n` is about equal to `p`<sup>`3`</sup>. With this information, this appears to be a "trivially factorable `n`" type of problem.

## Solution

We will try to just brute force factor the public key, by starting from the cube root of `n` and searching for primes in the ascending and descending directions. We know this brute force shouldn't take *too* long because we expect the factors to be within the cube root plus or minus 400000. Once we find two of the primes, we just divide `n` to find the third factor.

After identifying the three factors `p`, `q`, and `r`, we just apply the RSA formulas. `d = inverse(e, (p-1)*(q-1)*(r-1))`, then `m = pow(c, d, n)`<sup id="a2">[2](#f2)</sup>, and we convert to binary and ascii to find the flag.

### An aside

Looking at the factors, we can see that they were 30726, 127770, and -158496 away from the cube root. All below 400000. In addition, I let the script search for all the primes within 520 primes of the cube root, and found the average distance to be around 699, right around our expected average distance.

---

<b id="f1">1</b> For those unaware, the import `Crypto` comes from the package [pycryptodome](https://pypi.org/project/pycryptodome/) [↩](#a1)

<b id="f2">2</b> See [here](https://github.com/beepboop271/ctf-writeups-solutions/tree/master/general%20resources/crypto/rsa.md) for RSA formulas and explanation [↩](#a2)
