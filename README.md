# paud
Python library to process audio



open audio

```python
from paud import Audio

au = Audio.open('audio.wav') #file or path

print(f'audio duration = {au.duration}')

au.play() #play audio

au[:100].play() #play first 100 frames of audio


```



