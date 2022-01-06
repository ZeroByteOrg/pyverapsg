
class YM2151:
	def __init__(self, rev=39):
		self.transpose = (rev < 39)
		self.regs = [-1] * 256
		self.updates = {}
		self.queue = []
		self.chanlock = [False] * 8
		self.chanused = [False] * 8
		
	def write(self,reg,val):
		if reg == 0x19 and val >= 0x80:
			reg = 0x1a
		if reg == 0x14:
			val &= 0xb3 # mask off the IRQ enable bits
		if self.transpose and reg & 0xf8 == 0x28:
			# pitch-correction if outputting for a 4MHz-clock YM...
			foo = 1
		if reg == 0x08:
			self.flushvoice(val & 0x07)
			self.queue.extend([8,val])
			if val & 0xf8 > 0:
				self.chanused[val&7] = True
		else:
			self.updates[reg] = val

	def flush(self) -> list:
		for i in self.updates:
			reg = i
			if reg == 0x1a: reg = 0x19
			if self.regs[i] != self.updates[i]:
				self.regs[i] = self.updates[i]
				self.queue.extend([reg,self.regs[i]])
		out = self.queue
		self.queue = []
		self.updates = {}
		return out
		
	def flushvoice(self,voice):
		if voice > 7: return
		for i in range(0,13):
			reg = voice + 0x20 + (8 * i)
			if reg in self.updates and self.regs[reg] != self.updates[reg]:
				self.regs[reg] = self.updates[reg]
				self.queue.extend([reg,self.regs[reg]])
				del self.updates[reg]

class VERAPSG:
	def __init__(self):
		self.regs = [-1] * 64
		self.updates = {}
		self.chanlock = [False] * 8
		self.chanused = [False] * 8
		
	def write(self, reg, val):
		if reg % 4 == 2 and val >= 0x40:
			self.chanused[int(reg/4)] = True
		self.updates[reg] = val
				
	def flush(self) -> list:
		out = []
		for i in self.updates:
			if self.updates[i] != self.regs[i]:
				self.regs[i] = self.updates[i]
				out.extend([i,self.regs[i]])
		self.updates = {}
		return out

# ----- from vgm2zsm php script: -----
#	$songdata[6] = $channelsused['ym'];
#	$songdata[7] = $channelsused['psg'] & 0xff;
#	$songdata[8] = $channelsused['psg'] >> 8;
#	$songdata[9] = ZSMTICKRATE & 0xff; 
#	$songdata[10] = (ZSMTICKRATE >> 8) & 0xff;
#   songdata[11 - 15] = reserved (set to zero)

class ZSMfile:
	def __init__(self, fm, psg, rate=60):
#		self.data = [0] * 16 # don't include the 2-byte PRG header here.
#		self.data[2] = 0xff # default to non-looping tune
#		self.data[5] = 0xff # default to no PCM data present
		self.data = []
		self.vgmticks = 0
		self.ticksperframe = int(44100/rate)
		self.delay = 0
		self.fm = fm
		self.psg = psg

	def tick(self, ticks):
		self.vgmticks += ticks
		if self.vgmticks < self.ticksperframe: return
		newdelay = int(self.vgmticks/self.ticksperframe)
		self.vgmticks = self.vgmticks % self.ticksperframe
		out = self.psg.flush()
		fmout = self.fm.flush()
		# append the fmout buffer to the out buffer.
		# fm buffer needs a YM reg/val command byte= 0x40 + n pairs.
		# The command byte cannot specify n>63 so we must break the fm
		# writes into batches of < 64 reg/val pairs each
		l = len(fmout)
		while l > 0:
			out.append(int(min(l/2,63)+0x40))	# ymwrite command byte
			out.extend(fmout[0:64*2])			# up to 63 reg/val pairs
			del fmout[0:64*2]					# remove up to 63 pairs
			l = len(fmout)						# update length then loop
		if len(out) > 0:
			# if any chip commands are ready to write, first clear any
			# prior delay amount into the stream
			while self.delay > 0:
				if self.delay > 127:
					self.data.append(0xff)
					self.delay -= 127
				else:
					self.data.append(self.delay + 0x80)
					self.delay = 0
			self.data.extend(out)
			self.delay = newdelay
		else:
			self.delay += newdelay

psg = VERAPSG()
ym = YM2151()
zsm = ZSMfile(ym,psg)
zsm.tick(730)
ym.write(0x20,0)
zsm.tick(730)
ym.write(0x20,1)
zsm.tick(730)
ym.write(0x20,2)
print(zsm.data)
