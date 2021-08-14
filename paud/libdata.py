import wave
from io import BytesIO


class ToData:
    def __init__(self, frames, params, lib="wave"):
        self.frames = frames
        self.params = params
        self.lib = lib

        self.libs = {
            "wave": self.wave,
        }

        self.data = self.libs[self.lib]()

    def wave(self):
        with BytesIO() as f:
            with wave.open(f, "wb") as wav:
                wav.setparams(self.params)

                for i in range(self.params[3]):
                    wav.writeframes(bytes(self.frames[i]))

            f.seek(0)
            data = f.read()

        return data

    def __bytes__(self):
        return self.data
