"""
Python interface to the vera psg emulator code from x16emu
This module uses CFFI to create the glue code but also to actually compile everything else too!
"""


import os
from cffi import FFI


ffibuilder = FFI()
ffibuilder.cdef("""
void psg_reset(void);
void psg_writereg(uint8_t reg, uint8_t val);
void psg_render(int16_t *buf, unsigned num_samples);
void YM_render(int16_t *stream, uint32_t samples);
void YM_write(uint8_t reg, uint8_t val);
void YM_reset();
void debug();

uint32_t YM_samplerate(uint32_t clock);

""")


libraries = ["x16sound", "stdc++"]
compiler_args = []
macros =  []

if os.name == "posix":
    libraries = ["x16sound", "stdc++"]  # ["m", "pthread", "dl"]
    compiler_args = ["-g1", "-O3"]
    macros.extend([
        ("HAVE_LIBM", "1"),
        ("HAVE_UNISTD_H", "1"),
    ])


custom_sources = []
x16sound_sources = ["x16sound.c"]


ffibuilder.set_source("_x16sound", """
#include <stdint.h>

void psg_reset(void);
void psg_writereg(uint8_t reg, uint8_t val);
void psg_render(int16_t *buf, unsigned num_samples);
void YM_render(int16_t *stream, uint32_t samples);
void YM_write(uint8_t reg, uint8_t val);
void YM_reset();
void debug();

uint32_t YM_samplerate(uint32_t clock);

""",
    sources=custom_sources + x16sound_sources,
    include_dirs=[],
    library_dirs=["."],
    libraries=libraries,
    define_macros=macros,
    extra_compile_args=compiler_args)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
