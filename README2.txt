box16* are just there for references from back when the YM2151 interface was much simpler in Box16.

I've renamed the module to x16sound and updated the build, etc.

New build target in Makefile: make lib
(builds libx16sound.a)
x16sound.c is the interface C file
x16sound.py is the renamed and modified verapsg.py

For reference on the YM libs:
opm.cpp is the code that instantiates the YM as an object, and also includes the accessor functions.

These are the necessary files from the ymfm library sources:
ymfm_opm.cpp
ymfm.h
ymfm_fm.h
ymfm_fm.ipp

On ubuntu:
g++ -L. -lmylib -o myprog myprog.cpp <--- linker fails to find the functions in mylib
g++ -L. -o myprog myprog.cpp -lmylib <--- linker finds the code, and this works

Not sure if this phenomenon is what's happening behind the scenes with ffi

