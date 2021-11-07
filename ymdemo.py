import miniaudio      # pip install miniaudio
import x16sound
import time


def x16sound_stream() -> miniaudio.PlaybackCallbackGeneratorType:
	required_frames = yield b""  # generator initialization
	inrate = x16sound.YMsamplerate(3579545)
	while True:
		required_frames = yield x16sound.YMrender(required_frames)

# Vibraphone 1 from Deflemask
patch = bytes([0xe4,0x00,0x19,0x65,0x56,0x61,0x1e,0x41,0x23,0x0a,0x5f,0x9e,0xdb,0x9e,0x10,0x0c,0x07,0x05,0x00,0x0b,0x0a,0x0a,0xba,0xf6,0x85,0xf5])

def patchYM():
	x16sound.YMwrite(0x20,patch[0])
	x16sound.YMwrite(0x38,patch[1])
	reg = 0x40
	for i in range(2, 25, 1):
		x16sound.YMwrite(reg,patch[i])
		reg = reg + 0x08

stream = x16sound_stream()
next(stream)  # start the generator

with miniaudio.PlaybackDevice(sample_rate=48000) as device:
	print("sample rate is: ", x16sound.YMsamplerate(3579545))
	print("playing on:", device.backend)
	device.start(stream)

	patchYM()
	x16sound.YMwrite(0x28,0x4a)
	x16sound.YMwrite(0x08,0x00)
	x16sound.YMwrite(0x08,0x78)
	time.sleep(2)
	x16sound.YMwrite(0x08,0x00)
