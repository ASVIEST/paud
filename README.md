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



open audio from URL

```python
import requests
from paud import Audio
from io import BytesIO

r = requests.get('https://file-examples-com.github.io/uploads/2017/11/file_example_WAV_10MG.wav')

au = Audio.open(BytesIO(r.content))
au.play()
```

