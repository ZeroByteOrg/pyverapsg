#include <iostream>
#include "x16sound.c"

int main() {
	std::cout << "Hello, world!";
	YM_reset();
	psg_reset();
	return 0;
}
