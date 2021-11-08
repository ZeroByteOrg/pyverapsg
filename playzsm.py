import x16sound
import time
import sys



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

x16 = x16sound.system()
x16.startaudio()

play = True
while play:
	command = ZSM[index]
#	print ("ZSM[",hex(index),"] = ", hex(command))
	index += 1
	cmd_bits = (command & 0xc0) >> 6
	if cmd_bits == 0:
		value = ZSM[index]
#		print ("  PSG write: ", hex(command), " <-- ", hex(value))
		index += 1
		x16.PSG.write(command,value)
	else:
		if	cmd_bits == 1:
			n = command & 0x3f
			if n==0:
#				print("  PCM write: (skipping 4 bytes)")
				index += 4	# skip 4-byte PCM command
			else:
#				print("  YM  write: (",n," commands)")
				while n > 0:
					reg = ZSM[index]
					value = ZSM[index+1]
#					print("             ",hex(reg),",",hex(value))
					index += 2
					x16.YM.write(reg,value)
					n -= 1
		else:
			delay = command & 0x7f
			if delay > 0:
#				print ("  DELAY = ", delay, "(",delay/60,"sec)")
				time.sleep(delay / 60)
			else:
				if loop > 0:
#					print ("  LOOP")
					index = loop
				else:
					play = False
x16.stopaudio()
