import collections
import subprocess
from hachoir.stream import FileInputStream
from hachoir.parser import guessParser, archive

# 1. process the zip file and extract the data (a Deflate stream) for each file
parser = guessParser(FileInputStream("challenge.zip"))
# ignore stuff like zip central directory
files = [entry for entry in parser if type(entry) == archive.zip.FileEntry]
# compressed_data is the last field in the file entry, so index -1
streams = [list(file)[-1].value for file in files]

# 2. use infgen to decode the dynamic huffman tree in each stream
info = []
for stream in streams:
    # https://github.com/madler/infgen
    p = subprocess.run("./infgen", input=stream, capture_output=True)
    info.append(p.stdout.decode())

# 3. copy the code given in the Deflate RFC to rebuild the huffman tree
trees = []
for file in info:
    # ignore all the other infgen output
    lines = [line for line in file.split("\n") if line.startswith("litlen")]

    # litlen 10 7
    # litlen 32 3
    # litlen 33 12
    # ...
    # -> [(10, 7), (32, 3), (33, 12), ...]
    litlens = [tuple(map(int, line.split()[1:])) for line in lines]

    max_bits = max(x[1] for x in litlens)

    # https://datatracker.ietf.org/doc/html/rfc1951#page-7
    bl_count = [0]*(max_bits+1)
    for literal, length in litlens:
        bl_count[length] += 1

    code = 0
    next_code = [0]*(max_bits+1)
    for bits in range(1, max_bits+1):
        code = (code + bl_count[bits-1]) << 1
        next_code[bits] = code

    tree = [0]*300
    for literal, length in litlens:
        tree[literal] = next_code[length]
        next_code[length] += 1

    trees.append(tree)

    # print(collections.Counter(x[1] for x in litlens))
    # print(len(litlens))
    # print(ord("E") in set(x[0] for x in litlens))
    # print(bin(tree[ord("E")])[2:].zfill(8))

# 4. get the flag by reversing the bits of the huffman code for "E" in each file
flag = []
for tree in trees:
    code = bin(tree[ord("E")])[2:].zfill(8)
    flag.append(chr(int(code[::-1], 2)))
print("".join(flag))
# CTF{!-!OLE-E-COM!7RESSION}
