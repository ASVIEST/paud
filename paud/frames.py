from math import ceil
from audioop import reverse

from .frame import Frame


class DataFrames:
    __slots__ = ["data", "frame_width"]

    def __init__(self, data, frame_width):
        self.data = data
        self.frame_width = frame_width

    def __getitem__(self, item):
        if isinstance(item, int):
            if item < len(self):
                return self.get_frame(item)
            else:
                raise IndexError(f"{type(self).__name__} index out of range")

        elif isinstance(item, slice):
            # TODO: add step support
            return DataFrames(
                self.data[
                    0
                    if item.start is None
                    else item.start * self.frame_width : 0
                    if item.stop is None
                    else item.stop * self.frame_width
                ],
                self.frame_width,
            )

    def __iter__(self):
        return (self.get_frame(i) for i in range(len(self)))

    def __len__(self):
        return ceil(len(self.data) / self.frame_width)

    def __reversed__(self):
        return DataFrames(
            reverse(self.data, self.frame_width),
            self.frame_width,
        )

    def get_frame(self, index):
        return Frame(
            self.data[index * self.frame_width : (index + 1) * self.frame_width]
        )

    def min(self):
        return min(self.data)

    def max(self):
        return max(self.data)
