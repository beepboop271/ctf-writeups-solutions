#include <bits/stdc++.h>
using namespace std;

string flag = "<flag>";
string output_file = "encrypted.txt";

int main() {
	srand(time(NULL));

	ofstream output;
	output.open(output_file);

	for (char chr : flag) {
		output << (char) (chr ^ (rand() % 256));
	}

	output.close();
}