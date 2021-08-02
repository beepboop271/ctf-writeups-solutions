import re

# 1. read the hardcoded rom bits

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

# 2. verify we know what all the possible lines are

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

# 3. substitute all the possible lines for their C equivalents

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

# 4. perform further substitution of long code blocks


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

# 5. write the result

with open("converted-short.c", "w") as f:
    f.write(
"""#include <stdlib.h>
#include <stdio.h>

char S=0;
unsigned char A=0, B=0, C=0, I=0, M=0, N=0, O=0, P=0, Q=0, R=0, X=0, Y=0, Z=0;
unsigned char rom[256] = {""")
    f.write(", ".join(map(str, rom)))
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
