
class YM2151:
	def __init__(self):
		self.regs = [0] * 256
		self.dirty = []
		self.queue = []
		self.chanlock = [False] * 8
		self.chanused = [False] * 8
		
	def write(self,reg,val):
		if reg == 0x19 and val >= 0x80:
			reg = 0x1a
		if reg == 0x14:
			val &= 0xb3 # mask off the IRQ enable bits
		if reg == 0x08:
			self.flushvoice(val & 0x07)
			self.queue.extend([8,val])
			if val & 0xf8 > 0:
				self.chanlock[val&7] = True
		else:
			if self.regs[reg] != val:
				self.regs[reg] = val
				if reg not in self.dirty:
					self.dirty.extend([reg])

	def flush(self) -> list:
		for i in self.dirty:
			if i == 0x1a:
				self.queue.extend([0x19,self.regs[0x1a]])
			else:
				self.queue.extend([i,self.regs[i]])
		out = self.queue
		self.queue = []
		self.dirty = []
		return out
		
	def flushvoice(self,voice):
		if voice > 7: return
		for i in range(0,13):
			reg = 0x20 + 8 * i
			if reg in self.dirty:
				self.queue.extend([reg,self.regs[reg]])
				self.dirty.remove(reg)
		
