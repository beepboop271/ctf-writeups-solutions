# x86 Assembly

***This is work in progress/draft. There may be very poorly written sections or incorrect information***

In the meantime, check out:

- [x64 Intro](https://cs.nyu.edu/courses/fall11/CSCI-GA.2130-001/x64-intro.pdf)
- [x64 Cheat Sheet](https://cs.brown.edu/courses/cs033/docs/guides/x64_cheatsheet.pdf)

(If you understand the topics after just reading these links then why are you even reading the pages I've written, clearly you already have a decent understanding)

---

Prerequisite topics: [C](https://gribblelab.org/CBootCamp/), more specifically just pointers

*Note: The images in this document are meant to viewed with a white background, though it is possible to view them on a dark background they may not look great. I wanted to keep the images transparent instead of having a solid white background though, so I made sure it's not impossible to read them on a dark background, it just might not look as good.*

---

## Obligatory Introduction

All software eventually runs on a CPU or some processor. However, CPUs can only process machine code, which is quite literally just a long sequence of numbers. To make things easier for humans to read and write, assembly languages simply swap out the numbers in machine code for commands and keywords which are much easier to understand.

The conversion between machine code and assembly is really a 1:1 swap between words to numbers, which is different from the conversion between a language like C into machine code, a process that involves a lot of optimization and code generation. This is the reason why converting an executable back into assembly is very easy, but converting an executable back into source code is a difficult and imperfect job.

Nowadays, the typical consumer laptop or desktop computer contains a CPU from Intel or AMD running what's called the "x86 instruction set architecture". The term instruction set refers to (believe it or not) what instructions, or operations, the processor is capable of performing, and how instructions should be encoded as machine code. Machine code from one instruction set will not run on another instruction set, because each set has its own machine code (e.g. the numbers `0x89 0xc3` could mean one operation in one set and a totally different operation in another, in addition, one processor might support an instruction that another doesn't support). You could imagine CPUs with different instruction sets it as different programming languages, where the exact syntax and features differ between languages, but most of the time the fundamentals are all there.

Instruction sets other than x86 are very common in other markets, for example phones from Apple and most (all?) Android phones run an ARM instruction set. Though the machine code for non-x86 processors will look very different from x86 machine code, the assembly code will probably be somewhat comparable (as the same basic concepts of assembly are generally common).

## Fun Fun Terminology

`x86` is a blanket term for all x86 related architectures. It also refers to 32 bit x86. `i386` is also another term for 32 bit x86, named after the first 32 bit x86 CPU, the Intel 80386. `x86-64` and `x64` both refer to 64 bit x86, and `amd64` also refers to 64 bit x86, named after AMD, the company who introduced the first 64 bit x86 CPU, the AMD Opteron.

- In general: `x86`
- 32 bit: `x86`, `i386`
- 64 bit: `x86-64`, `x64`, `amd64`

Note that even though `i386` and `amd64` reference a specific company, if you see an application download or something like that offering `i386` and `amd64` versions, it does not matter if you have and Intel or AMD CPU, but rather whether you are running 32 bit or 64 bit (most likely 64 bit).

## ~~Boring Fundamentals~~ General Stuff

### Registers

> Add 4 and 8, then subtract 2 from the result
>
> Is the value above greater than the result of 10 minus 3?

To compute the answer to that question, you probably mentally kept track of the different values, storing 12 somewhere, then turning that 12 into 10, and then comparing that 10 with a 7. Humans need "working memory" or very short term memory to perform computations.

Likewise, a CPU also needs something like working memory to do calculations (it calculates 10 and 7, but if the CPU can't put those numbers anywhere, how can it compare them?). This working memory has to be different from both long term storage and RAM, because to a CPU, RAM is **really slow**, and permanent storage is **really really slow**.

In order for a CPU to work fast, there are very small pieces of memory named registers that are physically on the CPU, very close to the circuits which perform calculations.

To get an idea of how slow the world outside of a CPU is, you can have a look at this table<sup id="a1">[1](#f1)</sup>:

```text
Latency Comparison Numbers (~2012)
----------------------------------
L1 cache reference                         0.5 ns
L2 cache reference                         7   ns          14x L1 cache
Main memory reference                    100   ns          20x L2 cache
Read 4K randomly from SSD*           150,000   ns  150 us
Read 1 MB sequentially from memory   250,000   ns  250 us
Round trip within same datacenter    500,000   ns  500 us
Read 1 MB sequentially from SSD*   1,000,000   ns    1 ms  4X memory
Disk seek                         10,000,000   ns   10 ms  20x datacenter roundtrip
Read 1 MB sequentially from disk  20,000,000   ns   20 ms  80x memory, 20X SSD
Send packet CA->Netherlands->CA  150,000,000   ns  150 ms

*~1GB/sec SSD
```

L1 and L2 cache are caches on the CPU that try to store frequently used or soon to be used pieces of information from RAM, so that if the CPU needs the information it doesn't need to wait for a RAM access. Though the registers and L1 cache are both on the CPU, the registers are even closer to the computation, and thus quicker to access.

### Instructions

A CPU contains many different circuits that each perform one small and specific operation. Each operation that the CPU is programmed to perform is called an "instruction". Each instruction is given an "opcode", short for operation code. The opcode of an instruction is a unique number to be used in machine code which can tell the CPU what specific calculation needs to be done. Each instruction is also given a short mnemonic code like "ADD" or "JMP" (jump), so that people can write assembly with words and not machine code with numbers. Each instruction can have operands (e.g. ADD takes two values to add), but some special instructions have no operands.

## *The* Stack

You may know what *a* stack is, but do you know what *the* stack (or *the* call stack) is? This section only covers *the* call stack at a high level, I'll get to how *the* stack looks in assembly later, so you can skip if you already know this.

First of all, *a* stack is an ordered data structure. In the simplest form *a* stack only has two operations: push (add) a value, and pop (remove/retrieve) the most recently added value. Since the most recently added element is always the one to be removed, stacks are called "LIFO", Last In First Out<sup id="a2">[2](#f2)</sup>.

![Pushing and popping to a stack](images/stack.png?raw=true)

One very useful application of *a* stack is to keep track of function calls when running a program. For example, look at the following Python program which does absolutely nothing useful:

```python
import random

def g(a, b):
    return (a*b) % (a+b)

def f(s):
    n = 0
    for char in s:
        n += g(ord(char), random.randint(0, 10))
    return n

print(f("hello"))
```

Every time you call a function (in a single threaded context), you pause execution in your current block of code and let the function run code until it returns control (and possibly a value) back to you. Every function call is independent, each with its own local scope which can hold local variables independent of local variables from all other function calls. These paused blocks of code execution can be stored perfectly with *a* stack.

The stack example above shows elements being added on the top, but just imagine the stack is flipped upside down for this example, meaning new elements appear on the bottom (this is due to two reasons, one of which will be revealed later and the other is because I'm using a table and you can't have headers on the bottom).

At the start of the program, before our `print`, this is what *the* stack looks like (imagine the global scope is a `main` function):

function | data
--- | ---
`main` | `random` = `module 'random' from 'C:\\Python38\\lib\\random.py'`<br>`g` = `function g at 0x0000015B0749AB80`<br>`f` = `function f at 0x0000015B0749CEE0`

Then, we encounter the `print` function. However, we are passing `f("hello")` into `print`, which means we need to evaulate `f("hello")` so that we know what to send the `print` function. This means we need to give up our control of code execution to the function `f` to let `f` figure out what the right value is. However, we don't want to start executing `main` from the beginning all over again and reset all our variables when we come back from `f`, and we don't want `f`'s variables interfering with `main`'s variables. In order to evaluate `f` but save our state in our current scope `main`, we can push and save all of `main`'s variables, as well as the exact location in `main` where we left off (so that we can return to the right place), in one block called a "stack frame", then push a new frame onto *the* stack, giving the new frame control of execution and its own separate local variables.

function | variables
--- | ---
`main` | `random` = `module 'random' from 'C:\\Python38\\lib\\random.py'`<br>`g` = `function g at 0x0000015B0749AB80`<br>`f` = `function f at 0x0000015B0749CEE0`<br><br>Paused execution on line 12, evaluating first argument of `print`<sup id="a3">[3](#f3)</sup>
`f` | Will return control to `main`, line 12 once finished<br>`s` = `"hello"`<br>`n` = `0`

Then, as we are executing `f` we encounter a function call to `g`. However, `g` takes two arguments and we are passing the results of two functions to `g`! Again, we save our current state on *the* stack and push a new frame. Side note: I'll assume the `ord` and `print` functions both call the first argument `x`, just for labelling purposes.

function | variables
--- | ---
`main` | `random` = `module 'random' from 'C:\\Python38\\lib\\random.py'`<br>`g` = `function g at 0x0000015B0749AB80`<br>`f` = `function f at 0x0000015B0749CEE0`<br><br>Paused execution on line 12, evaluating first argument of `print`
`f` | Will return control to `main`, line 12 once finished<br>`s` = `"hello"`<br>`n` = `0`<br>`char` = `'h'`<br><br>Paused execution on line 9, evaluating first argument of `g`
`ord` | Will return control to `f`, line 9 once finished<br>`x` = `'h'`

Then, as `ord` finishes its job of calculating, it returns with a value of `104`. In order to go back to the function `f` that called `ord`, we can pop the last stack frame of `ord` off *the* stack, and since we stored where the previous function was, we can return control back to the right spot.

function | variables
--- | ---
`main` | `random` = `module 'random' from 'C:\\Python38\\lib\\random.py'`<br>`g` = `function g at 0x0000015B0749AB80`<br>`f` = `function f at 0x0000015B0749CEE0`<br><br>Paused execution on line 12, evaluating first argument of `print`
`f` | Will return control to `main`, line 12 once finished<br>`s` = `"hello"`<br>`n` = `0`<br>`char` = `'h'`<br>`g_first_argument`<sup id="a4">[4](#f4)</sup> = `104`

Then, we evaluate the second argument:

function | variables
--- | ---
`main` | `random` = `module 'random' from 'C:\\Python38\\lib\\random.py'`<br>`g` = `function g at 0x0000015B0749AB80`<br>`f` = `function f at 0x0000015B0749CEE0`<br><br>Paused execution on line 12, evaluating first argument of `print`
`f` | Will return control to `main`, line 12 once finished<br>`s` = `"hello"`<br>`n` = `0`<br>`char` = `'h'`<br>`g_first_argument` = `104`<br><br>Paused execution on line 9, evaluating second argument of `g`
`randint` | Will return control to `f`, line 9 once finished<br>`min` = `0`<br>`max` = `10`

`randint` returns with `4` this time, we pop it off *the* stack to see that we should transfer control back to `f`, and we can then finally call `g` from `f`.

function | variables
--- | ---
`main` | `random` = `module 'random' from 'C:\\Python38\\lib\\random.py'`<br>`g` = `function g at 0x0000015B0749AB80`<br>`f` = `function f at 0x0000015B0749CEE0`<br><br>Paused execution on line 12, evaluating first argument of `print`
`f` | Will return control to `main`, line 12 once finished<br>`s` = `"hello"`<br>`n` = `0`<br>`char` = `'h'`<br><br>Paused execution on line 9, evaluating right hand side
`g` | Will return control to `f`, line 9 once finished<br>`a` = `104`<br>`b` = `4`

`g` returns with `92`, so we pop it off *the* stack and go back to `f`, which completes the first iteration of the loop.

function | variables
--- | ---
`main` | `random` = `module 'random' from 'C:\\Python38\\lib\\random.py'`<br>`g` = `function g at 0x0000015B0749AB80`<br>`f` = `function f at 0x0000015B0749CEE0`<br><br>Paused execution on line 12, evaluating first argument of `print`
`f` | Will return control to `main`, line 12 once finished<br>`s` = `"hello"`<br>`n` = `92`<br>`char` = `'e'`

I'll skip over the next iterations because they're the same thing. Eventually, we end on this:

function | variables
--- | ---
`main` | `random` = `module 'random' from 'C:\\Python38\\lib\\random.py'`<br>`g` = `function g at 0x0000015B0749AB80`<br>`f` = `function f at 0x0000015B0749CEE0`<br><br>Paused execution on line 12, evaluating first argument of `print`
`f` | Will return control to `main`, line 12 once finished<br>`s` = `"hello"`<br>`n` = `422`<br>`char` = `'o'`

Then, `f` returns with `422`, so we pop `f` off *the* stack and see that we return back to `main` to call `print`.

function | variables
--- | ---
`main` | `random` = `module 'random' from 'C:\\Python38\\lib\\random.py'`<br>`g` = `function g at 0x0000015B0749AB80`<br>`f` = `function f at 0x0000015B0749CEE0`<br><br>Paused execution on line 12, calling function
`print` | Will return control to `main`, line 12 once finished<br>`x` = `422`

Once `print` is done, it returns and gets popped, leaving us with just `main`. Since we have reached the end of the file, `main` returns and our stack is empty, telling us there is nowhere to transfer control to because our program has finished running.

## Some Size Terms

In case you didn't know, here are some terms you need to know:

- In General:
  - Bit: A single **b**inary dig**it**, either `0` or `1`
  - Byte: `8` bits, can be shortened to `b`
  - Word: The natural or standard size a certain processor uses, e.g. 16 bit, 32 bit, 64 bit
- In x86:
  - Word: `16` bits, or `2` bytes. Note that a "word" refers to 16 bits even on an x86-64 (64 bit) CPU
    - Can be shortened to `w`
  - Double Word: `32` bits, or `2` words
    - `dword`, or `l` for long
  - Quad Word: `64` bits, or `4` words
    - `qword`

## Operands

Assembly consists of instructions performing operations on operands. There are three different types of possible operands: registers, immediates, and memory addresses.

### x86 Registers

The first x86 processor (Intel 8086) was a 16 bit processor, so all the data registers were 16 bits or 2 bytes wide. The following were available registers:

- General Purpose Registers (GPRs)<br>Each register is two bytes wide: the upper byte could be accessed replacing `X` for `H`, and the lower byte with `L` (e.g. `AH`, `AL`)<br>Though the registers can be used for anything (hence the name "general purpose"), they were named with some uses in mind.
  - `AX`: Accumulator
  - `BX`: Base Index (i.e. the start of an array)
  - `CX`: Counter (like a loop)
  - `DX`: Data/Anything/Supplement AX<sup id="a5">[5](#f5)</sup>
  - `SI`: Source Index (for string operations)
  - `DI`: Destination Index
- The next two registers keep track of pointers that manage *the* call stack. I've only given a high-level overview, but I'll cover the assembly implementation of *the* stack later. These registers should generally only be used for their intended purpose.
  - `SP`: Stack Pointer. This holds the memory address of the **top-most *element*** in *the* stack (each stack frame has several elements inside it, like multiple local variables)
  - `BP`: Base Pointer. This holds the memory address of the **start of the current (top-most) stack *frame***, or the first element in the current frame
- `IP`: Instruction Pointer. This holds the memory address of the instruction that will be executed next. Automatically incremented to point to the next instruction after executing one, should probably never be touched. Tells you where in the program you are.
- `CS`, `DS`, `SS`, `ES`: Segment registers. Not really useful nowadays<sup id="a6">[6](#f6)</sup>.
- Flags register: Certain bits in the register are flags representing the state of the CPU. The main use is to create the assembly equivalent of `if` statements, performing an operation depending on whether certain flags are set.

Then, when 32 bit x86 processors were created, these registers were **e**xtended. Every register (except for the segment registers, which gained `FS` and `GS`) were made to have 32 bit versions: `EAX`, `EBX`, `ECX`, `EDX`, `ESI`, `EDI`, `ESP`, `EBP`, and `EIP`. All the registers from 16 bit x86 were kept for backwards compatibility, so to access the lower word of `EAX` you could use `AX`. In addition, the `H` and `L` single byte registers were kept too, so you could set the lowest byte of `EDX` with `DL`.

![32 bit registers](images/32-bit-registers.png?raw=true)

Note: the flags register is not directly accessible but some bits can be set manually if needed

The introduction of 64 bit x86 not only extended each register again (`RAX`, `RBX`, `RCX`, `RDX`, `RSI`, `RDI`, `RSP`, `RBP`, and `RIP`), maintaining all the 32 bit, 16 bit, and single byte registers from before, but also added 8 new GPRs: `R8`, `R9`, `R10`, `R11`, `R12`, `R13`, `R14`, and `R15`. Like the previous 4 GPRs (`RAX`, `RBX`, `RCX`, and `RDX`), you can access the lower dword, the lower word, and the lowest byte. However, you cannot access the second byte like you can on `AH`, `BH`, `CH`, or `DH` with these new registers.

In addition, the new GPRs have different names for their smaller versions. All you need to do is add the single letter suffix of the size you want. E.g:

- `R8`: 64 bits
  - `R8D`: 1 dword, lowest 32 bits
  - `R8W`: 1 word, lowest 16 bits
  - `R8B`: 1 byte, lowest 8 bits
- `R9`: 64 bits
  - `R9D`: 1 dword, lowest 32 bits
  - `R9W`: 1 word, lowest 16 bits
  - `R9B`: 1 byte, lowest 8 bits
- ... and on

The registers `RSI`, `RDI`, `RSP`, and `RBP` can also have their lowest byte accessed with `SIL`, `DIL`, `SPL`, and `BPL` on 64 bit x86.

![64 bit registers](images/64-bit-registers.png?raw=true)

Another Note: Even though flags was extended in 32 bit and 64 bit x86, the majority of the bits are not used for anything.

x86 processors can also have SSE and AVX instructions that operate on 128, 256, and even 512 bit registers, meant to hold several pieces of data in one register and execute operations on them in parallel. Reverse engineering challenges involving floating point numbers will probably see use of them.

### How are registers used?

Variables in languages like Java or C++ are statically typed, and can only contain a value or reference of the appropriate type. These are quite strict. Pointers in C allow you to do whatever you want to the memory, including things that will surely crash the program, but there are still static types for signed/unsigned, int/float (then again, [you can interpret the bits of a float as an int with pointers](https://en.wikipedia.org/wiki/Fast_inverse_square_root#Overview_of_the_code)).

Registers are basically uncontrolled pieces of memory. It is entirely up to the programmer to decide if a register's value should be interpreted as a signed int, unsigned int, or pointer. The only exception is with floating point numbers, which actually do need to be stored in registers that are designed to work with floating point instructions (this is pretty much all I'm going to write about floats in assembly because in my limited experience I have never seen problems extensively use them, also it seems like it would take a decent chunk of time to research as I have never touched floating point assembly before).

### Immediates

In high level languages, there are variables/constants, which we replace with registers and memory locations in assembly. High level languages also have number or string literals, constant values typed into the source of a program: `int n = 5` assigns the number literal 5 to `n`, `const char *s = "hi"` assigns a pointer to a string literal `"hi"` stored directly in the executable. Though strings are a bit more complicated in assembly (stored in data sections, then referenced from the main program), numeric literals can be used. However, they are called immediates in assembly. For example, `add rax, 5` adds the immediate `5` (base 10) to the value in `rax` (`rax += 5`).

### Memory

The final operand type is a memory address. The instruction `mov rax, rsi` (`mov` for move) is like saying `rax = rsi`, copying exactly the contents of the register `rsi` into the register `rax`. However, by adding square brackets `[]`, the instruction will instead refer to memory, completely changing the meaning (you can imagine `[]` being like the `*` dereference operation in C).

- `mov rax, [rsi]` is like `rax = *rsi`: treat `rsi` as a memory pointer, copying the 64 bits present at the memory address specified in `rsi` into `rax`
- `mov [rax], rsi` is like `*rax = rsi`, treat `rax` as a memory pointer, copying the contents of the `rsi` register into the memory location pointed to by `rax`.

When referencing memory, the assembler will try to automatically figure out how much memory to read. For example, `mov rax, [rdi]` has a 64 bit register, `rax`, as the destination, so it would read 8 bytes (64 bits) from the address specified in `rdi`. Likewise, `mov eax, [rdi]` would read 4 bytes, and `mov [rax], edi` would write 4 bytes.

Sometimes the assembler cannot infer the size, in which case you need to manually specify. For example `mov [rax], 0x1` could mean to move `0x01` (byte), `0x0001` (word), `0x00000001` (dword), or `0x0000000000000001` (qword). The size can be specified by writing the short form of the size, followed by the word "PTR" as follows:

Size | Instruction
--- | ---
1 Byte | `mov BYTE PTR [rax], 0x1`: Treat `rax` as a pointer to a byte, and copy `0x1` as a byte
2 Bytes | `mov WORD PTR [rax], 0x1`: Treat `rax` as a pointer to a word, and copy `0x1` as a word
4 Bytes | `mov DWORD PTR [rax], 0x1`: Treat `rax` as a pointer to a dword, and copy `0x1` as a dword
8 Bytes | `mov QWORD PTR [rax], 0x1`: Treat `rax` as a pointer to a qword, and copy `0x1` as a qword

Some people prefer to write the size directives on all operations, so that no inference needs to be done, e.g. `mov eax, DWORD PTR [rdi]` instead of just `mov eax, [rdi]` (this is also what disassemblers will do when converting machine code to assembly).

Other ways to generate memory addresses (called addressing modes) allow for indexing and offsetting. In 32 bit x86, memory can be addressed with `base_pointer + index*scale + displacement`. Any combination of at least one of those parts is valid. For example:

Mode | Instruction
--- | ---
Base | `mov eax, [esi]`
Scaled Index | `mov eax, [ecx*2]`
Displacement | `mov eax, [0x12345]`
Base + Scaled Index | `mov eax, [esi + ecx*4]`
Base + Displacement | `mov eax, [esi+5]`
Scaled Index + Disp. | `mov eax, [ecx*4 + 9]`
Base + Scaled Index + Disp. | `mov eax, [esi + ecx*8 + 0xc]`

Base can be `EAX`, `EBX`, `ECX`, `EDX`, `ESP`, `EBP`, `ESI`, or `EDI` (no small registers or `EIP`).

Index can be `EAX`, `EBX`, `ECX`, `EDX`, `EBP`, `ESI`, or `EDI` (no small registers, no `EIP`, no `ESP`).

Scale can be 1, 2, 4, or 8 (e.g. arrays containing bytes, shorts, ints...).

Displacement is a number, positive or negative.

In x64, base can be `RAX`, `RBX`, `RCX`, `RDX`, `RSI`, `RDI`, `RSP`, `RBP`, `R8`, `R9`, `R10`, `R11`, `R12`, `R13`, `R14`, or `R15` (no `RIP`, no smaller registers unless running in 32 bit mode in which case follow 32 bit rules which do not change, e.g. no `R8D` even in 32 bit mode).

Index can be all the registers that base is, except no `RSP`.

Scale and displacement are the same.

In 64 bit, an additional addressing mode is to use `RIP` relative addresses, e.g. `RIP + 0x2d45`. Note that you cannot use `RIP` with any of the other addressing modes as a base or index. Using `RIP` relative addressing allows for position independent code which will not be covered in this document. A disassembler is able to provide information to help understand where a `RIP` relative address is pointing to.

## x86 Syntax

There are two main ways of writing x86 assembly, Intel syntax and AT&T syntax. This article and repo exclusively uses Intel syntax (unless some challenge is given in AT&T, I guess), though it is good to be able to identify and still understand both variants.

Intel | AT&T
--- | ---
Reference registers by writing their name | Reference registers by writing `%`name
Order of operands is destination, source:<br>`add rax, rbx` is like saying `rax += rbx`<br>`mov rax, rbx` is `rax = rbx` | Order of operands is source, destination:<br>`add %rax, %rbx` is like saying `rbx += rax`<br>`mov %rax, %rbx` is `rbx = rax`
Type immediates directly into the program:<br>`add rax, 5` | Prefix all immediates with `$`:<br>`add $5, %rax`
Use [base + index*scale + disp] to address memory:<br>`mov [rbx + rcx*4 + 0x20], rax` | Use disp(base, index, scale) to address memory<br>(note that no `$` is placed on disp or scale):<br>`mov %rax, 0x20(%rbx, %rcx, 4)`
Use size directives to specify width of operands:<br>`mov BYTE PTR [rax], 0x1`<br>`mov WORD PTR [rax], 0x1`<br>`mov DWORD PTR [rax], 0x1`<br>`mov QWORD PTR [rax], 0x1` | Use size suffixes to specify width of operands:<br>`movb $0x1, (%rax)`<br>`movw $0x1, (%rax)`<br>`movl $0x1, (%rax)`<br>`movq $0x1, (%rax)`

In my opinion AT&T just looks really bad compared to Intel, with the unnecessary prefixes and strange addressing mode. The only thing it has going for it is the source, dest order, which some people prefer. It's not that difficult to get used to dest, source though (unless you've been reading source, dest your whole life or something).

## Looping, Branching, and Flags

You've probably heard of `goto` before but were told to never use it, since it's not easy to follow and can be replaced with ifs, loops, functions, returns, or even breaks, all of which are easier to read. However, in assembly, you really only have two tools (aside from functions) to manage control flow: unconditional jumps and conditional jumps.

An unconditional jump (instruction `jmp`) is exactly how it sounds: instead of incrementing the instruction counter<sup id="a7">[7](#f7)</sup> to move to the next instruction, jump to some specified instruction instead (basically `goto`).

Conditional jumps are more complicated... read on to see how they work.

Jumps can be absolute or relative, and a disassembler will provide labels or additional info to help you read the jump, such as writing what function the jump is to and the offset inside that function.

Loops and branches are fundamental components of any remotely complex program, so how are they implemented in assembly as jumps? First of all, let's try to break down what makes up an `if` statement.

```python
x = some_function()
if x > 0:   # condition
    x = -1  # conditionally executed code
print(x)    # unconditionally executed code
# ... more code
```

An `if` statement on its, shown above, has a condition. If the condition is `true`, we continue executing the next line of code. If the condition is `false`, we jump past the inner block and execute the code immediately after. Here's some weird pseudocode that's a mix between python and C while incorporating ideas of assembly:

```python
x = some_function()

if x > 0, continue, otherwise jump to label A
x = -1

A:
print(x)
# ... more code
```

Do note that if the computer doesn't jump to `A` and instead executes `x = -1`, it'll just reach `A` on the next instruction and execute it. It's not like an if/else. The computer will always advance one instruction at a time unless explicity told to jump.

Here's a more complicated example to further demonstrate the idea of jumping after conditions (it really doesn't matter if you understand the python or not, I was just writing random useless lines):

```python
y = function_returning_list()
if len(y) == 0:
    # generate a list of random numbers
    print("empty")
    y = [random.random() for i in range(50)]
elif len(y) > 100:
    # randomly discard some elements
    print("long")
    y = [n for n in y if random.random() > 0.5]
else:
    # double the list (extend list with a copy)
    print("not long")
    y *= 2
print("this will always be printed")
```

```python
y = function_returning_list()

if len(y) == 0, continue, otherwise jump to label A
print("empty")
y = [random.random() for i in range(50)]
jump to C unconditionally

A:
if len(y) > 100, continue, otherwise jump to label B
print("long")
y = [n for n in y if random.random() > 0.5]
jump to C unconditionally

B:
print("not long")
y *= 2

C:
print("this will always be printed")
```

Hopefully now you can see the uses of conditional and unconditional jumps for if statements. Notice how the unconditional jumps are used to make sure only one branch of the if/else if/else block is executed.

What about more complicated conditions? This block:

```python
if check_something(x) and (not other_check(x)) and (y < -40 or y >= 5):
    do_something()
print("end")
```

can be rewritten with single condition checks like this (replace and with nested ifs and replace or with if/else if chains):

```python
if check_something(x):
    if not other_check(x):
        if y < -40:
            do_something()
        elif y >= 5:
            do_something()
print("end")
```

and finally converted to jumps like this:

```python
x = get_value()
y = get_other_value()

if check_something(x) == True, continue, otherwise jump to label B
if other_check(x) == False, continue, otherwise jump to label B
if y >= -40, continue, otherwise jump to label A
if y >= 5, continue, otherwise jump to label B

A:
do_something()

B:
print("end")
```

Notice that we inverted the condition and wrote `if y >= -40`. This is so that we only have to write the code for `do_something()` once. If `y` is less than `-40`, it will immediately jump to `do_something()`. Otherwise, it will continue checking the other condition.

Here is another example of a longer chain to further demonstrate this else-if jumping.

```python
y = maybe_get_int()
if (y is not None) and (y < -40 or y == 0 or y >= 5):
    do_something()
else:
    print("no")
print("end")
```

```python
y = maybe_get_int()
if y is not None, continue, otherwise jump to B
if y >= -40, continue, otherwise jump to A
if y != 0, continue, otherwise jump to A
if y >= 5, continue, otherwise jump to B

A:
do_something()
jump to C unconditionally

B:
print("no")

C:
print("end")
```

Okay. I hope that was enough examples to get the idea of jumps across. Now I'll introduce conditional jumps in assembly.

### The Flags Register

As mentioned before, the flags register contains certain boolean flags representing states in the CPU. Specifically, some instructions are made to update certain flags. After the CPU executes one of these instructions, each flag the instruction is supposed to upddate will be cleared or set to reflect the work done by the instruction.

The flags we care about are as follows:

- `ZF`: Zero Flag
- `SF`: Sign Flag
- `OF`: Overflow Flag
- `CF`: Carry Flag

For example, the `add` instruction affects all of the flags mentioned (and more). When you run something like `add rdx, rax`, the CPU will "check":

- `ZF`: Set to `1` if the result of the operation was `0`, otherwise cleared to `0`
- `SF`: Set to equal the most significant/sign bit of the result (i.e. `1` if negative result, `0` if positive)

#### The Carry Flag

The carry flag is set every time math instructions like `add` are used. `CF` can be used to help in doing math, but for the purposes of this document we'll only look at how flags are used for comparison. The CPU always updates `CF` after applicable instructions, even though we only care about `CF` when using unsigned operands (since the CPU doesn't know if we're signed or unsigned). `CF` is also modified by more than just `add` and `sub` (subtract), but I'll only go over those two here.

`CF`: Short explanation (i.e. explanation without binary math)

For addition, the carry flag is set when the sum of two registers is larger than the size of the registers used, i.e. when the addition creates a carry past the end of the register.

Decimal example: suppose you can only store two digit decimal numbers, but wanted to add 82 and 24. `2 + 4` makes 6, so the ones digit is 6. However, `8 + 2` makes 10, so the tens digit is 0 (the result of the addition is just 6) and the 1 carries past the end of our two digit register. This would set `CF`.

For subtraction, the carry flag is set when subtracting two numbers results in a "borrow" from past the end of the register.

Decimal example: suppose you wanted to subtract 51 from 12. `2 - 1` is 1, so the ones digit is 1. However, `1 - 5` would be negative, but you can't borrow, because there are no more digits left to borrow from, thus `CF` is set (this explanation is not exactly accurate but good enough, read the long explanation for accuracy).

The absolute minimum you need to know about `CF` is that it is used with unsigned comparison, and so subtraction of `a - b` with `b > a` will result in `CF` being set because you can't produce a negative result with unsigned integers.

[skip past long explanation](#The-Overflow-Flag)

`CF`: Long explanation (prerequisite topics: subtraction and negative binary numbers using two's complement)

When adding 2 two digit numbers like 82 and 24, we end up with the result 106. Adding the tens digits 8 and 2 caused us to write down `0` as the sum, then bring a carry digit of `1` into the hundreds digit. Though carry is not an issue for us when we do math in decimal on paper, when a CPU only has a fixed amount of bits to work with, carry can be an issue. For example, if you had an 8 bit register and wanted to add together `240 + 53`:

```text
  11110000
+ 00110101
----------
      0101
```

The first few bits were simple, but next we have `1 + 1`. This is two, which is `10`. We write down `0` and carry the `1`. This results in `1 + 1 + 1`, or three, `11`. We write down `1` and carry the `1`.

```text
  111
  11110000
+ 00110101
----------
1 00100101
```

The 8 bit result we get is 37, which is clearly wrong. However, if we kept track of whether or not something was carried past the MSB (most significant bit<sup id="a8">[8](#f8)</sup>), we would be able to know if our answer is wrong and set `CF`.

Subtraction, on the other hand, is different. In addition, `CF` is set if the addition operation caused a carry past the MSB. In subtraction, `CF` is set if the subtraction *didn't* cause a carry past the MSB.

Here's an example of a "typical" (i.e. `a - b`, `a > b`) unsigned subtraction: `114 - 42`

```text
                  111 1111
  01110010        01110010
- 00101010  =>  + 11010101
----------      ----------
                1 01001000
```

The 8 bit result was 72, which is the correct result to `114 - 42`. Notice that getting the correct result relies on the fact that we cut off the carry bit to keep our result in 8 bits. However, this is what happens when we try to do unsigned subtraction that results in a negative number: `42 - 114`:

```text
                     11111
  00101010        00101010
- 01110010  =>  + 10001101
----------      ----------
                0 10111000
```

The carry bit wasn't set this time, and the result was 184, which is not `42 - 114`. It turns out that whenever the carry *bit* is not set, the unsigned subtraction is incorrect (because the subtrahend was larger than the minuend i.e. `a - b`, `b > a`). Thus, the carry *flag* is set whenever the carry *bit* is unset, which occurs when we are subtracting a larger number from a smaller one.

#### The Overflow Flag

Like `CF`, the overflow flag is involved in math instructions like `add`. The CPU always updates `OF` after applicable instructions, even though we only care about `OF` when using signed operands. `OF` is also modified by more than just `add` and `sub` (subtract), but I'll only go over those two here.

Do note that interpreting "overflow flag" as the flag that is set when a value "overflows" is not exactly correct, because the carry flag could also be described like that.

Without going into how negative binary numbers are actually implemented, suffice it to say that the first bit of a number is its sign, as described for the sign flag.

The range of a signed byte is -128 to 127, so if the addition or subtraction of two numbers produces a result outside of that range, the resulting byte will be incorrect.

If you think about it, the addition of two signed bytes with different signs will never produce a result outside of the signed byte range:

- positive plus a negative (0 + (-128) = -128)
- positive minus a positive (same as previous)
- negative plus a positive (-1 + 127 = 126)
- negative minus a negative (same as previous)

However, addition of two signed bytes with the same sign might go out of range:

- positive plus a positive (127 + 127 = 254)
- positive minus a negative (same as previous)
- negative plus a negative (-128 + (-128) = -256)
- negative minus a positive (same as previous)

When the result of an operation goes out of range, what will end up happening is the sign bit will flip<sup id="a9">[9](#f9)</sup>. Therefore, whenever two numbers of the same sign are added together (or two numbers of differing signs are subtracted), and the sign bit of the result is not the same as the original sign (or the original sign of the destination, in the case of subtraction), we know there is an error, and so `OF` is set.

### The `cmp` Instruction

If instructions like `add` and `sub` change the flags, we can use the flags to figure out how the two operands to `add` and `sub` were ordered relative to each other (e.g. if `a - b` turns on `ZF`, we know `a == b`, because `a - b = 0` is only true if `a == b`). However, executing an instruction like `sub rax, rdx` is like saying `rax -= rdx`, actually changing the value stored in `rax`. Introduce the `cmp` instruction: `cmp rax, rdx` *performs* the subtraction `rax - rdx`, and updates the flags according to the result, but *doesn't store* the result anywhere.

### Conditional Jumps

Here are the most important conditional jumps. Notice that each instruction has multiple written forms, for example `jne` is just an alias for `jnz` and they are both the same thing.

For the explanations, assume `cmp al, dl` was right before each jump instruction.

Also, you don't really need to know the explanations, I just thought it would be weird to list all the conditional jump instructions without talking about `cmp`, and I thought it would be weird to talk about how you have to put a `cmp` before a conditional jump without explaining flags.

|| Signed? | Flags&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Explanation
--- | --- | --- | ---
`je`<br>`jz`   | Both     | `ZF == 1`             | Jump if Equal / Jump if Zero<br>If `al - dl = 0`, they must be equal.
`jne`<br>`jnz` | Both     | `ZF == 0`             | Jump if Not Equal / Jump if Not Zero<br>Opposite of previous. If `al - dl != 0`, they must not be equal
||||
`jb`<br>`jnae` | Unsigned | `CF == 1`             | Jump if Below / Jump if Not Above or Equal<br>If `al - dl` set the carry flag, that means an incorrect unsigned subtraction was made. This only happens when the unsigned numbers become negative. `al - dl` is only negative when `dl` is larger than `al`, thus `jb` will jump when `al` is smaller than `dl`
`jnb`<br>`jae` | Unsigned | `CF == 0`             | Jump if Not Below / Jump if Above or Equal<br>Opposite of previous. `CF == 0` means that the subtraction was valid, i.e. the result was non-negative (positive or 0). That means `al > dl` (positive) or `al == dl` (0).
`jbe`<br>`jna` | Unsigned | `CF == 1 || ZF == 1`  | Jump if Below or Equal / Jump if Not Above<br>`CF == 1` is the same as `jb`. Adding the `|| ZF == 1` just means to jump if below or equal.
`jnbe`<br>`ja` | Unsigned | `CF == 0 && ZF == 0`  | Jump if Not Below or Equal / Jump if Above<br>Opposite of previous. Same as `jae`, but makes sure `ZF == 0` to exclude the "equals" part.
||||
`jl`<br>`jnge` | Signed   | `SF != OF`            | Jump if Less / Jump if Not Greater or Equal<br>If `OF == 0`, the calculation is valid. If a valid result has `SF == 0`, that means it is non-negative. If `al - dl` is non-negative, that means `al >= dl`. However, `SF == 1` would mean `al - dl` is negative, so if `OF == 0`, `SF == 1` for `al < dl`.<br>If `OF == 1`, the calculation went out of bounds. If `SF == 1` as well, that means the result was too high (`> 127`) and became negative. This must mean `dl` is negative, since subtracting a negative is the only way to create an addition that gets too high. If `dl` is negative, the only way `al` could be lesser is if it was more negative. However, if `al` was more negative, the difference would never overflow by being too high, thus `al` cannot be less if `OF == 1 && SF == 1`. However, if `OF == 1` and `SF == 0`, that means the overflow happened from a value too low (`< -128`), which means `dl` has to be positive (to subtract from `al`). If `dl` is positive, `al` must be negative or else it wouldn't have gone past -128 and set `OF`, so if `OF == 1`, `SF == 0` for `al < dl`.
`jnl`<br>`jge` | Signed   | `SF == OF`            | Jump if Not Less / Jump if Greater or Equal<br>Opposite of previous. `OF == 0 && SF == 0` means a valid calculation produced `al - dl >= 0`, or `al >= dl`. `OF == 1 && SF == 1` means the subtraction became invalid by overflowing too high (`> 127`), so `dl` was negative, and `al` was non-negative, so `al > dl`.
`jle`<br>`jng` | Signed   | `SF != OF || ZF == 1` | Jump if Less or Equal / Jump if Not Greater<br>`SF != OF` is the same as `jl`. Adding the `|| ZF == 1` just means to jump if less or equal.
`jnle`<br>`jg` | Signed   | `SF == OF && ZF == 0` | Jump if Not Less or Equal / Jump if Greater<br>Opposite of previous. Same as `jge`, but makes sure `ZF == 0` to exclude the "equals" part.

[Find more jumps here.](http://unixwiz.net/techtips/x86-jumps.html)

### The `test` instruction

Another very common instruction to see before a conditional jump is something like `test rax, rax`. The `test` instruction performs bitwise AND on the operands, but like the `cmp` instruction, it doesn't store the result anywhere. `test` modifies `ZF`, `SF`, and more. Since the bitwise and of two identical values is just the value itself, `test rax, rax` will only set `ZF` if `rax == 0` and `SF` if `rax < 0`.

`test rax, rax` [essentially replaces](https://stackoverflow.com/questions/33721204/test-whether-a-register-is-zero-with-cmp-reg-0-vs-or-reg-reg) `cmp rax, 0`.

### Branching Revisited

I'll just redo some examples from before, but with conditional jumps.

**Note that I use `mov rax, fake_function()`, but this is not how functions work in assembly. I'll get to those after loops.**

```python
y = function_returning_list()
if len(y) == 0:
    # generate a list of random numbers
    print("empty")
    y = [random.random() for i in range(50)]
elif len(y) > 100:
    # randomly discard some elements
    print("long")
    y = [n for n in y if random.random() > 0.5]
else:
    # double the list (extend list with a copy)
    print("not long")
    y *= 2
print("this will always be printed")
```

```x86asm
y = function_returning_list()

mov rax, len(y)
; Jump if Not Zero
; Jump to ELIF if ZF != 1 (rax != 0)
; If ZF == 1 (rax == 0), continue
test rax, rax
jnz ELIF

print("empty")
y = [random.random() for i in range(50)]
jmp END

ELIF:
; Jump if Not Above (Jump if Below or Equal)
; Jump to ELSE if rax <= 100 (If rax > 100, continue)
cmp rax, 100
jna ELSE

print("long")
y = [n for n in y if random.random() > 0.5]
jmp END

ELSE:
print("not long")
y *= 2

END:
print("this will always be printed")
```

<sup id="a10">[10](#f10)</sup>

It might take a bit to get used to all the inverted conditions: instead of `if rax > 100` now you have to do "jump `if rax <= 100`". Here's another example.

```python
if check_something(x) and (not other_check(x)) and (y < -40 or y >= 5):
    do_something()
print("end")
```

```python
if check_something(x):
    if not other_check(x):
        if y < -40:
            do_something()
        elif y >= 5:
            do_something()
print("end")
```

```x86asm
mov rbx, x
mov rcx, y

mov rax, check_something(rbx)
; Jump if Zero
; Jump to END if ZF == 1 (rax == 0 i.e. false)
; If ZF != 1 (rax != 0 i.e. true), continue
test rax, rax
jz END

mov rax, other_check(rbx)
; Jump if Not Zero
; Jump to END if ZF != 1 (rax != 0 i.e. true)
; If ZF == 1 (rax == 0 i.e. false), continue
test rax, rax
jnz END

; Skip to do_something() if rcx < -40,
; boolean OR, no need to check the other range
; if we already know one side is true

; Jump if Less (Jump if Not Greater or Equal)
; Jump to SUCCESS if rcx < -40 (If rcx >= -40, continue checking)
cmp rcx, -40
jl SUCCESS

; Skip to the end if rcx < 5 (both parts of the OR
; were false, which makes the whole if condition false)

; Jump if Less (Jump if Not Greater or Equal)
; Jump to END if rcx < 5 (If rcx >= 5, continue)
cmp rcx, 5
jl END

SUCCESS:
do_something()

END:
print("end")
```

<sup id="a11">[11](#f11)</sup>

Here's the last example. Have you been skimming through these examples? I feel like that would not be wise if you've never learned assembly before, these jumps are pretty annoying to get used to after dealing with if statements for years. I won't write super verbose comments anymore for jumps:

```python
y = maybe_get_num()
if (y is not None) and (y < -40 or y == 0 or y >= 5):
    do_something()
else:
    print("no")
print("end")
```

`None` is a special singleton object in python, so all `None`s have the same address. Let's just assume comparing to `None` is the same as comparing to a certain address

```x86asm
mov rax, maybe_get_num()
cmp rax, 0x123456789
; Jump if Equal
; If the address of rax and None are equal, rax is None
je ELSE

; Jump if Less (Jump if Not Greater or Equal)
cmp rax, -40
jl SUCCESS
; Jump if Zero
test rax, rax
jz SUCCESS
; Jump if Less (Jump if Not Greater or Equal)
cmp rax, 5
jl ELSE

SUCCESS:
do_something()
jmp END

ELSE:
print("no")

END:
print("end")
```

This time gcc structured the code the same way as my direct conversion (though it applied the range optimization from the last example).

### Loops

Hopefully by now you can figure out a conditional jump because all control flow is made of jumps in assembly.

#### Do-While Loop

The only real difference between the do-while loop and if statements is that an if branch jumps forwards in code, while the loop jumps backwards. If you figured out jumps with the examples for if statements, these loops should be easy.

```c
int n = k;
do {
    n += k*2 + 5;
    printf("%d\n", n);
} while (n < 100);
printf("%d\n", n);
```

```x86asm
; edx will be k. Note that I wrote
; these examples as if k was a function
; parameter and some value you could
; just mov into a register. This is not
; exactly how functions work, you'll see
; later
mov edx, k
; eax will be n
mov eax, edx

; Pre-compute k*2 + 5 so that we
; don't need to do unnecessary
; calculation in the loop
add edx, edx
add edx, 5

START:
add eax, edx
printf("%d\n", eax)
cmp eax, 100
jl START

printf("%d\n", eax);
```

#### While Loop

A while loop might run 0 times, as opposed to a do-while loop which runs at least once. To implement this, we need a conditional jump before the start of the loop to skip everything.

```c
int n = k;
while (n < 100) {
    n += k*2 + 5
    printf("%d\n", n);
}
printf("%d\n", n);
```

```x86asm
; edx will be k
mov edx, k
; eax will be n
mov eax, edx

; Continue to the loop only if n < 100
; Notice that instead of moving the
; loop's conditional jump to the top
; we add this jump before the loop
cmp edx, 100
jge END

; Pre-compute
add edx, edx
add edx, 5

START:
add eax, edx
printf("%d\n", eax)

cmp eax, 100
jl START

END:
print(eax)
```

If we were to move the conditional jump to the top, there would be an additional unconditional jump at the bottom, which means we need to execute more instructions per each loop iteration. Given that the extra jump to skip the whole loop would only be executed once, it makes sense to add that jump and keep the conditional at the bottom. If we didn't choose to add an extra jump and moved the conditional to the top, the more iterations our loop runs, the more unnecessary unconditional jumps we perform.

It is possible to have a loop with the top conditional jump and an extra bottom unconditional jump, but [putting the conditional jump at the bottom is basically standard practice](https://stackoverflow.com/questions/47783926/why-are-loops-always-compiled-into-do-while-style-tail-jump). Here's the example from above but with a conditional jump at the top and an unconditional jump at the bottom:

```x86asm
; edx = k
mov edx, k
; eax = n
mov eax, edx

; We have to pre-compute outside the loop
; this time. This means that we waste a bit
; of time precomputing in the case that the
; loop runs 0 times
add edx, edx
add edx, 5

; Notice that the loop body has more
; instructions than last time (extra jmp).
; However, the program as a whole is shorter
; by a bit without that jump at the top to
; skip everything
START:
cmp eax, 100
jge END

add eax, edx
printf("%d\n", eax)
jmp START

END:
print(eax)
```

#### For Loop

```c
int n = k;
for (int i = 0; i < k; ++i) {
    n += k*2 + i;
    printf("%d\n", i);
}
printf("%d\n", n);
```

```x86asm
; edx will be k
mov edx, k
; eax will be n
mov eax, edx

; if k <= 0, the for loop will run 0 times,
; so skip to the end
test edx, edx
jle END

; ebx will store the original value of k
; (to use for comparison)
mov ebx, edx
; edx will store k*2 (to add in the loop)
add edx, edx

; ecx will be i
mov ecx, 0

START:
add eax, edx
add eax, ecx

printf("%d\n", ecx)

; ++i
add ecx, 0x1

; loop again if ecx != ebx
; we know ecx must have started < ebx, so if
; ecx == ebx, that means ecx is no longer < ebx
cmp ecx, ebx
jne START

END:
printf("%d\n", eax)
```

Here's the for with the conditional jump at the top, once again there is an extra `jmp` in the loop code compared to the bottom conditional loop:

```x86asm
mov edx, k
mov ebx, edx  ; ebx = k
add edx, edx  ; edx = k*2

mov eax, ebx  ; eax = n = k
mov ecx, 0    ; ecx = i = 0

START:
; end if i >= k
cmp ecx, ebx
jge END

; n += k*2 + i
add eax, edx
add eax, ecx

printf("%d\n", ecx)

; ++i
add ecx, 1
jmp START

END:
printf("%d\n", eax)
```

## Functions and Calling Conventions: *The* Stack Revisited

In the previous section, I wrote function calls in the assembly examples just like you would in a high level language. However, of course, it is not that simple in assembly. In fact, it is so not-simple that calling a function written with conventions of 32-bit assembly will just not work at all if you use 64-bit function conventions.

In addition, this is a *convention*. There isn't anything physically preventing you from having your own way to call function in your programs. The convention solely exists so that other people can assume how to use your functions and so that you can assume how to use other functions. In fact, the convention in this document is just the way Unix-like ope

### 32-bit

### 64-bit

## Instructions that are good to know but haven't been mentioned already

---

<b id="f1">1</b> [Table source](https://gist.github.com/jboner/2841832). Do note that searching "Latency numbers every programmer should know" results in variations on the same table, such as [this one that tries to make the timescales easier to understand](https://gist.github.com/hellerbarde/2843375). [↩](#a1)

<b id="f2">2</b> Some people also call them "FILO" for First In Last Out, though I think that's less clear than LIFO (and for the reverse, queues, FIFO is definitely more clear than LILO). [↩](#a2)

<b id="f3">3</b> When the code is actually being run on the CPU, lines of code are converted in to CPU instructions. When you have a line of code like `n += g(ord(char), random.randint(0, 10))` that does many things, writing the exact return location isn't very clear. However, this line would be split up into many separate instructions that each do one thing and one thing only. Since each instruction has a different location in the program, it is possible to specify an exact instruction to return to. This hopefully should be clear by the time you finish this document. [↩](#a3)

<b id="f4">4</b> The program doesn't actually create a new local variable when you nest function calls like this. Again, the explanation for where the result is really stored will be revealed later in this document (well, I guess since this footnote is at the end it's technically before...). [↩](#a4)

<b id="f5">5</b> DX was (and still is) able to "merge" with AX into one larger register. In 16 bit days, the DX:AX register pair could hold 32 bits of information, EDX:EAX could hold 64 bits, etc.

For some fun reading after reading the whole lesson, look at the [cdq](https://www.felixcloutier.com/x86/cwd:cdq:cqo) instruction. See how EDX:EAX or RDX:RAX is used in [division](https://www.felixcloutier.com/x86/idiv) to store large operands and in [multiplication](https://www.felixcloutier.com/x86/imul) to store large products. [More info, I guess](https://stackoverflow.com/questions/36464879/when-and-why-do-we-sign-extend-and-use-cdq-with-mul-div). In additon, take a look at this snippet of code:

```c
int x = get_int();
printf("%d\n", x < 0 ? 255 : 0);
```

For me, on Ubuntu 18.04, gcc 7.5.0, at all optimization levels other than `O0`, the above code assembled to use the `cdq` instruction in a manner like this:

```x86asm
call whatever  ; eax will have the int returned from the function
cdq            ; sign extend eax into edx:
               ;   if eax is positive, fill edx with 0
               ;     pretending we have 4 bit registers:
               ;     0001 (1) becomes 0000 0001 (1)
               ;   if eax is negative, fill edx with 1
               ;     pretending we have 4 bit registers:
               ;     1011 (-5 in 4 bit) becomes 1111 1011 (-5 in 8 bit)
               ; this creates a 64 bit signed int edx:eax
movzx edx, dl  ; since edx will be either filled with 0 or 1, zero extend
               ; dl, the lowest byte, into edx. if edx is filled with 0,
               ; zero extending dl = 0 will just keep edx as 0. however,
               ; if edx is filled with 1, zero extending dl = 11111111 will
               ; replace the higher bytes of edx with 0, leaving only 255
               ; in edx.
```

Compare the assembly with `cdq` to one using branches:

```x86asm
call whatever
test eax, eax
jns .A         ; jump if the sign flag is 0, i.e. jump if non-negative
mov edx, 0xff
jmp .B
.A:
xor edx, edx
.B:
; ... more code
```

How often will you actually see `cdq` used to do something like this? Who knows, I just thought it was cool to share.

[↩](#a5)

<b id="f6">6</b> 16 bit x86 processors could only store 16 bits in their data registers. A 16 bit piece of data can only address 64 KiB of RAM, but the CPUs were wired up so that they could be capable of being used with 20 bits of memory (1 MiB). Segment registers were used to split up memory into *segments*. Blocks of up to 64 KB in size were created within the 1 MiB of RAM. The 16 most significant bits of the 20 bit starting address would be stored in a segment register, allowing the 16 least significant bits to be stored in a data register and used as an offset to reference any address within that block. Four segment registers meant that you could use four 64 KiB blocks in your 16 bit program. However, nowadays 64 bit CPUs exist. If all 64 bits were used, you could address 16 *exbibytes* of RAM. This is absolutely pointless and CPUs (currently) only use 48 bits (which still is capable of 256 TiB). [↩](#a6)

<b id="f7">7</b> Each instruction actually takes up a variable amount of space, with some instructions only needing a single byte and some taking up 5, 6, or more bytes. This is because you first need to encode what operation to do, then any arguments, and things like immediates or memory addresses need to be encoded in the instruction. So "incrementing" doesn't necessarily mean `++RIP`. [↩](#a7)

<b id="f8">8</b> The most significant bit is the bit in a binary number with the highest "value". For example, when we write decimal numbers, the ones digit is the rightmost. Then each digit on the left is "worth" 10 times more than the one to the right, i.e. an increase of 1 in the tens digit is worth 10 increases of the ones digit. Likewise, each bit on the left is worth twice as much as the one to the right. Thus, the most significant bit is the leftmost and the least significant bit is the rightmost. However, this might not always be the case in some very specific low level situations, which is why "most significant bit" or "most significant digit" is better than "leftmost digit" [↩](#a8)

<b id="f9">9</b> I didn't want to add a long explanation that just shows the bit flipping, so I'll do it in a footnote.

A positive integer will always have the MSB as `0`, because if it was `1` that would mean it is a negative integer. If we add two positive integers together and their sum is too large to fit in the amount of bits available, there will be a carry into the MSB, setting it to 1, turning the number negative. Example: `24 + 95` vs `83 + 58` (or `24 - (-95)` vs `83 - (-58)`)

```text
    11          |   111  1
  00011000  24  |   01010011  83
+ 01011111  95  | + 00111010  58
----------      | ----------
  01110111  119 |   10001101  -115
```

On the other hand, two negative numbers wil always have the MSB as `1`. If we add those two MSBs together, the two `1`s become a `0`, unless there was also a carry into the MSB (like in the left example). If the right 7 bits do not have enough magnitude (i.e. the numbers are very low like in the right example), the sum won't be enough to carry into the MSB, thus the number turns positive.

```text
  1 11 1        |    1111
  11001010  -54 |   10110110  -74
+ 11011010  -38 | + 10111101  -67
----------      | ----------
1 10100100  -92 | 1 01110011  115
```

[↩](#a9)

<b id="f10">10</b> When I actually compiled a similar version of this example, gcc organized the code a bit differently:

```x86asm
y = function_returning_list()
mov rax, len(y)

; Jump if Zero
; Jump to FIRST_SUCCESS if ZF == 1 (rax == 0)
; If ZF != 1 (rax != 0), continue
test rax, rax
jz FIRST_SUCCESS

; Jump if Above (Jump if Not Below or Equal)
; Jump to SECOND_SUCCESS if rax > 100 (if rax <= 100, continue)
cmp rax, 100
ja SECOND_SUCCESS

print("not long")
y *= 2

END:
print("this will always be printed")
; note: The C code I wrote to test this example was in
; a function, and returned after this line. Maybe it
; would have been organized differently if there was more?
; Or it could just jump away to somewhere else after here.

SECOND_SUCCESS:
print("long")
y = [n for n in y if random.random() > 0.5]
jmp END

FIRST_SUCCESS:
print("empty")
y = [random.random() for i in range(50)]
jmp END
```

I guess this is more readable compared to the assembly I wrote directly converted from python? Doesn't seem more efficient

[↩](#a10)

<b id="f11">11</b> Again, gcc organized the code differently. In addition, the range check was optimized:

```x86asm
mov rbx, x
mov rcx, y

mov rax, check_something(rbx)
; Jump if Not Zero
; Jump to OTHER_CHECKS if ZF != 1 (rax != 0 i.e. true)
; If ZF == 1 (rax == 0 i.e. false), continue
test rax, rax
jnz OTHER_CHECKS

END:
print("end")
; Again, it returned here in my C code.

OTHER_CHECKS:
mov rax, other_check(rbx)
; Jump if Not Zero
; Jump to END if ZF != 1 (rax != 0 i.e. true)
; If ZF == 1 (rax == 0 i.e. false), continue
test rax, rax
jnz END

; Originally, the condition was y < -40 || y >= 5
add rcx, 40  ; Add 40. y < 0 || y >= 45
cmp rcx, 44  ; Compare to 44
; Jump if Not Above (Jump if Below or Equal)
; Notice jna is an unsigned instruction!
; All valid negative numbers were shifted so that
; -41 became -1. Then, invalid negative numbers became
; small positive numbers. By treating rcx as an
; unsigned integer, all the negative numbers suddenly
; appear to be very large positive numbers. Thus, if
; rcx is not above 44 (within [0, 45)), y must be
; within [-40, 5) and thus be rejected.
jna END

do_something()
jmp END
```

[↩](#a11)

<b id="f12">12</b> hi [↩](#a12)

<b id="f13">13</b> hi [↩](#a13)

<b id="f14">14</b> hi [↩](#a14)

