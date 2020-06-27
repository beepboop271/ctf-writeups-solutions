# 12-shades-of-redpwn

> Everyone's favorite guess god Tux just sent me a flag that he somehow encrypted with a color wheel!
>
> I don't even know where to start, the wheel looks more like a clock than a cipher... can you help me crack the code?

Provided files: `ciphertext.jpg`, `color-wheel.jpg`

Prerequisite topics: [Number bases](https://www.mathsisfun.com/numbers/bases.html), [Ascii](http://www.asciitable.com/)

## Inspiration

Opening the images provided and noticing this line:
> looks more like a clock

![color-wheel.jpg](provided-files/color-wheel.jpg)

We see that there are twelve colours, so maybe we can number the colours in the wheel like a clock, and copy those numbers over to the ciphertext.

## Reasoning

We can assume each pair of colours is a character, which means that there are `12*12 = 144` possible characters. This is definitely enough to fit the flag characters as ascii, and since there are only 12 colours, we can be fairly sure it's a base 12 encoding.

Converting the colours gives us this:

```text
86 90 81 87 A3 49 99 43 97 97 41 92 49 7B 41 97 7B 44 92 7B 44 96 98 A5
f  l  a  g  {                                                        }
```

Aside: At first, I numbered the wheel exactly like a clock, with 12 at the top and 1 right after, but then I noticed that when checking against the known first characters of the flag, i had `9B` for `l` instead of `90`, so I changed the numbering, replacing the top colour with 0.

## Solution

Running `chr(int("86", 12))`<sup id="a1">[1](#f1)</sup> gives `"f"`, so base 12 seems good. Repeating this for all the characters gives us the flag.

---

<b id="f1">1</b> The `int(x)` function provides an optional second argument for base, so `int("86", 12)` converts the string assuming base of 12. [↩](#a1)
