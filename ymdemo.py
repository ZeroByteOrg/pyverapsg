import miniaudio      # pip install miniaudio
import verapsg
import time


def verapsg_stream() -> miniaudio.PlaybackCallbackGeneratorType:
    required_frames = yield b""  # generator initialization
    while True:
        required_frames = yield verapsg.YMrender(required_frames)

patch = bytes([0xe4,0x00,0x19,0x65,0x56,0x61,0x1e,0x41,0x23,0x0a,0x5f,0x9e,0xdb,0x9e,0x10,0x0c,0x07,0x05,0x00,0x0b,0x0a,0x0a,0xba,0xf6,0x85,0xf5])

def patchYM():
	verapsg.YMwritereg(0x20,patch[0])
	verapsg.YMwritereg(0x38,patch[1])
	reg = 0x40
	for i in range(2, 25, 1):
		verapsg.YMwritereg(reg,patch[i])
		reg = reg + 0x08

stream = verapsg_stream()
next(stream)  # start the generator

with miniaudio.PlaybackDevice(sample_rate=48000) as device:
    print("playing on:", device.backend)
    device.start(stream)

    patchYM()
    verapsg.YMwritereg(0x28,0x4a)
    verapsg.YMwritereg(0x08,0x00)
    verapsg.YMwritereg(0x08,0x78)
    time.sleep(2)
    verapsg.YMwritereg(0x08,0x00)
