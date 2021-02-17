#include <bits/stdc++.h>
using namespace std;

int main() {
  time_t t = time(NULL);

  while (true) {
    srand(t);
    if (('c' ^ (rand() % 256)) == 0x64) {
      if (('t' ^ (rand() % 256)) == 0xd6) {
        if (('f' ^ (rand() % 256)) == 0xfe) {
          if (('{' ^ (rand() % 256)) == 0x78) {
            cout << "found " << t << '\n';
          }
        }
      }
    }
    --t;
  }

  return 0;
}
