"""
Python interface to the vera psg emulator code from X16Emu
"""
import miniaudio
from _x16sound import lib, ffi
import array


__version__ = "1.0"

def stream_generator(chip) -> miniaudio.PlaybackCallbackGeneratorType:
	required_frames = yield b""  # generator initialization
	while True:
		required_frames = yield chip.render(required_frames)

class psgchip:
	def __init__(self):
		self.reset()
		self.output = stream_generator(self)
		next(self.output)
		
	def freqw(self, hz: int) -> int:
		return int(hz / (48828.125 / 2**17))

	def write(self, reg: int, value: int) -> None:
		lib.psg_writereg(reg, value)

	def render(self, num_samples: int) -> bytearray:
		buffer = bytearray(num_samples*4)
		lib.psg_render(ffi.from_buffer("int16_t *", buffer), num_samples)
		return buffer

	def render_a(self, num_samples: int) -> array.array:
		buffer = array.array('h', [0]*num_samples*2)
		lib.psg_render(ffi.from_buffer("int16_t *", buffer, True), num_samples)
		return buffer
		
	def reset(self) -> None:
		lib.psg_reset()

class ymchip:
	#factor = 1.465
	factor = 1.0
	def __init__(self, clock=3579545):
		self.clock = clock
		self.reset()
		self.output = stream_generator(self)
		next(self.output)

	def write(self, reg: int, value: int) -> None:
		lib.YM_write(reg, value)

	def render(self, num_samples: int) -> bytearray:
		buffer = bytearray(num_samples*4)
		lib.YM_render(ffi.from_buffer("int16_t *", buffer), num_samples)
		return buffer

	def render_a(self, num_samples: int) -> array.array:
		buffer = array.array('h', [0]*num_samples*2)
		lib.YM_render(ffi.from_buffer("int16_t *", buffer, True), num_samples)
		return buffer
		
	def samplerate(self) -> int:
		return int(lib.YM_samplerate(self.clock) * self.factor)

	def reset(self) -> None:
		lib.YM_reset()
		
	def debug(self) -> None:
		lib.debug()
		
class system:
	YM	= ymchip()
	PSG = psgchip()
	def __init__ (self):
		self.YMaudio  = miniaudio.PlaybackDevice(sample_rate=self.YM.samplerate())
#		self.PSGaudio = miniaudio.PlaybackDevice(sample_rate=48000)
		self.PSGaudio = miniaudio.PlaybackDevice(sample_rate=48828)
		
	
	def reset(self) -> None:
		self.YM.reset()
		self.PSG.reset()
		
	def startaudio(self):
		self.YMaudio.start(self.YM.output)
		self.PSGaudio.start(self.PSG.output)
		
	def stopaudio(self):
		self.YMaudio.stop()
		self.PSGaudio.stop()

#reset()
