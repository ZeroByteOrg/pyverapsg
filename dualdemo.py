import miniaudio      # pip install miniaudio
import x16sound
import time


def psg_stream() -> miniaudio.PlaybackCallbackGeneratorType:
    required_frames = yield b""  # generator initialization
    while True:
        required_frames = yield x16sound.PSGrender(required_frames)

def ym_stream() -> miniaudio.PlaybackCallbackGeneratorType:
	required_frames = yield b""  # generator initialization
	while True:
		required_frames = yield x16sound.YMrender(required_frames)

# Vibraphone 1 from Deflemask
patch = bytes([0xe4,0x00,0x19,0x65,0x56,0x61,0x1e,0x41,0x23,0x0a,0x5f,0x9e,0xdb,0x9e,0x10,0x0c,0x07,0x05,0x00,0x0b,0x0a,0x0a,0xba,0xf6,0x85,0xf5])

def patchYM(voice):
	voice = voice & 0x07
	x16sound.YMwrite(0x20+voice,patch[0])
	x16sound.YMwrite(0x38+voice,patch[1])
	reg = 0x40+voice
	for i in range(2, 25, 1):
		x16sound.YMwrite(reg,patch[i])
		reg = reg + 0x08

def volumefade():
    for vol in range(63, 0, -1):
        print(vol, end=" ", flush=True)
        x16sound.PSGwrite(2, 0b11000000 | vol)
        time.sleep(0.05)
    print()

ymaudio = ym_stream()
psgaudio = psg_stream()
next(ymaudio)  # start the generator
next(psgaudio)  # start the generator

factor = 1.465
YM = miniaudio.PlaybackDevice(sample_rate=int(x16sound.YMsamplerate(3579545)*factor))
PSG = miniaudio.PlaybackDevice(sample_rate=48000)
YM.start(ymaudio)
PSG.start(psgaudio)

print("sample rate is: ", x16sound.YMsamplerate(3579545))
print("playing on:", YM.backend)

for i in range(0,7,1):
	patchYM(i)

x16sound.YMwrite(0x28,0x4a)
x16sound.YMwrite(0x08,0x00)
x16sound.YMwrite(0x08,0x78)
time.sleep(2.0)
x16sound.YMwrite(0x08,0x00)

freq = x16sound.freqw(440)
# I guess we should perhaps add constants to refer to the vera registers....
x16sound.PSGwrite(0, freq & 255)
x16sound.PSGwrite(1, freq >> 8)
x16sound.PSGwrite(2, 255)
x16sound.PSGwrite(3, 2 << 6)
print("triangle")
volumefade()
