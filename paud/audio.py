from .frame import Frame
from .play import Play
from .libdata import ToData
import platform
import wave
import subprocess
import copy

import pathlib
import io

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
            if args or kwargs:
                self.sample_width = kwargs.setdefault(
                    "sample_width", len(bytes(self.max()))
                )
            else:
                self.sample_width = 2

    @classmethod
    def open(cls, file, old_reader=False):

        if isinstance(file, pathlib.Path):
            file = io.FileIO(file, "rb")

        if isinstance(file, (str, pathlib.Path, io.IOBase)):
            with wave.open(file, "rb") as f:
                sample_width = f.getsampwidth()
                frame_rate = f.getframerate()
                frame_count = f.getnframes()
                channels = f.getnchannels()

                if old_reader:
                    frames = [Frame(f.readframes(1)) for i in range(frame_count)]
                else:
                    frame_size = sample_width * channels

                    content = f.readframes(frame_count)
                    frames = [
                        Frame(content[0 + i : frame_size + i])
                        for i in range(0, frame_count * frame_size, frame_size)
                    ]

        return cls(
            sample_width=sample_width,
            frame_rate=frame_rate,
            channels=channels,
            frames=frames,
            frame_count=frame_count,
        )

    def duration(self):
        return self.frame_count / self.frame_rate

    @property
    def frame_width(self):
        return self.channels * self.sample_width

    @property
    def peak_amplitude(self):
        return 256 ** self.sample_width / 2

    # @property
    # def sample_width(self):
    #     default = 16
    #     if self.frames:
    #         return len(bytes(self.max()))
    #     else:
    #         return default

    @property
    def frame_count(self):
        return len(self.frames)

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
        # data = self.frames_to_data(self.frames)

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
            return Audio(self.frames[index], params=self.params)
        elif isinstance(index, int):
            return self.frames[index]
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
        frames = copy.deepcopy(self.frames)
        if isinstance(other, Frame):
            frames.append(other)
        elif isinstance(other, Audio):
            frames.extend(other.frames)

        return Audio(frames=frames)

    def __mul__(self, other):
        frames = copy.deepcopy(self.frames)
        if isinstance(other, int):
            frames *= other
        else:
            raise TypeError(
                f"can't multiply sequence by non-int of type '{type(other).__name__}'"
            )

        return Audio(frames=frames)

    def __gt__(self, other):
        return self.frames > other.frames
