# bubbly

> It never ends
>
> `nc 2020.redpwnc.tf 31039`

Provided file: `bubbly`

Prerequisite topics: [Reversing Basics](https://github.com/beepboop271/ctf-writeups-solutions/tree/master/general%20resources/rev%20and%20pwn/rev-basics.md)

## Investigation

Let's start off with `file bubbly`<sup id="a1">[1](#f1)</sup>:

```text
bubbly: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/l, for GNU/Linux 3.2.0, BuildID[sha1]=edb56d2d9355bcee01909f171d8a272a3e82d053, not stripped
```

So it's just a 64-bit ELF<sup id="a2">[2](#f2)</sup> (linux executable). We'll grant execution permission and then run it.

`chmod +x bubbly`<sup id="a3">[3](#f3)</sup>

`./bubbly`<sup id="a4">[4](#f4)</sup>

```text
I hate my data structures class! Why can't I just sort by hand?
asdf
Try again!
```

```text
I hate my data structures class! Why can't I just sort by hand?
4
25
Try again!
```

```text
I hate my data structures class! Why can't I just sort by hand?
5
5
5
5
3
9
Try again!
```

It looks like the file takes numbers, but there isn't much we can figure out without looking at the program itself. I'll start off with [Ghidra](https://ghidra-sre.org/).

After opening the ELF and analysing it with default options, we can see that there is a `main` function available to us. We'll start there, and have a look at the decompiled code.

```c
int main(void) {
  uint32_t i;
  int unused;
  _Bool pass;

  setbuf(stdout,(char *)0x0);
  setbuf(stdin,(char *)0x0);
  setbuf(stderr,(char *)0x0);
  puts("I hate my data structures class! Why can\'t I just sort by hand?");
  pass = false;
  while( true ) {
    __isoc99_scanf(&DAT_00102058);
    if (8 < i) break;
    nums[i] = nums[i] ^ nums[i + 1];
    nums[i + 1] = nums[i + 1] ^ nums[i];
    nums[i] = nums[i] ^ nums[i + 1];
    pass = check();
  }
  if (pass == false) {
    puts("Try again!");
  }
  else {
    puts("Well done!");
    print_flag();
  }
  return 0;
}
```

This program seems quite simple. It looks like we want to get `pass = true`, so that it calls the `print_flag()` function. I'll quickly check that to make sure there are no weird things going on.

```c
void print_flag(void) {
  int unused;

  system("cat flag.txt");
  return;
}
```

Very cool.

Back in `main`, the core of the program appears to be the while loop:

```c
 while( true ) {
  __isoc99_scanf(&DAT_00102058);
  if (8 < i) break;
  nums[i] = nums[i] ^ nums[i + 1];
  nums[i + 1] = nums[i + 1] ^ nums[i];
  nums[i] = nums[i] ^ nums[i + 1];
  pass = check();
}
```

Those three lines with the bitwise XOR operation seem familiar, and is actually the code to [swap two variables without using a temporary one](https://stackoverflow.com/questions/1826159/swapping-two-variable-value-without-using-third-variable), equivalent to this:

```c
while( true ) {
  __isoc99_scanf(&DAT_00102058);
  if (8 < i) break;
  temp = nums[i];
  nums[i] = nums[i+1];
  nums[i+1] = temp;
  pass = check();
}
```

The next thing we need to investigate is that sketchy `scanf`<sup id="a5">[5](#f5)</sup> call. Looks like the decompiler isn't enough here, we'll have to look at the assembly.

```text
0010122d 48 8d 45 f4     LEA        RAX=>i,[RBP + -0xc]
00101231 48 89 c6        MOV        RSI,RAX
00101234 48 8d 3d        LEA        RDI,[DAT_00102058]
         1d 0e 00 00
0010123b b8 00 00        MOV        EAX,0x0
         00 00
00101240 e8 1b fe        CALL       __isoc99_scanf
         ff ff
```

In 64-bit x86, we place the first argument to a function in `RDI`, and the second argument in `RSI`. `scanf` takes a variable amount of arguments, but it looks like we're not using `RDX`, the third argument. The first argument to `scanf` should be the format string. It looks like we're loading something from the data section of the ELF for our first argument, and since we're expecting a string literal to be loaded in, this makes sense. In Ghidra, we can hover the mouse cursor over the label `[DAT_00102058]` and it shows us:

```text
                     DAT_00102058
00102058 25              ??         25h    %
00102059 64              ??         64h    d
0010205a 00              ??         00h
```

At the address specifed, the bytes `0x25`, `0x64`, and `0x00` are present. Ghidra has given us the ascii conversion: `%d`, and the `0x00` is just the null terminator<sup id="a6">[6](#f6)</sup>. This means that the first argument is the string `"%d"`, `scanf` is in fact taking in one number.

Back in `main`, we see that the second argument, `RSI`, is set from `RAX`, which refers to a stack variable. Ghidra has helpfully annotated that the stack address being referenced is the variable it has automatically named `i`.

Finally, our loop looks like:

```c
while (true) {
  scanf("%d", &i);
  if (i > 8) break;
  temp = nums[i];
  nums[i] = nums[i+1];
  nums[i+1] = temp;
  pass = check();
}
```

It looks like we continually swap two adjacent values in the array, until we enter an index out of bounds, after which the program sees if we have fulfilled some condition. We'll investigate the `check` function now.

```c
_Bool check(void) {
  uint32_t i;
  _Bool pass;

  i = 0;
  while( true ) {
    if (8 < i) {
      return true;
    }
    if (nums[i + 1] < nums[i]) break;
    i = i + 1;
  }
  return false;
}
```

Since this function is so straightforward, it decompiled without any issues. However, code generated from assembly is often mildly difficult to read, because the logic is often optimized into instructions that would look strange as code. We can rewrite the loop as follows:

```c
bool check(void) {
  for (uint32_t i = 0; i < 9; ++i) {
    if (nums[i] > nums[i+1]) {
      return false;
    }
  }
  return true;
}
```

This `check` function just looks like it's checking for whether or not `nums` is sorted ascending. Since we want `check` to return `true` and set `pass` to `true`, we want to make `nums` sorted ascending. Given that we found `main` to allow us to swap adjacent values, and that the challenge name is bubbly, it looks like we need to perform manual bubble sort<sup id="a7">[7](#f7)</sup> on `nums` to get it sorted.

## Solution

In order to manually sort the array by inputting indices to swap, we need to know what the values in the array are. Again, just by hovering our mouse cursor over the label `nums`, Ghidra shows us the bit of the ELF that stores the array.

```text
                     nums
00104060 01 00 00        uint32_t
         00 0a 00
         00 00 03
   00104060 [0]          1h,   Ah,   3h,   2h
   00104070 [4]          5h,   9h,   8h,   7h
   00104080 [8]          4h,   6h
```

```python
nums = [0x1, 0xA, 0x3, 0x2, 0x5, 0x9, 0x8, 0x7, 0x4, 0x6]
```

Then, I'll just implement bubble sort but print out the lower index every time a swap is made, and then I'll copy over the swap indices over to the program and get the flag.

---

<b id="f1">1</b> [file](https://man7.org/linux/man-pages/man1/file.1.html) is a command that attempts to determine the file type/format from the contents [↩](#a1)

<b id="f2">2</b> [Wikipedia page for ELF (see the diagram in the first section)](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format)

[Another link that has useful information in like the first half of the page](https://linuxhint.com/understanding_elf_file_format/) [↩](#a2)

<b id="f3">3</b> [chmod](https://linux.die.net/man/1/chmod) is a command that changes file permissions [↩](#a3)

<b id="f4">4</b> `./file` is literally just how you run a file in the current directory that's not in your PATH<sup id="a8">[8](#f8)</sup> I don't know what else to say why did you click on this footnote [↩](#a4)

<b id="f5">5</b> [C input and output](https://gribblelab.org/CBootCamp/10_Input_and_Output.html)

[Documentation for scanf](http://www.cplusplus.com/reference/cstdio/scanf/) [↩](#a5)

<b id="f6">6</b> All strings in C are [null-terminated strings](http://www.cs.ecu.edu/karl/2530/spr17/Notes/C/String/nullterm.html) [↩](#a6)

<b id="f7">7</b> [Bubble sort](https://medium.com/madhash/bubble-sort-in-a-nutshell-how-when-where-4965e77910d8) [↩](#a7)

<b id="f8">8</b> Why is there a footnote in a footnote? [What is PATH and what are environment variables?](https://superuser.com/questions/284342/what-are-path-and-other-environment-variables-and-how-can-i-set-or-use-them) [↩](#a8)