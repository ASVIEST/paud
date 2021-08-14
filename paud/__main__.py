from . import Audio
from . import Frame

au = Audio.open("output.wav")
au.play()

x = au[:2]
print((Frame(21) + x + Frame(32)).frames)

print(au.frames[:10])