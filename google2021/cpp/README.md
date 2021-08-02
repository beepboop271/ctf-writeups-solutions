# CPP

Google CTF Qualifiers 2021 - Reversing - 155 solves/75 points

> We have this program's source code, but it uses a strange DRM solution. Can you crack it?

Provided file: `cpp.c`

## Investigation

Upon opening the file, we are greeted by thousands of lines of preprocessor directives. It looks like a flag is being input at the top of the file:

```c
// Please type the flag:
#define FLAG_0 CHAR_C
#define FLAG_1 CHAR_T
#define FLAG_2 CHAR_F
#define FLAG_3 CHAR_LBRACE
```

Then, it is processed somehow. Let's try to compile the file, `gcc cpp.c`. The preprocessor will run through all the directives before the compiler compiles the code, so we should be able to see what is going on.

```txt
cpp.c:110:2: warning: #warning "Please wait a few seconds while your flag is validated." [-Wcpp]
  110 | #warning "Please wait a few seconds while your flag is validated."
      |  ^~~~~~~
In file included from cpp.c:6221,
                 from cpp.c:6218,
                 from cpp.c:6218,
                 from cpp.c:6221,
                 from cpp.c:6218,
                 from cpp.c:6221,
                 from cpp.c:6218,
                 from cpp.c:6218,
                 from cpp.c:6221,
                 from cpp.c:6218,
                 from cpp.c:6218,
                 from cpp.c:6218,
                 from cpp.c:6218:
cpp.c:6208: error: #error "INVALID_FLAG"
 6208 | #error "INVALID_FLAG"
      |
```

Look like the preprocessor will stop the compilation using an `#error` directive if the flag isn't accepted, and we don't get an output executable.

Let's have a closer look at the source file and see what commands are being used.

## Preprocessor Directives

For those unaware, the preprocessor is a program that runs certain special lines of code, called preprocessor directives, before any code compilation occurs. Preprocessor directives all begin with `#`. The preprocessor is most commonly used to include other source files, or to expand code macros. Let's go through all the directives the source uses.

### `#define`, `#undef`

`#define` declares a macro. For example, `#define PI 3.14` or `#define BUF_SIZE 1024`. When the preprocessor runs, all instances of `PI` or `BUF_SIZE` are replaced with their associated value/code. It is possible to define a macro with an empty value, like `#define X`. The code given uses both of these, such as `#define S 0` and `#define A0`.

`#undef` is like the opposite of `#define`, removing a macro definition. The defining and undefining process happens sequentially throughout the program as the directives are encountered.

### `#if`, `#ifdef`, `#ifndef`, `#else`, `#endif`

`#if` functions the same way as an if statement in normal code. If the condition is not met, any code or directives in the if body is ignored. Macros are expanded, for example the challenge uses `#if S == 0`, which would expand the S macro into its value. The `#ifdef` and `#ifndef` statements check if a macro exists for a certain definition.

An if block is ended by either an `#endif`, or an `#else` block (which would be ended by an `#endif`).

### `#warning`, `#error`

`#warning` simply prints out a warning message, while `#error` prints an error message and also halts the compilation process.

### `#include`, `__INCLUDE_LEVEL__`

`#include` is how other source files are *included* in the compilation of a certain file, for example standard library functions. Including is essentially like copy-pasting the referenced file, so usually care must be taken to prevent accidentally including the same file twice (e.g. A includes B and C, but C's source includes B) with an [include guard](https://en.wikipedia.org/wiki/Include_guard).

However, that is ignored in this challenge, because (as an editor might warn you when opening the file) `cpp.c` includes itself. You can think of this a recursive function call, where the function body contains all the preprocessor directives.

The challenge also uses a macro `__INCLUDE_LEVEL__`, which as the [gcc docs](https://gcc.gnu.org/onlinedocs/cpp/Common-Predefined-Macros.html) say:

> This macro expands to a decimal integer constant that represents the depth of nesting in include files. The value of this macro is incremented on every ‘#include’ directive and decremented at the end of every included file. It starts out at 0, its value within the base file specified on the command line.

The challenge uses this to make sure setup at the start of the file is only done once, and not repeated upon recursive inclusion.

## What is the file doing?

Skimming through the file, it looks like there are a few distinct blocks of what is happening. After the `#if __INCLUDE_LEVEL__ == 0`, a bunch of setup is happening. The flag is defined, the macro `S` is defined to be 0, and a bunch of `ROM` macros are defined:

```c
#define ROM_00000000_0 1
#define ROM_00000000_1 1
#define ROM_00000000_2 0
#define ROM_00000000_3 1
#define ROM_00000000_4 1
#define ROM_00000000_5 1
#define ROM_00000000_6 0
#define ROM_00000000_7 1
#define ROM_00000001_0 1
#define ROM_00000001_1 0
#define ROM_00000001_2 1
#define ROM_00000001_3 0
#define ROM_00000001_4 1
#define ROM_00000001_5 0
#define ROM_00000001_6 1
#define ROM_00000001_7 0
#define ROM_00000010_0 1
#define ROM_00000010_1 1
#define ROM_00000010_2 0
```

It looks like bytes are being defined bit by bit here to fill up some form of ROM (read-only memory). The format of the macros appears to be `ROM`, followed by the byte address in binary, then the bit number in decimal.

Afterwards, it looks like the flag is being copied into the ROM (indentation added):

```c
#if FLAG_0 & (1<<0)
    #define ROM_10000000_0 1
#else
    #define ROM_10000000_0 0
#endif
#if FLAG_0 & (1<<1)
    #define ROM_10000000_1 1
#else
    #define ROM_10000000_1 0
#endif
#if FLAG_0 & (1<<2)
    #define ROM_10000000_2 1
#else
    #define ROM_10000000_2 0
#endif
#if FLAG_0 & (1<<3)
    #define ROM_10000000_3 1
#else
    #define ROM_10000000_3 0
#endif
#if FLAG_0 & (1<<4)
    #define ROM_10000000_4 1
#else
    #define ROM_10000000_4 0
#endif
```

Remember, macros are expanded in `#if` directives, so the numeric value of the 0th flag character is tested. If the 0th bit is set in the flag, the 0th bit of the ROM at address 128 it set. If the 1st bit is set in the flag, the 1st bit of the ROM at address 128 is set. This continues on and on, with `FLAG_1` at `ROM_10000001`, `FLAG_2` at `ROM_10000010`, and so on.

Then, some more complicated macros are defined.

```c
#define _LD(x, y) ROM_ ## x ## _ ## y
#define LD(x, y) _LD(x, y)
#define _MA(l0, l1, l2, l3, l4, l5, l6, l7) l7 ## l6 ## l5 ## l4 ## l3 ## l2 ## l1 ## l0
#define MA(l0, l1, l2, l3, l4, l5, l6, l7) _MA(l0, l1, l2, l3, l4, l5, l6, l7)
#define l MA(l0, l1, l2, l3, l4, l5, l6, l7)
```

The `##` operator here is used to concatenate tokens ([docs](https://gcc.gnu.org/onlinedocs/cpp/Concatenation.html)) and build an *identifier*. Roughly, it would be like if the following Python code printed out "world":

```python
hello = "world"
token1 = "he"
token2 = "llo"
# print(token1 ## token2)
```

Normal string concatenation would just add "he" and "llo" together to "hello". However, suppose we could take concatenate the values of `token1` and `token2` and treat it as an identifier. Then, it would reference the variable `hello`. This is essentially what is being done in the macros.

Upon searching through the file, it appears that these are only used to run something like `LD(l, 3)`. The `l`, using the `MA` macro, would take the values of the macros `l0` through `l7`, whatever they may be, and paste them together to form a longer binary number (the address). Then, the address would be passed into LD, and it would be pasted along with the second argument (a decimal number) into a ROM address, in the format discussed earlier.

So, this program is able to read the flag like so:

```c
#define l7 1
#define l6 0
#define l5 0
#define l4 0
#define l3 1
#define l2 0
#define l1 1
#define l0 1
// set the address to 0b10001011 = 139
// since FLAG_0 is at 128, this would be FLAG_11

// expands to ROM_ + 10001011 + _ + 0 = ROM_10001011_0
#if LD(l, 0) == 1
    // code to run if FLAG_11's 0th bit is set
#else
    // code to run if FLAG_11's 0th bit is unset
#endif
#if LD(l, 1) == 1  // code to run based on FLAG_11's 1st bit
#if LD(l, 2) == 1  // etc...
#if LD(l, 3) == 1
#if LD(l, 4) == 1
#if LD(l, 5) == 1
#if LD(l, 6) == 1
#if LD(l, 7) == 1
```

After all this setup, the program has `#if __INCLUDE_LEVEL__ > 12` and then looks something like this (again, indentation added):

```c
#if __INCLUDE_LEVEL__ > 12
    #if S == 0
        // stuff
    #endif
    #if S == 1
        // stuff
    #endif
    #if S == 2
        // stuff
    #endif
    // ...

    #if S == 57
        #undef S
        #define S 58
        #error "INVALID_FLAG"
    #endif
    #if S == 58
        #undef S
        #define S 59
        #undef S
        #define S -1
    #endif
#else
    #if S != -1
        #include "cpp.c"
    #endif
    #if S != -1
        #include "cpp.c"
    #endif
#endif
```

Seems there might be some sort of state machine here, with S controlling what state the machine is in. In addition, as mentioned, there is the recursive `#include "cpp.c"`. Various processing is done, including processing based on the flag, and the program either reaches state 57, which throws `#error "INVALID_FLAG"`, or state 58, which defines S as -1 and exits the recursive loop. There's also state 10, which throws `#error "BUG"`.

Finally, there is this (indentation added):

```c
#if __INCLUDE_LEVEL__ == 0
    #if S != -1
        #error "Failed to execute program"
    #endif
    #include <stdio.h>
    int main() {
        printf("Key valid. Enjoy your program!\n");
        printf("2+2 = %d\n", 2+2);
    }
#endif
```

If the preprocessor state machine exits without setting S to -1 (as done in state 58), the compilation fails. If it does set S to -1, we get to find out what the value of `2+2` is.

## `angr` time

I had never used angr or z3 before this challenge, but I knew of them. This challenge involves determining some input which will produce a desired output state, some input which satisfies the constraints that the program imposes through its state machine. This is exactly an example of something angr is good at.

However, in order for angr to determine the constraints so that a valid input can be solved, it needs to be able to execute the program and explore the various branches. This means we need to produce an executable file for angr that it can manipulate the input with, because so far we've been running the file in gcc with a hardcoded flag.

First, let's convert the ROM bits in the file into an array that we can put in the final program. I sliced out the part defining the ROM to get this:

```python
import re

pat = re.compile(r"^#define ROM_([01]{8})_([0-7]) ([01])\n$")

with open("cpp.c") as f:
    # 112 #define ROM_00000000_0 1
    #     ...
    # 839 #define ROM_01011010_7 0
    rom_data = [pat.match(line) for line in f.readlines()[111:839] if pat.match(line)]

rom = [0]*255
max_addr = 0

for match in rom_data:
    addr = int(match.group(1), 2)
    bit, value = map(int, match.groups()[1:])
    rom[addr] |= value << bit
    if addr > max_addr:
        max_addr = addr

rom = rom[:max_addr+1]
print(rom)
```

```txt
[187, 85, 171, 197, 185, 157, 201, 105, 187, 55, 217, 205, 33, 179, 207, 207, 159, 9, 181, 61, 235, 127, 87, 161, 235, 135, 103, 35, 23, 37, 209, 27, 8, 100, 100, 53, 145, 100, 231, 160, 6, 170, 221, 117, 23, 157, 109, 92, 94, 25, 253, 233, 12, 249, 180, 131, 134, 34, 66, 30, 87, 161, 40, 98, 250, 123, 27, 186, 30, 180, 179, 88, 198, 243, 140, 144, 59, 186, 25, 110, 206, 223, 241, 37, 141, 64, 128, 112, 224, 77, 28]
```

Then, I cut out the `#if __INCLUDE_LEVEL__ > 12`, `#else`, `#endif` block (i.e. the state machine loop) into another file to process it. In my first attempt, I used a bunch of if statements to convert the output, but I ended up missing some cases, so to be sure, I wrote a second regex based version which first ensures that I know what all the cases are before substituting them for C code.

Here is the full regex, if you're interested. It (along with the code) is not very important, so you can skip over it:

```regex
^(?:#if (?:__INCLUDE_LEVEL__ > 12|S [!=]= -?\d+|LD\(l, [0-7]\))|#ifn?def (?:c|[A-Z][0-7])|#else|#endif|#define (?:c|S -?\d+|l[0-7] [01]|[A-Z][0-7])|#undef (?:c|S|[A-Zl][0-7])|#error (?:"INVALID_FLAG"|"BUG")|#include "cpp\.c")\n$
```

```python
with open("cpp.c") as f:
    # 1926 #if __INCLUDE_LEVEL__ > 12
    #      ...
    # 6223 #endif
    lines = f.readlines()[1925:6223]

pat = re.compile(
    r"^(?:"
    r"#if (?:__INCLUDE_LEVEL__ > 12|S [!=]= -?\d+|LD\(l, [0-7]\))|"
    r"#ifn?def (?:c|[A-Z][0-7])|"
    r"#else|"
    r"#endif|"
    r"#define (?:c|S -?\d+|l[0-7] [01]|[A-Z][0-7])|"
    r"#undef (?:c|S|[A-Zl][0-7])|"
    r'#error (?:"INVALID_FLAG"|"BUG")|'
    r'#include "cpp\.c"'
    r")\n$"
)
assert all(pat.match(line) for line in lines)
```

Now, how will we convert to C?

Macro definitions will become variables: S is always defined to some integer, so it will have an integer type, and whenever S is defined to be a certain value, we will set the S variable to be that number.

For all macros with format `[A-Z][0-7]`, the value is empty. So, we just need to keep track of whether the macro is defined or not. Since each capital letter is always followed by a number from 0-7, we can just create a single byte to represent each capital letter, and use the nth bit to represent whether that specific macro is defined or not.

`#undef` will just set bits/values to 0.

If-like directives are just if statements testing the appropriate values/bits.

In addition, we can create a byte array `rom` which will hold both the hardcoded values and the flag.

Finally, we will mimic the recursive `#include` by placing everything in a function called `run` which takes a parameter `include` to mimic the `__INCLUDE_LEVEL__` macro, and call `run(include+1)` each time we need to replace `#include "cpp.c"`

Pattern|Example|Replacement
-|-|-
`^#if __INCLUDE_LEVEL__ > 12$`|-|`if (include > 12) {`
`^#if S ([!=]=) (-?\d+)$`|`#if S == 1`|`if (S == 1) {`
`^#if LD\(l, ([0-7])\)$`|`#if LD(l, 2)`|`if (rom[l] & (1<<2)) {`
`^#ifdef c$`|-|`if (c) {`
`^#ifndef c$`|-|`if (c == 0) {`
`^#ifdef ([A-Z])([0-7])$`|`#ifdef A4`|`if (A & (1<<4)) {`
`^#ifndef ([A-Z])([0-7])$`|`#ifndef B3`|`if ((B & (1<<3)) == 0) {`
`^#else$`|-|`} else {`
`^#endif$`|-|`}`
`^#define c$`|-|`c = 1;`
`^#define S (-?\d+)$`|`#define S 21`|`S = 21;`
`^#define l([0-7]) ([01])$`|`#define l5 1`|`l \|= 1<<5;`
`^#define ([A-Z])([0-7])$`|`#define C1`|`C \|= 1<<1;`
`^#undef c$`|-|`c = 0;`
`^#undef S$`|-|`S = 0;`
`^#undef ([A-Zl])([0-7])$`|`#undef N6`|`N = N & (~(1<<6));`
`^#error "INVALID_FLAG"$`|-|`printf("%s\n", "INVALID_FLAG");`<br>`exit(1);`
`^#error "BUG"$`|-|`printf("%s\n", "BUG");`<br>`exit(1);`
`^#include "cpp.c"$`|-|`run(include+1);`

```python
full = "".join(lines)

subs = {
    r"^#if __INCLUDE_LEVEL__ > 12$": "if (include > 12) {",
    r"^#if S ([!=]=) (-?\d+)$":
        lambda match: f"if (S {match.group(1)} {match.group(2)}) {{",
    r"^#if LD\(l, ([0-7])\)$":
        lambda match: f"if (rom[l] & (1<<{match.group(1)})) {{",
    r"^#ifdef c$": "if (c) {",
    r"^#ifndef c$": "if (c == 0) {",
    r"^#ifdef ([A-Z])([0-7])$":
        lambda match: f"if ({match.group(1)} & (1<<{match.group(2)})) {{",
    r"^#ifndef ([A-Z])([0-7])$":
        lambda match: f"if (({match.group(1)} & (1<<{match.group(2)})) == 0) {{",
    r"^#else$": "} else {",
    r"^#endif$": "}",
    r"^#define c$": "c = 1;",
    r"^#define S (-?\d+)$":
        lambda match: f"S = {match.group(1)};",
    r"^#define l([0-7]) ([01])$":
        lambda match: f"l |= {match.group(2)}<<{match.group(1)};",
    r"^#define ([A-Z])([0-7])$":
        lambda match: f"{match.group(1)} |= 1<<{match.group(2)};",
    r"^#undef c$": "c = 0;",
    r"^#undef S$": "S = 0;",
    r"^#undef ([A-Zl])([0-7])$":
        lambda match: f"{match.group(1)} = {match.group(1)} & (~(1<<{match.group(2)}));",
    r'^#error "INVALID_FLAG"$': 'printf("%s\\\\n", "INVALID_FLAG");\nexit(1);',
    r'^#error "BUG"$': 'printf("%s\\\\n", "BUG");\nexit(1);',
    r'^#include "cpp.c"$': "run(include+1);",
}

for pat, sub in subs.items():
    full = re.sub(pat, sub, full, flags=re.MULTILINE)

with open("converted-long.c", "w") as f:
    f.write(
"""#include <stdlib.h>
#include <stdio.h>

char S=0;
unsigned char c=0, l=0;
unsigned char A=0, B=0, C=0, I=0, M=0, N=0, O=0, P=0, Q=0, R=0, X=0, Y=0, Z=0;
unsigned char rom[256] = {""")
    f.write(", ".join(rom))
    f.write(
"""};

void run(int include) {
""")
    f.write(full)
    f.write(
"""}

int main() {
  scanf("%s", &rom[128]);
  run(0);
  if (S == -1) {
    printf("win\\n");
  }
  return 0;
}
""")
```

## It was not `angr` time

Unfortunately, the output of the program so far is over 4000 lines long, with over 1000 `if` statements. I tried running a simple `angr` solve script on it, and I watched it run for several minutes, continually increasing RAM usage to over 12 GB, before stopping it (I assume the more branches there are, the more the program flow depends on the input, and the more branched states you need to keep track of, resulting in a slow and memory intensive run).

However, looking at the output code, it seems like there are some very redundant blocks of code that result from every operation being done at the bit level. In addition, the code at different states seems pretty repetitive, like the same operation is being done to different inputs at different states.

Let's look through to see if we can find all the different operations to simplify them.

### Zero Check

```c
if ((Q & (1<<0)) == 0) {
    if ((Q & (1<<1)) == 0) {
        if ((Q & (1<<2)) == 0) {
            if ((Q & (1<<3)) == 0) {
                if ((Q & (1<<4)) == 0) {
                    if ((Q & (1<<5)) == 0) {
                        if ((Q & (1<<6)) == 0) {
                            if ((Q & (1<<7)) == 0) {
                                S = 0;
                                S = 58;
                            }
                        }
                    }
                }
            }
        }
    }
}
```

It's pretty clear that this is just going across each bit in the byte Q, checking for 0. We can replace this with:

```c
if (Q == 0) {
    S = 0;
    S = 58;
}
```

I could add a check to see if the same variable is assigned to multiple times in a row, but since that doesn't change the number of branches, I didn't bother.

### Bitwise OR

```c
if ((Q & (1<<0)) == 0) {
    if (A & (1<<0)) {
        Q |= 1<<0;
    }
}
if ((Q & (1<<1)) == 0) {
    if (A & (1<<1)) {
        Q |= 1<<1;
    }
}
// ... (replace each <<0 with <<1, <<2, <<3, etc.)
```

When repeated for each bit, this block computes Q |= A. If it's not clear, a truth table can help. First, we can see that the only variable being edited is Q. A is just an input.

Q | A || Q'
-|-|-|-
0|0||
0|1||
1|0||
1|1||

Since we only check if Q is 0, that means we do nothing if Q is 1.
When we do nothing, that means we just copy the value of Q to the output Q'.

Q | A || Q'
-|-|-|-
0|0||
0|1||
1|0||1
1|1||1

Likewise, we only continue if A is 1, which means we do nothing if A is 0.

Q | A || Q'
-|-|-|-
0|0||0
0|1||
1|0||1
1|1||1

If both Q is 0 and A is 1, we set Q to 1 as well.

Q | A || Q'
-|-|-|-
0|0||0
0|1||1
1|0||1
1|1||1

Since this is the OR operation, and it's being applied to each bit, we have bitwise OR. Replacement:

```c
Q |= A;
```

### Bitwise XOR

```c
if (C & (1<<0)) {
    if (A & (1<<0)) {
        A = A & (~(1<<0));
    } else {
        A |= 1<<0;
    }
}
// ...
```

Let's use the truth table again. We only check if C is 1, so do nothing/copy A when C is 0. If C is 1, we then check whether A is 1 or 0. If A is 1, we set A to 0, and if A is 0, we set A to 1:

A|C||A'
-|-|-|-
0|0||0
0|1||1
1|0||1
1|1||0

This is XOR applied to each bit, bitwise XOR.

```c
A ^= C;
```

The process is pretty much the same for the next few operations.

### Bitwise NOT

```c
if (R & (1<<0)) {
    R = R & (~(1<<0));
} else {
    R |= 1<<0;
}
// ...
```

R||R'
-|-|-
0||1
1||0

```c
R = ~R;
```

### Bitwise AND

```c
if (Z & (1<<0)) {
    if ((B & (1<<0)) == 0) {
        Z = Z & (~(1<<0));
    }
}
// ...
```

Z|B||Z'
-|-|-|-
0|0||0
0|1||0
1|0||0
1|1||1

```c
Z &= B;
```

### Copy

```c
if (X & (1<<0)) {
    Z |= 1<<0;
} else {
    Z = Z & (~(1<<0));
}
// ...
```

Z|X||Z'
-|-|-|-
0|0||0
0|1||1
1|0||0
1|1||1

```c
Z = X;
```

### ROM Copy

```c
l = l & (~(1<<0));
if (B & (1<<0)) {
    l |= 1<<0;
} else {
    l |= 0<<0;
}
// ...

if (rom[l] & (1<<0)) {
    A |= 1<<0;
} else {
    A = A & (~(1<<0));
}
// ...
```

The first part zeroes `l`, then copies 1 or 0 if B is 1 or 0, so it is equivalent to `l = B;`.

The second part is the copy operation we just saw, but using `rom[l]` as the source instead.

In addition, `l` is never used outside of these blocks, which means we can just get rid of the `l` entirely and replace these blocks with:

```c
A = rom[B];
```

### Addition

This block was the longest and most complicated one by far.

```c
c = 0;

if ((R & (1<<0)) == 0) {
    if ((Z & (1<<0)) == 0) {
        if (c) {
            R |= 1<<0;
            c = 0;
        }
    } else {
        if (c == 0) {
            R |= 1<<0;
            c = 0;
        }
    }
} else {
    if ((Z & (1<<0)) == 0) {
        if (c) {
            R = R & (~(1<<0));
            c = 1;
        }
    } else {
        if (c == 0) {
            R = R & (~(1<<0));
            c = 1;
        }
    }
}
// ... (note: `c = 0;` at the top is not repeated)
```

Though there are now 3 inputs and 2 outputs for each bit, the analysis we did before still applies. When the exact input is described in the code, determine what the outputs should be. When the input is not covered (do nothing), copy the inputs.

R|Z|c||c'|R'
-|-|-|-|-|-
0|0|0||0|0
0|0|1||0|1
0|1|0||0|1
0|1|1||1|0
1|0|0||0|1
1|0|1||1|0
1|1|0||1|0
1|1|1||1|1

If you're familiar with binary addition/computer engineering, you'll likely recognize this process. This block performs addition, and the `c` is the carry bit. Try adding up the bits on the left, and see that it produces the binary number written on the right (e.g. 0 + 1 + 1 = 0b10). The carry bit is preserved for the next bit's block so the addition works properly.

Replacement:

```c
R += Z;
```

### I *love* regex

Since I spent too much time troubleshooting my first attempt at this challenge, I was super paranoid and used regex to replace every single case, just to be sure I wasn't overlooking something. Here's the code I used, which is inserted in after the first round of replacements but before the file writing part. I wouldn't recommend taking much away from this though, especially the addition case.

```python
def repeat(x, start=1):
    base = x
    i = start
    # replace (\w) ... (\w) ... with \1 ... \2 ...
    while r"(\w)" in base:
        base = base.replace(r"(\w)", f"\\{i}", 1)
        i += 1

    # replace <<0 with <<1, <<2, <<3, ...
    parts = [x]
    for i in range(1, 8):
        parts.append(base.replace("<<0", f"<<{i}"))

    return "".join(parts)


subs = {
    # zero check
    repeat(r"if \(\((\w) & \(1<<0\)\) == 0\) {\n")+r"([^}]+)}\n}\n}\n}\n}\n}\n}\n}\n":
    lambda match: f"if ({match.group(1)} == 0) {{\n{match.group(2)}}}\n",

    # bitwise or
    repeat(r"if \(\((\w) & \(1<<0\)\) == 0\) {\nif \((\w) & \(1<<0\)\) {\n\1 \|= 1<<0;\n}\n}\n"):
    lambda match: f"{match.group(1)} |= {match.group(2)};\n",

    # bitwise xor
    repeat(r"if \((\w) & \(1<<0\)\) {\nif \((\w) & \(1<<0\)\) {\n\2 = \2 & \(~\(1<<0\)\);\n} else {\n\2 \|= 1<<0;\n}\n}\n"):
    lambda match: f"{match.group(2)} ^= {match.group(1)};\n",

    # bitwise not
    repeat(r"if \((\w) & \(1<<0\)\) {\n\1 = \1 & \(~\(1<<0\)\);\n} else {\n\1 \|= 1<<0;\n}\n"):
    lambda match: f"{match.group(1)} = ~{match.group(1)};\n",

    # bitwise and
    repeat(r"if \((\w) & \(1<<0\)\) {\nif \(\((\w) & \(1<<0\)\) == 0\) {\n\1 = \1 & \(~\(1<<0\)\);\n}\n}\n"):
    lambda match: f"{match.group(1)} &= {match.group(2)};\n",

    # copy
    repeat(r"if \((\w) & \(1<<0\)\) {\n(\w) \|= 1<<0;\n} else {\n\2 = \2 & \(~\(1<<0\)\);\n}\n"):
    lambda match: f"{match.group(2)} = {match.group(1)};\n",

    # rom copy
    repeat(r"l = l & \(~\(1<<0\)\);\nif \((\w) & \(1<<0\)\) {\nl \|= 1<<0;\n} else {\nl \|= 0<<0;\n}\n")
    +repeat(r"if \(rom\[l\] & \(1<<0\)\) {\n(\w) \|= 1<<0;\n} else {\n\2 = \2 & \(~\(1<<0\)\);\n}\n", 2):
    lambda match: f"{match.group(2)} = rom[{match.group(1)}];\n",

    # addition
    r"c = 0;\n"
    +repeat(r"if \(\((\w) & \(1<<0\)\) == 0\) {\nif \(\((\w) & \(1<<0\)\) == 0\) {\nif \(c\) {\n\1 \|= 1<<0;\nc = 0;\n}\n} else {\nif \(c == 0\) {\n\1 \|= 1<<0;\nc = 0;\n}\n}\n} else {\nif \(\(\2 & \(1<<0\)\) == 0\) {\nif \(c\) {\n\1 = \1 & \(~\(1<<0\)\);\nc = 1;\n}\n} else {\nif \(c == 0\) {\n\1 = \1 & \(~\(1<<0\)\);\nc = 1;\n}\n}\n}\n"):
    lambda match: f"{match.group(1)} += {match.group(2)};\n",
}

for pat, sub in subs.items():
    full = re.sub(pat, sub, full)
```

We can also remove the declaration for `c` and `l` at the top of the converted file, now that they are both eliminated.

## `angr` time for real

Finding an input which produces a certain state in the program is a fairly standard use case for angr, so I just went to the [docs for examples](https://docs.angr.io/examples), and found [this](https://github.com/angr/angr-doc/blob/master/examples/b01lersctf2020_little_engine/solve.py). The angr code is mostly unchanged from there. The constraints were chosen by taking the minimum and maximum numeric values defined with the `CHAR_` macros in the challenge source (`#define CHAR_0 48`, `#define CHAR_RBRACE 125`).

```python
import angr
import claripy

p = angr.Project("cpp")

flag_chars = [claripy.BVS(f"flag_{i}", 8) for i in range(27)]
flag = claripy.Concat(*(flag_chars + [claripy.BVV(b"\n")]))

st = p.factory.entry_state(
    args=["./cpp"],
    add_options=angr.options.unicorn,
    stdin=flag,
)

for k in flag_chars:
    st.solver.add(k >= ord("0"))
    st.solver.add(k <= ord("}"))

sm = p.factory.simulation_manager(st)
sm.run()

for x in sm.deadended:
    if b"win" in x.posix.dumps(1):
        print(x.posix.dumps(0))
```

Note that I compiled `converted-short.c` into the executable `cpp`.

Now that we've significantly simplified the program, this angr code gives us a result in under 10 seconds.

```txt
b'CTF{pr3pr0cess0r_pr0fe5sor}\n'
```
