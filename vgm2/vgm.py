#import zlib
import sys
import gzip

class VGMfile:
	def __init__(self, filename):
		self.version = 0
		try:
			self.data = open(filename, mode='rb').read()
		except:
			self.data = bytearray ()
			return
		try:
			self.data = gzip.decompress(self.data)
		except:
			self.data = self.data
		if len(self.data) < 0x40:
			self.data = bytearray ()
			return
		self.magic = self.le32(0)
		if self.magic != 0x206d6756:
			self.data = bytearray ()
			return
		self.version = self.data[0x09]
		x = self.data[0x08]
		self.version += (x >> 4) / 10
		self.version += (x & 0xf) / 100
		self.offset = 0x40
		if self.version >= 1.5:
			self.offset = self.le32(0x34) + 0x34
		self.loop = self.le32(0x1c) + 0x1c
		self.pointer = self.offset

	def le32(self,offset) -> int:
		i = self.data[offset]
		i += self.data[offset+1] << 8
		i += self.data[offset+2] << 16
		i += self.data[offset+3] << 24
		return i

	def le16(self,offset) -> int:
		i = self.data[offset]
		i += self.data[offset+1]
		return i

	def skip(self, num_bytes):
		self.pointer += num_bytes
		self.pointer = min(len(self.data)-1,self.pointer)
		
	def seek(self, index):
		self.pointer = min(max(index,self.offset),len(self.data)-1)
		
	def reset(self):
		self.pointer = self.offset

	def read1(self) -> int:
		d = self.data[self.pointer]
		self.skip(1)
		return d

VGM = VGMfile("ryu.vgz")
print (len(VGM.data))
print (str(VGM.le32(0)))
print ("version = ", VGM.version)
		
	
