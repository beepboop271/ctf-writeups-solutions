#include <bits/stdc++.h>
using namespace std;

int lol[] = {
0x64, 0xD6, 0xFE, 0x78, 0xD0, 0xC6, 0xA1, 0xC0, 0xA7, 0xA0, 0x91, 0x25, 0x58, 0xEC, 0x49, 0x5F, 0x8A, 0xAF, 0x9F, 0x41, 0x51, 0x47, 0x41, 0x32, 0xF2, 0xE9, 0x47, 0x97, 0x38, 0x56, 0x77, 0x54, 0xC9, 0x93, 0x57, 0x32, 0x49
};

int main() {
  srand(1595568762);

  for (char chr : lol) {
    cout << (char) (chr ^ (rand() % 256));
  }
  cout << '\n';

  return 0;
}
