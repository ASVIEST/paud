import io
import math
import platform
import subprocess
import wave
from os import PathLike

from .frame import Frame
from .frames import DataFrames
from .libdata import ToData
from .play import Play

lib = "wave"


def get_os():
    os = platform.system()

    if os == "Linux":
        if subprocess.check_output(["uname", "-o"]).strip() == b"Android":
            return "termux"
        else:
            return "linux"
    else:
        return os.lower()


class Audio:
    def __init__(self, *args, **kwargs):

        self.frames = (
            list(args[0])
            if len(args) == 1 and isinstance(args[0], (list, tuple))
            else list(args)
        )

        if "frames" in kwargs:
            if isinstance(kwargs["frames"], DataFrames):
                self.frames = kwargs["frames"]  # .append(kwargs["frames"])
            else:
                self.frames.extend(kwargs["frames"])

        if "params" in kwargs:
            parameters = kwargs["params"]
            self.channels, self.sample_width, self.frame_rate, = (
                parameters[0],
                parameters[1],
                parameters[2],
            )

        else:
            self.frame_rate = kwargs.setdefault("frame_rate", 44.1 * 1000)
            self.channels = kwargs.setdefault("channels", 1)
            if kwargs.get("sample_width"):
                self.sample_width = kwargs["sample_width"]
            else:
                self.sample_width = len(bytes(self.max()))

    @classmethod
    def open(cls, file, lazy=True):

        if isinstance(file, (str, PathLike, io.IOBase)):
            with wave.open(file, "rb") as f:
                sample_width = f.getsampwidth()
                frame_rate = f.getframerate()
                frame_count = f.getnframes()
                channels = f.getnchannels()

                frame_size = sample_width * channels

                content = f.readframes(frame_count)

                if lazy:
                    frames = DataFrames(content, frame_size)
                else:
                    frames = [
                        Frame(content[i : frame_size + i])
                        for i in range(0, frame_count * frame_size, frame_size)
                    ]

        return cls(
            sample_width=sample_width,
            frame_rate=frame_rate,
            channels=channels,
            frames=frames,
            frame_count=frame_count,
        )

    @property
    def duration(self):
        return self.frame_count / self.frame_rate

    @property
    def frame_width(self):
        return self.channels * self.sample_width

    @property
    def peak_amplitude(self):
        return 256 ** self.sample_width / 2

    @property
    def frame_count(self):
        return len(self.frames)

    @property
    def data(self):
        if isinstance(self.frames, DataFrames):
            return self.frames.data
        return ToData(self.frames, self.params, lib).data

    @property
    def params(self):
        return (
            self.channels,
            self.sample_width,
            self.frame_rate,
            self.frame_count,
            "NONE",
            "Uncompressed",
        )

    def play(self):
        Play(
            get_os(),
            ToData(self.frames, self.params, lib).data,
        )

    def save(self, file):
        if isinstance(file, str):
            file = open(file, "wb")
        with file as f:
            f.write(ToData(self.frames, self.params, lib).data)

    def append(self, frame):
        self.frames.append(frame)

    def extend(self, frames):
        self.frames.extend(frames)

    def max(self):
        return max(self.frames)

    def __len__(self):
        return self.frame_count

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Audio(
                self.frames[
                    self.parse_index(index.start) : self.parse_index(
                        index.stop
                    ) : index.step
                ],
                params=self.params,
            )
        elif isinstance(index, int):
            return self.frames[index]
        elif isinstance(index, str):
            return self.frames[self.ms_pos(self.parse_timestamp(index))]
        else:
            raise TypeError(
                f"Audio indices must be integers or slices, not {type(index)}"
            )

    def __setitem__(self, key, value):
        if isinstance(key, (slice, int)):
            if isinstance(value, Frame):
                self.frames[key] = value
            else:
                raise TypeError("Audio value must be Frame")
        else:
            raise TypeError(
                f"Audio indices must be integers or slices, not {type(key)}"
            )

    def __add__(self, other):
        if other == 0:
            return self
        if isinstance(other, Frame):
            return Audio(frames=self.frames + [other], params=self.params)
        elif isinstance(other, Audio):
            return Audio(self.frames + other.frames, params=self.params)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(other).__name__}' and 'Audio'"
            )

    def __mul__(self, other):
        if isinstance(other, int):
            return Audio(frames=self.frames * other, params=self.params)
        else:
            raise TypeError(
                f"can't multiply sequence by non-int of type '{type(other).__name__}'"
            )

    def __gt__(self, other):
        return self.frames > other.frames

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return (self.frames, self.params) == (other.frames, other.params)
        return False

    def __array__(self, dtype="int16"):  # "float32"):
        import numpy as np

        dtype = np.dtype(dtype)

        max_ = 1 << (8 * self.sample_width - 1)

        arr = np.frombuffer(self.data, dtype=f"int{self.sample_width * 8}")

        if dtype.kind in "iu" and dtype != arr.dtype:
            arr = arr * (np.iinfo(dtype).max + 1) / max_

        if dtype.kind == "f":
            arr = (arr / max_).astype(dtype)

        return arr.reshape((-1, self.channels))

    def reverse(self):
        return Audio(frames=reversed(self.frames), params=self.params)

    def separate(self, n):
        n = math.ceil(self.frame_count / n)
        return tuple(
            Audio(frames=self.frames[i : i + n], params=self.params)
            for i in range(0, self.frame_count, n)
        )

    def ms_pos(self, ms):
        return int(ms * (self.frame_rate / 1000))

    def parse_index(self, index):
        return (
            self.ms_pos(self.parse_timestamp(index))
            if isinstance(index, str)
            else index
        )

    @staticmethod
    def parse_timestamp(string):
        ms_time = [24 * 60 ** 2 * 1000, 60 ** 2 * 1000, 60 * 1000, 1000]
        time = list(map(float, string.split(":")))
        i = 0
        while ms_time and time:
            i += ms_time.pop() * time.pop()
        return int(i)
