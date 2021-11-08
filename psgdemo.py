import x16sound
import time



# The x16 docs say that the vera sample frequency is 48828
# To avoid internal resampling I just stick 48000 in the audio device,
# which should be a natively supported sample rate by many audio hardware.
# For exact frequencies stick 48828 in here and miniaudio should resample on the fly,
# (but this has some quality loss.

x16 = x16sound.system()

def volumefade():
    for vol in range(63, 0, -1):
        print(vol, end=" ", flush=True)
        x16.PSG.write(2, 0b11000000 | vol)
        time.sleep(0.05)
    print()

x16.startaudio()

print("playing on:", x16.PSGaudio.backend)

freq = x16.PSG.freqw(440)
# I guess we should perhaps add constants to refer to the vera registers....
x16.PSG.write(0, freq & 255)
x16.PSG.write(1, freq >> 8)
x16.PSG.write(2, 255)
x16.PSG.write(3, 2 << 6)
print("triangle")
volumefade()
x16.PSG.write(3, 1 << 6)
print("sawtooth")
volumefade()
x16.PSG.write(3, 3 << 6)
print("noise")
volumefade()
x16.stopaudio()

