.PHONY:  all dist install clean

all:
	@echo "Targets:  dist, lib, install, clean" 

clean:
	rm -rf build dist __pycache__ *.egg-info *.so
	rm -rf *.o *.a

dist:
	rm -f dist/*
	python setup.py clean --all
	python setup.py sdist

install: lib
	pip install miniaudio
	pip install .
	
lib:
	g++ -O3 -fPIC -c opm.cpp
	g++ -O3 -fPIC -c ymfm_opm.cpp
	gcc -O3 -fPIC -c vera_psg.c
	ar rcs libx16sound.a opm.o ymfm_opm.o vera_psg.o
	

