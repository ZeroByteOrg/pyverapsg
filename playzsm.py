import miniaudio      # pip install miniaudio
import x16sound
import time
import sys

def psg_stream() -> miniaudio.PlaybackCallbackGeneratorType:
    required_frames = yield b""  # generator initialization
    while True:
        required_frames = yield x16sound.PSGrender(required_frames)

def ym_stream() -> miniaudio.PlaybackCallbackGeneratorType:
	required_frames = yield b""  # generator initialization
	while True:
		required_frames = yield x16sound.YMrender(required_frames)

fname = "BGM39.ZSM"
try:
	file = open(fname, mode='rb')
except OSError:
    print ("Could not open/read file:", fname)
    sys.exit()
    
ZSM = file.read()
file.close()

index = 2 + 16	# skip the 2-byte PRG header and ZSM header

# doing it by brute force even though I know there exists a "Python"
# way to do this easily.... just don't know what that is.
if ZSM[4] != 0xff:
	loop = ZSM[2] + ZSM[3] * 256 + 0x2000 * ZSM[4]
	loop += 2
else:
	loop = 0


		



YM = ym_stream()
PSG = psg_stream()
next(YM)  # start the generator
next(PSG)  # start the generator

factor = 1.465
YMaudio = miniaudio.PlaybackDevice(sample_rate=int(x16sound.YMsamplerate(3579545)*factor))
PSGaudio = miniaudio.PlaybackDevice(sample_rate=48000)
YMaudio.start(YM)
PSGaudio.start(PSG)

print("sample rate is: ", x16sound.YMsamplerate(3579545))
print("playing on:", YMaudio.backend)

play = True
while play:
	command = ZSM[index]
	print ("ZSM[",hex(index),"] = ", hex(command))
	index += 1
	cmd_bits = (command & 0xc0) >> 6
	if cmd_bits == 0:
		value = ZSM[index]
		print ("  PSG write: ", hex(command), " <-- ", hex(value))
		index += 1
		x16sound.PSGwrite(command,value)
	else:
		if	cmd_bits == 1:
			n = command & 0x3f
			if n==0:
				print("  PCM write: (skipping 4 bytes)")
				index += 4	# skip 4-byte PCM command
			else:
				print("  YM  write: (",n," commands)")
				while n > 0:
					reg = ZSM[index]
					value = ZSM[index+1]
					print("             ",hex(reg),",",hex(value))
					index += 2
					x16sound.YMwrite(reg,value)
					n -= 1
		else:
			delay = command & 0x7f
			if delay > 0:
				print ("  DELAY = ", delay, "(",delay/60,"sec)")
				time.sleep(delay / 60)
				#sys.exit()
			else:
				if loop > 0:
					print ("  LOOP")
					index = loop
				else:
					play = False
