import socket
import time

def flip(bit):
    return "1" if bit == "0" else "0"

known_bits = list("1100110")  # we know "f" is the first char
known_bits.extend(["."]*(301-7))
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163 ,167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293]

for prime in primes:
    with socket.socket() as sock:
        sock.connect(("2020.redpwnc.tf", 31284))
        # call .recv and do nothing with the result because
        # recv will force us to wait until the program is ready.
        # we don't want to input and grab the response too
        # quickly, because sometimes the ciphertext won't be
        # printed by the time we're done recieving
        sock.recv(100)  # Enter i
        sock.send(bytes(f"{prime-1}\n", "ascii"))
        sock.recv(100)  # Enter j
        sock.send(bytes(f"{prime}\n", "ascii"))
        bits = sock.recv(1000).decode().rstrip()[-301:]
        print(bits)

        known_bits[prime] = flip(bits[prime])
        # for some of the primes, 2*prime is already over 301 bits.
        # however, it turns out that if the square of the prime is
        # over our maximum, that means that all of its multiples
        # will have already been counted by lower primes, so only
        # process mutliples if we need to
        if prime*prime < len(bits):
            for n in range(prime*prime, len(bits), prime):
                known_bits[n] = flip(bits[n])
    # i dont like spamming unless it's really necessary
    time.sleep(0.2)
    print("".join(known_bits))

flag = "".join(known_bits)
print("".join(
    [chr(int(flag[i:i+7], 2)) for i in range(0, len(flag), 7)]
))
