try:
    from mpmath import log
except ImportError:
    from math import log


class Frame:
    def __init__(self, value):
        if isinstance(value, int):
            self.value = int.to_bytes(
                value, length=self.bytes_needed(value), byteorder="little"
            )

        elif isinstance(value, bytes):
            self.value = value

    def __int__(self):
        return int.from_bytes(self.value, byteorder="little")

    def __str__(self):
        return str(self.__int__())

    def __bytes__(self):
        return self.value

    def __repr__(self):
        return f"Frame({self.__str__()})"

    def __reversed__(self):
        pass

    def __add__(self, other):
        from .audio import Audio

        if isinstance(other, Frame):
            return Audio(frames=[self, other])
        if isinstance(other, Audio):
            return Audio(frames=[self, *other.frames])

    def __mul__(self, other):
        from .audio import Audio

        if isinstance(other, int):
            return Audio(frames=[self] * other)
        else:
            raise TypeError(
                f"can't multiply sequence by non-int of type '{type(other).__name__}'"
            )

    def __gt__(self, other):
        return self.value > other.value

    @staticmethod
    def bytes_needed(n):
        if n == 0:
            return 1
        return int(log(n, 256)) + 1
