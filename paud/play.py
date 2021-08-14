import wave
import tempfile
import soundfile as sf
from io import BytesIO


class Play:
    # enviroments = {
    #     'termux': termux,
    #     'windows': windows
    # }

    def __init__(self, env, data):
        self.env = env
        self.data = data

        self.enviroments = {
            "termux": self.termux,
            "windows": self.windows,
            "linux": self.linux,
            "macos": self.macos,
        }

        self.enviroments[self.env]()

    def termux(self):
        from termux import Media

        with tempfile.NamedTemporaryFile() as temp:
            temp.write(self.data)
            Media.play(temp.name)

    def windows(self):
        import winsound

        winsound.PlaySound(self.data, winsound.SND_MEMORY | winsound.SND_NOSTOP)


    def linux(self):
        pass

    def macos(self):
        pass

    def pyaudio_play(self):
        pass
