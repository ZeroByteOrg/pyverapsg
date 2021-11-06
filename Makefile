.PHONY:  all dist install clean

all:
	@echo "Targets:  dist, install, clean" 

clean:
	rm -rf build dist __pycache__ *.egg-info *.so

dist:
	rm -f dist/*
	python setup.py clean --all
	python setup.py sdist

install:
	pip install miniaudio
	pip install .

