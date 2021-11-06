// Commander X16 Emulator
// Copyright (c) 2020 Frank van den Hoef
// All rights reserved. License: 2-clause BSD

#include <stdint.h>

extern void psg_reset(void);
extern void psg_writereg(uint8_t reg, uint8_t val);
extern void psg_render(int16_t *buf, unsigned num_samples);
extern void YM_render(int16_t *stream, uint32_t samples);
extern void YM_write(uint8_t reg, uint8_t val);
extern void YM_reset();

extern uint32_t YM_samplerate(uint32_t clock);

/*
void ym_render(int16_t *stream, uint32_t samples) {
	YM_render(stream, samples);
}
	
void ym_write(uint8_t reg, uint8_t val) {
	YM_write(reg, val);
}

void ym_reset() {
	YM_reset();
}

*/
