import miniaudio      # pip install miniaudio
import verapsg
import time


def verapsg_stream() -> miniaudio.PlaybackCallbackGeneratorType:
    required_frames = yield b""  # generator initialization
    while True:
        required_frames = yield verapsg.render(required_frames)


def volumefade():
    for vol in range(63, 0, -1):
        print(vol, end=" ", flush=True)
        verapsg.writereg(2, 0b11000000 | vol)
        time.sleep(0.05)
    print()


# The x16 docs say that the vera sample frequency is 48828
# To avoid internal resampling I just stick 48000 in the audio device,
# which should be a natively supported sample rate by many audio hardware.
# For exact frequencies stick 48828 in here and miniaudio should resample on the fly,
# (but this has some quality loss.

stream = verapsg_stream()
next(stream)  # start the generator

with miniaudio.PlaybackDevice(sample_rate=48000) as device:
    print("playing on:", device.backend)
    device.start(stream)

    freq = verapsg.freqw(440)
    # I guess we should perhaps add constants to refer to the vera registers....
    verapsg.writereg(0, freq & 255)
    verapsg.writereg(1, freq >> 8)
    verapsg.writereg(2, 255)
    verapsg.writereg(3, 2 << 6)
    print("triangle")
    volumefade()
    verapsg.writereg(3, 1 << 6)
    print("sawtooth")
    volumefade()
    verapsg.writereg(3, 3 << 6)
    print("noise")
    volumefade()

