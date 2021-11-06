#include <iostream>
#include <stdint.h>

#include "x16sound.c"

int main() {
	std::cout << "Hello, world!";
	YM_reset();
	psg_reset();
	ym_write(0x20,0);
	return 0;
}
