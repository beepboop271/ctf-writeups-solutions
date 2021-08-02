# David and the Tree

Google CTF Qualifiers 2021 - Miscellaneous - 29 solves/260 points

> Sometimes, what's more important is not what you have, but what you're missing.

Provided file: `challenge.zip`

## Investigation

The first thing I noticed was that the provided file was a zip file. All challenge attachments in the CTF were provided in zip files, so this challenge gave a zip file (`challenge.zip`) in a zip file (that all challenges have), immediately suggesting that the `challenge.zip` file itself had some significance.

Extracting `challenge.zip` gave 26 `.txt` files, numbered 0 through 25.

Opening `00.txt`, we see some uppercase text with hard line wrapping:

```txt
I


IF YOUTH, THROUGHOUT ALL HISTORY, HAD HAD A CHAMPION TO STAND UP FOR
IT; TO SHOW A DOUBTING WORLD THAT A CHILD CAN THINK; AND, POSSIBLY,
DO IT PRACTICALLY; YOU WOULDN'T CONSTANTLY RUN ACROSS FOLKS TODAY
WHO CLAIM THAT "A CHILD DON'T KNOW ANYTHING." A CHILD'S BRAIN STARTS
FUNCTIONING AT BIRTH; AND HAS, AMONGST ITS MANY INFANT CONVOLUTIONS,
THOUSANDS OF DORMANT ATOMS, INTO WHICH GOD HAS PUT A MYSTIC POSSIBILITY
FOR NOTICING AN ADULT'S ACT, AND FIGURING OUT ITS PURPORT.
```

Searching this text brings up results about a novel, *Gadsby* by Ernest Vincent Wright. Something unique about this text, mentioned in the first sentence of the Wikipedia page, is that the letter `e` is never used, which is interesting.

The first thing I did was check if there were any modifications to the text: do these text files contain a perfect copy of some online text, or have some characters been modified?

The first result on Google for "Gadsby full text" is a [link to Project Gutenberg](https://www.gutenberg.org/ebooks/47342), which presents many formats for the text. The first option is HTML, but it is pretty different from our files. The provided text files use `--` in place of unicode em dashes, and surround words with `_` in place of italics formatting. These differences, in addition to the hard line wrapping (not present in the HTML version), made me continue searching for other versions.

Fortunately, just a few options later, Gutenberg presents a [plain text file](https://www.gutenberg.org/cache/epub/47342/pg47342.txt), which appears to be identical in formatting.

I downloaded a copy, manually deleted the lines at the start and end of the file which were not part of the novel, and converted it to uppercase to match the provided files. At the same time, I also joined the 26 provided files into one.

```python
# full.txt: https://www.gutenberg.org/cache/epub/47342/pg47342.txt
with open("full.txt") as f:
    original = f.read().upper()

chapters = []
for n in range(26):
    with open(f"{str(n).zfill(2)}.txt") as f:
        chapters.append(f.read())

# the file from Gutenberg uses 4 blank lines between chapters
provided = "\n\n\n\n".join(chapters)

print(original == provided)
```

```txt
True
```

Since I knew the only difference between the provided files and the original copy was the casing, I could safely ignore the text, unlike some challenges which encode the flag using differences in files.

## Compressing With Trees

If the text files are meaningless, the only other place to look would be the `challenge.zip` file which I was suspicious of at the start. The challenge name "David and the Tree" tipped me off to what I should investigate next, because trees can be used when compressing something like a zip file, using something called Huffman Coding. Uncompressed bytes are mapped to compressed codes, and something called a Huffman Tree helps to build and decode these mappings. Usually, a custom mapping and tree is made for each piece of data being compressed, to get the most optimal compression amount, and this tree is stored along with the compressed data. I assumed that the flag might be encoded somehow in the Huffman Tree, which should be in the zip file somewhere.

### Huffman Coding Background [[skip]](#zip-file-format)

Suppose we wish to compress the string `"ABAAACABBBAAAACCABBD"`. With ASCII, each character would take up one byte: `A` would be `01000001` for example. One possible way to approach this is to map each letter (byte) to a new compressed code. If the compressed code is shorter than 8 bits, we would successfully shorten the bit length of the string.

Since the value `A` appears so often, we should try to map it to the shortest possible code. Let's say `A` is represented by a single bit, `1`. Now that `A` is given `1`, we can't let any other letter's compressed code start with the bit `1`, because otherwise we wouldn't be able to tell the two codes apart (e.g. if we had the mapping `B` = `11`, is `111` a compressed `AB` or `AAA`?). Since there aren't many short codes we can use, it would make sense to give the most frequent characters the shortest codes, so that we can save the most space. Less frequent characters would thus get longer compressed codes. A possible mapping is:

Character | Frequency | Uncompressed | Compressed
-|-|-|-
A | 10 | `01000001` | `1`
B | 6 | `01000010` | `01`
C | 3 | `01000011` | `001`
D | 1 | `01000100` | `000`

```txt
"ABAAACABBBAAAACCABBD"

Original (160 bits):
01000001 01000010 01000001 01000001 01000001 01000011 01000001
01000010 01000010 01000010 01000001 01000001 01000001 01000001
01000011 01000011 01000001 01000010 01000010 01000100

Compressed (34 bits):
1 01 1 1 1 001 1 01 01 01 1 1 1 1 001 001 1 01 01 000
```

Since none of the compressed codes are a prefix of another (called a prefix-free code), we will always be able to reconstruct the original string. Looking at the start of the compressed code, we see the bit `1`. Since no other code starts with `1`, we know this corresponds to `A`, so we'll write `A` and consume that one bit.

The next few bits are `01111`. The only code that starts with `01` is `B` (because otherwise `B` would be a prefix of the other code), and that also means there will be no code which is just `0` (because `0` is a prefix of `01`), which is why we know it must be a `B`, followed by 3 `A`s. After, we have `0011010101`. Once again, there is no code for `0`, or `00`, and the only code which starts with `001` is `C`. This process can be repeated to reconstruct the original string.

An efficient way to build and decode this mapping uses a Huffman Tree, which is a kind of binary tree.

Each leaf node represents a uncompressed value, such as the letter `A`, or `B`. Then, the compressed codes are stored using the path to leaf from the root. If we let "left" be `0`, and "right" be `1`, the Huffman Tree for our example would look like:

```txt
     Root
     /  \
    x    A (A path: R->right = 1)
   / \
  x   B    (B path: R->left->right = 01)
 / \
D   C      (C path: R->left->left->right = 001)
           (D path: R->left->left->left = 000)
```

The prefix-free property is guaranteed as long as our uncompressed characters stay as leaves, because the only way a code can be a prefix of another is if it is a parent to the other in the tree, and leaves have no children. The process of building or using the tree is not very relevant to the challenge, and can be found [on Wikipedia](https://en.wikipedia.org/wiki/Huffman_coding#Basic_technique). The most important information is that a Huffman Tree is built, based on the frequency of uncompressed characters, in order to map those uncompressed values to compressed codes, and that this tree is stored along with the compressed data.

## Zip File Format

The zip file format is primarily an archive format: it takes many files and directories, and converts them into a single file which can be extracted back into the original directory structure. It *also* supports compression, however an important part of this compression is that it is applied on a per-file basis. Each file is compressed independently. This is different from a `.tar.gz` file, which first uses tar to package the directory structure into a single file, then gzips the resulting file all at once.

Since each file is compressed individually, the zip file as a whole will not contain the tree(s) I am searching for. Initially, I did not remember this fact, so I made some uninformed searches like "zip view huffman tree". However, I stumbled upon this thread: [What tool lets me see gzip's Huffman table and blocks?](https://stackoverflow.com/questions/28253173/what-tool-lets-me-see-gzips-huffman-table-and-blocks), which pointed me towards a small program named [infgen](https://github.com/madler/infgen) which can output a human readable description of a gzip, zlib, or deflate stream. I saved this for later, did a bit of research, and remembered the existence of per-file compression. Searching "zip check algorithm" gave me: [How to determine compression method of a ZIP/RAR file](https://stackoverflow.com/questions/6896487/how-to-determine-compression-method-of-a-zip-rar-file), which pointed me towards the Python package [hachoir](https://pypi.org/project/hachoir/).

Each individual file should have the compressed data with the Huffman Tree used, so to find the Huffman Trees (which are, again, for *compression*), I'd need to first get the data of each file out of the zip, and ignore any information storing stuff like directory structure (which are for *archiving*).

`hachoir` comes with a bunch of parsers for binary files, including zip files (and it turns out to be far more convenient than searching up the spec and opening the file in a hex editor). I used `hachoir-urwid challenge.zip` to investigate.

```txt
0) file:challenge.zip: ZIP archive (147.5 KB)
   0) header[0]= 0x04034b50: Header (4 bytes)
 + 4) file[0]: File entry: 00.txt (15692) (15.4 KB)
   15728) header[1]= 0x04034b50: Header (4 bytes)
 + 15732) file[1]: File entry: 01.txt (10459) (10.2 KB)
   26223) header[2]= 0x04034b50: Header (4 bytes)
 + 26227) file[2]: File entry: 02.txt (9988) (9.8 KB)
   36247) header[3]= 0x04034b50: Header (4 bytes)
 + 36251) file[3]: File entry: 03.txt (5013) (5045 bytes)
   41296) header[4]= 0x04034b50: Header (4 bytes)
 + 41300) file[4]: File entry: 04.txt (7895) (7927 bytes)
   49227) header[5]= 0x04034b50: Header (4 bytes)
 + 49231) file[5]: File entry: 05.txt (4231) (4263 bytes)
   53494) header[6]= 0x04034b50: Header (4 bytes)
 + 53498) file[6]: File entry: 06.txt (7167) (7199 bytes)
   60697) header[7]= 0x04034b50: Header (4 bytes)
 + (...)
```

Looks like the zip file has a bunch of file entries for all the txt files, as expected. I expanded the information for some of the files and they all reported a compression method of deflate. There's also another field for the compressed data, which should be what I'm looking for, since the tree should be stored with the compressed data.

```txt
0) file:challenge.zip: ZIP archive (147.5 KB)
   0) header[0]= 0x04034b50: Header (4 bytes)
 - 4) file[0]: File entry: 00.txt (15692) (15.4 KB)
    + 0) version_needed: Version needed (2 bytes)
    + 2) flags: General purpose flag (2 bytes)
      4) compression= Deflate: Compression method (2 bytes)
    + 6) last_mod= 1980-01-01 00:00:00: Last modification file time (4 bytes)
      10) crc32= 0xe8d5abfe: CRC-32 (4 bytes)
      14) compressed_size= 15692: Compressed size (4 bytes)
      18) uncompressed_size= 24616: Uncompressed size (4 bytes)
      22) filename_length= 6: Filename length (2 bytes)
      24) extra_length= 0: Extra fields length (2 bytes)
      26) filename= "00.txt": Filename (6 bytes)
      32) compressed_data= "\5\xc1\x014-@\x92-\xd8\xb5\xd6Zk\xad(...)": File "00.txt" (15.3 KB) (15.3 KB)
   15728) header[1]= 0x04034b50: Header (4 bytes)
 + 15732) file[1]: File entry: 01.txt (10459) (10.2 KB)
   26223) header[2]= 0x04034b50: Header (4 bytes)
```

## Extracting Deflate Data

Files in a zip archive can specify what type of compression they use (or if they use no compression), and the most common method is an algorithm called [Deflate](https://en.wikipedia.org/wiki/Deflate). Deflate compresses data in a series of blocks. Each block is either:

1. Left uncompressed
2. Compressed to remove duplicate strings, then compressed with a Huffman Tree that is defined in the Deflate spec (the tree does not need to be stored in the resulting data)
3. Compressed to remove duplicate strings, then compressed with a Huffman Tree built dynamically (the tree uses the frequencies in the half-compressed data to determine the codes. Since it will be different depending on the input data, it needs to be stored in the resulting data).

[Here's](https://zlib.net/feldspar.html) some more info about Deflate, if curious.

I assumed that the files would use the third method so that the tree would be somewhere in the Deflate data for me to inspect. I used `hachoir` in a Python script to extract the `compressed_data` from each txt file, which would be Deflate data as specified by the compression method.

```python
from hachoir.stream import FileInputStream
from hachoir.parser import guessParser, archive

parser = guessParser(FileInputStream("challenge.zip"))

# ignore zip stuff like central directory
files = [entry for entry in parser if type(entry) == archive.zip.FileEntry]
# compressed_data is the last field in the file entry, so index -1
streams = [list(file)[-1].value for file in files]
```

I then used the infgen program I found earlier to process each stream.

```python
import subprocess

info = []
for stream in streams:
    p = subprocess.run("./infgen", input=stream, capture_output=True)
    info.append(p.stdout.decode())
```

Here's the first few lines of output by infgen for `00.txt`:

```txt
! infgen 2.4 output
!
last
dynamic
litlen 10 7
litlen 32 3
litlen 33 12
litlen 34 12
litlen 39 13
litlen 40 14
litlen 41 13
litlen 44 11
```

Each file's Deflate stream only had one block, since the first block in each file was marked as the last block, and all blocks were compressed using the dynamic Huffman Tree method (method #3 from before), so everything is going according to plan.

## How Deflate Stores Trees

At first, I had no clue what these "litlen" values meant, so I had a look at the comments in `infgen`'s code. Though they didn't really explain what the values were, the comments said that these values describe the dynamic/custom Huffman Tree used to compress the block. A search of "deflate dynamic header" gave me the thread [How to rebuild the dynamic Huffman tree from DEFLATE](https://stackoverflow.com/questions/53144375/how-to-rebuild-the-dynamic-huffman-tree-from-deflate). The thread was not very useful, except for the [link](https://datatracker.ietf.org/doc/html/rfc1951) to the RFC1951 spec that defines the Deflate format. Section 3.2 contained the relevant information.

The Deflate format wishes to store custom Huffman Trees in as small of a space as possible. The normal method of building Huffman Trees is not very convenient for this, as multiple trees could be built from the same frequency table (imagine if we took the tree from before and just mirrored it: the resulting codes would be the same length as before, but all different). So, the Deflate spec adds some of its own rules on the compressed Huffman Codes.

> * All codes of a given bit length have lexicographically consecutive values, in the same order as the symbols they represent;
> * Shorter codes lexicographically precede longer codes.

Here are some explanations based on the example from earlier, where we produced this table:

Character | Code
-|-
A | 1
B | 01
C | 001
D | 000

This tree would not satisfy the Deflate rules. It breaks both of them, since `D` comes right after `C`, and they have the same bit length, `D` should have a code that is 1 greater than the code of `C`, but it actually has a code 1 less than `C` (rule 1). In addition, the code for `A` is `1`, but it should compare (using string ordering) less than the code for `B`, which has a longer bit length (rule 2). You can imagine the code for `A` being the string `"b"`, while the code for `B` has the string `"ab"`. `"ab"` comes before `"b"`.

The following mapping would be valid under Deflate:

Character | Code
-|-
A | 0
B | 10
C | 110
D | 111

Notice that `111` is 1 after `110`, and that `"0"` < `"10"` < `"110"` (by string comparison - `"a"` < `"ba"` < `"bba"`).

It turns out that when given a table like below, there is only one possible way to map the characters to compressed codes which follow the Deflate rules.

Character | Bit Length
-|-
A|1
B|2
C|3
D|3

So, the above table is what the "litlen" values are storing. `litlen 66 2` would mean the uncompressed value 66 (ASCII for `'B'`) has a bit length of 2. Conveniently, the Deflate spec provides code on how to convert a list of characters and their bit lengths into a tree. We can just translate it into Python and see what we get.

```python
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
```

Here's the "tree" for `00.txt`. Remember, the actual Huffman Tree just helps to build and decode the mapping of uncompressed values to compressed codes. However, a list is sufficient to represent the mapping itself, where the `i`th element in the list represents the compressed code for the uncompressed value `i`.

```txt
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 4088, 4089, 0, 0, 0, 0, 8188, 16380, 8189, 0, 0, 2040,
16381, 4090, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4091, 16382, 0, 0, 0, 2041, 0, 4,
2042, 20, 21, 194, 195, 22, 5, 6, 508, 196, 23, 197, 7, 1, 198, 4092, 199, 8, 9,
200, 201, 202, 4093, 203, 2043, 204, 205, 206, 207, 509, 208, 209, 210, 211,
212, 0, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226,
227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242,
243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16383,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

## Where's the Flag?

Hm. Maybe converting the compressed codes to characters will help us see where to look?
`[chr(x) for x in trees[0] if x != 0]`

```txt
['`', '\u0ff8', '\u0ff9', 'ῼ', '㿼', '´', '߸', '㿽', '\u0ffa', '\u0ffb', '㿾', '߹', '\x04', 'ߺ', '\x14', '\x15', 'Â', 'Ã', '\x16', '\x05', '\x06', 'Ǽ', 'Ä', '\x17', 'Å', '\x07', '\x01', 'Æ', '\u0ffc', 'Ç', '\x08', '\t', 'È', 'É', 'Ê', '\u0ffd', 'Ë', '\u07fb', 'Ì', 'Í', 'Î', 'Ï', 'ǽ', 'Ð', 'Ñ', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö', '×', 'Ø', 'Ù', 'Ú', 'Û', 'Ü', 'Ý', 'Þ', 'ß', 'à', 'á', 'â', 'ã', 'ä', 'å', 'æ', 'ç', 'è', 'é', 'ê', 'ë', 'ì', 'í', 'î', 'ï', 'ð', 'ñ', 'ò', 'ó', 'ô', 'õ', 'ö', '÷', 'ø', 'ù', 'ú', 'û', 'ü', 'ý', '㿿']
```

Hm. `[chr(x) for x in trees[0] if chr(x) in string.printable]`?

```txt
['`', '\t']
```

Hm. Throughout essentially the entire challenge I assumed the flag was in the trees, that maybe the compressed codes would turn out to be ASCII and that the flag would be spelled out in the mapping for one of the files, but the only real clue to suggest any of this is the challenge name, and it doesn't look like there are any normal characters in most of the trees.

However, not all hope is lost. I printed out the `litlens` list at every iteration, and it seems like there some files with a *lot* of length 8 literals. This didn't really sound right (especially since the original length of a byte is 8 bits long), so let's do a real check. `import collections` and then inside the loop `print(collections.Counter(x[1] for x in litlens))`

```txt
Counter({8: 60, 12: 6, 4: 6, 14: 4, 11: 4, 5: 4, 3: 2, 13: 2, 9: 2, 7: 1})
Counter({8: 214, 7: 13, 6: 4})
Counter({8: 156, 12: 6, 11: 4, 14: 4, 3: 2, 13: 2, 10: 2, 4: 2, 9: 1, 7: 1})
Counter({8: 31, 5: 7, 4: 6, 9: 4, 13: 4, 14: 4, 12: 3, 3: 2, 10: 2, 6: 1, 7: 1, 11: 1})
Counter({8: 121, 12: 6, 9: 4, 14: 4, 3: 3, 13: 2, 11: 2, 4: 2, 6: 1, 10: 1})
Counter({8: 74, 10: 6, 4: 5, 5: 4, 14: 4, 3: 2, 11: 2, 12: 2, 13: 2, 6: 1})
Counter({8: 122, 12: 6, 11: 4, 10: 4, 13: 4, 4: 4, 3: 2, 6: 1})
Counter({8: 12, 5: 10, 13: 6, 4: 5, 14: 4, 6: 4, 10: 3, 3: 2, 9: 2, 7: 1})
Counter({8: 204, 12: 8, 11: 4, 10: 4, 4: 2, 5: 2, 7: 1})
Counter({8: 92, 12: 12, 11: 6, 4: 6, 3: 2, 9: 1, 7: 1})
Counter({8: 74, 12: 6, 11: 6, 4: 6, 13: 4, 3: 2, 5: 2, 6: 1, 10: 1, 9: 1})
Counter({8: 91, 13: 8, 4: 5, 9: 4, 3: 2, 10: 2, 5: 2, 12: 2, 11: 1, 7: 1})
Counter({8: 73, 13: 6, 4: 6, 9: 5, 15: 4, 11: 2, 14: 2, 5: 2, 6: 1, 2: 1})
Counter({8: 60, 13: 6, 11: 6, 4: 6, 14: 4, 5: 4, 3: 2, 9: 2, 7: 1})
Counter({8: 12, 5: 9, 4: 7, 6: 6, 14: 4, 13: 4, 11: 2, 9: 2, 10: 2, 3: 1, 7: 1, 12: 1})
Counter({8: 75, 10: 8, 4: 5, 5: 4, 12: 4, 3: 2, 11: 2, 7: 1, 9: 1})
Counter({8: 122, 12: 8, 11: 4, 10: 4, 4: 3, 7: 2, 3: 2, 5: 2})
Counter({8: 18, 5: 9, 13: 6, 6: 5, 4: 5, 15: 4, 10: 3, 3: 2, 14: 2, 9: 2})
Counter({8: 180, 10: 6, 4: 4, 13: 4, 11: 2, 12: 2, 6: 2, 7: 1})
Counter({8: 92, 11: 6, 4: 5, 13: 4, 10: 4, 5: 2, 3: 2, 12: 2, 7: 1})
Counter({8: 51, 10: 8, 11: 8, 4: 8, 5: 4, 6: 2, 7: 1, 3: 1})
Counter({8: 52, 11: 10, 4: 6, 12: 4, 5: 4, 3: 2, 6: 2, 10: 2, 7: 1})
Counter({8: 108, 12: 8, 5: 6, 11: 4, 10: 4, 4: 4, 7: 1, 3: 1})
Counter({8: 11, 5: 9, 11: 8, 6: 6, 4: 5, 9: 3, 3: 2, 10: 2, 7: 1})
Counter({8: 140, 10: 6, 12: 6, 13: 4, 5: 4, 4: 3, 7: 1, 3: 1})
Counter({8: 63, 11: 6, 5: 5, 4: 5, 12: 4, 9: 3, 3: 2, 10: 2, 6: 1, 7: 1})
```

In every single file, 8 is the most common Huffman Code length, and often by a significant margin. This didn't seem right, because there should be more codes with shorter length. Why would there be 214 codes of length 8 when there are only 13 codes of length 7 being used? This just seems to support my theory that some sort of ASCII text is in the Huffman Codes. To compare, I took the 26 txt files and compressed them in a zip file on my own using the default settings of WinRAR, and ran my script on this new zip file:

```txt
Counter({6: 11, 7: 10, 5: 9, 11: 8, 8: 5, 4: 3, 9: 3, 10: 2, 3: 2})
Counter({11: 12, 5: 11, 6: 11, 7: 10, 8: 5, 10: 2, 9: 2, 3: 2, 4: 2})
Counter({6: 13, 5: 10, 7: 9, 8: 8, 11: 4, 10: 2, 3: 2, 4: 2, 9: 2})
Counter({6: 13, 5: 10, 7: 10, 11: 6, 8: 5, 9: 4, 3: 2, 4: 2, 10: 1})
Counter({6: 13, 5: 10, 7: 10, 8: 5, 12: 4, 10: 4, 9: 3, 11: 2, 4: 2, 3: 2})
Counter({6: 15, 7: 11, 5: 9, 9: 4, 8: 3, 10: 3, 11: 2, 3: 2, 4: 2})
Counter({6: 14, 5: 10, 7: 8, 8: 5, 11: 4, 9: 4, 10: 2, 3: 2, 4: 2})
Counter({7: 12, 6: 10, 5: 9, 8: 5, 9: 4, 10: 3, 4: 3, 11: 2, 3: 2})
Counter({6: 12, 5: 11, 7: 8, 9: 7, 10: 6, 8: 3, 4: 2, 3: 2})
Counter({6: 12, 5: 11, 7: 7, 8: 6, 9: 5, 11: 4, 10: 4, 4: 2, 3: 2})
Counter({5: 11, 6: 11, 7: 10, 9: 7, 4: 4, 8: 4, 10: 2, 3: 1})
Counter({7: 13, 6: 12, 5: 10, 11: 8, 10: 4, 8: 3, 9: 2, 3: 2, 4: 2})
Counter({6: 13, 5: 10, 7: 9, 8: 6, 9: 6, 10: 3, 11: 2, 3: 2, 4: 2})
Counter({6: 15, 7: 9, 5: 7, 8: 7, 11: 4, 9: 4, 12: 4, 4: 3, 3: 2, 10: 1})
Counter({5: 11, 6: 11, 7: 10, 11: 6, 8: 5, 9: 3, 10: 3, 4: 2, 3: 2})
Counter({6: 16, 7: 8, 5: 7, 8: 5, 10: 4, 11: 3, 9: 3, 4: 3, 12: 2, 3: 2})
Counter({5: 11, 6: 11, 7: 9, 10: 8, 8: 7, 11: 4, 3: 2, 4: 2, 9: 1})
Counter({6: 12, 5: 11, 7: 8, 9: 6, 11: 6, 8: 4, 4: 2, 3: 2, 10: 1})
Counter({6: 13, 5: 12, 7: 11, 11: 4, 9: 4, 8: 3, 10: 2, 3: 2, 4: 1})
Counter({6: 14, 5: 10, 7: 7, 8: 6, 9: 5, 10: 4, 11: 4, 4: 2, 3: 2})
Counter({6: 14, 5: 10, 7: 7, 8: 6, 10: 6, 9: 5, 4: 4, 3: 1})
Counter({6: 12, 5: 11, 7: 8, 10: 7, 8: 5, 11: 2, 3: 2, 4: 2, 9: 2})
Counter({5: 12, 6: 10, 7: 9, 9: 5, 11: 4, 10: 4, 8: 2, 4: 2, 3: 2})
Counter({6: 14, 5: 10, 7: 8, 9: 6, 8: 4, 12: 4, 10: 2, 11: 2, 3: 2, 4: 2})
Counter({6: 12, 5: 11, 7: 7, 8: 6, 9: 5, 10: 5, 11: 2, 3: 2, 4: 2})
Counter({6: 13, 7: 9, 5: 8, 8: 7, 10: 4, 11: 3, 9: 3, 4: 3, 12: 2, 3: 2})
```

This looks way more reasonable. Few codes with short length, and steadily increasing code length frequencies. In addition, notice that the total number of mappings in the litlen sequence (`len(litlens)`) is much lower here. This makes sense, because the files being compressed are entirely uppercase plain english. There should be no need to have over 100 characters in the tree, because those characters would never appear in our uncompressed text, and so we don't need a mapping of those characters to a compressed Huffman Code.

Since the suspiciously common length is 8 bits, the exact length of a byte, it seems like there really is something to look at in the codes.

## Challenge Description to the Rescue

It was at this point that I thought back to the challenge description.

> Sometimes, what's more important is not what you have, but what you're missing.

As mentioned, there are way more codes than there should be in the provided trees, which means there are mappings for characters that are never even used. In addition, the text being compressed is a story without the letter `e`. Since the whole story is uppercase, that would be the character `E`. Perhaps there might be something special if the tree contains a code for the character `E`? Adding `print(ord("E") in set(x[0] for x in litlens))` gives `True` for every file.

I'll print out the code for `E` used in each file at the bottom of the loop body.
`print(bin(tree[ord("E")])[2:].zfill(8))`

```txt
11000010
00101010
01100010
11011110
10000100
10110100
10000100
11110010
00110010
10100010
10110100
10100010
10110100
11000010
11110010
10110010
10000100
11101100
01001010
10100010
11001010
11001010
10010010
11110010
01110010
10111110
```

We know the flag will start with `CTF{`, so let's just check what the binary for `C` is to see if there's some operation being applied to all of them.

Character | Binary | Huffman Code Found
-|-|-
C | `01000011` | `11000010`
T | `01010100` | `00101010`
F | `01000110` | `01100010`

Well, I think it's pretty clear that the bits are just being reversed. Let's add that into the script and get the flag.

```python
flag = []
for tree in trees:
    code = bin(tree[ord("E")])[2:].zfill(8)
    flag.append(chr(int(code[::-1], 2)))
print("".join(flag))
```

```txt
CTF{!-!OLE-E-COM!7RESSION}
```

Full solve script can be found in this folder (it's really just the given snippets put together in one file). Working directory must have the provided `challenge.zip`, as well as a compiled executable of [infgen](https://github.com/madler/infgen) to run.
