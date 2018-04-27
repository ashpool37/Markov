"""
Accessories for text i/o
"""

import typing


class WordWriter:
    """
    A simple interface to output space-separated words in lines of fixed
    maximum width.
    """

    def __init__(self, ofs: typing.TextIO, width: int = 80):
        """
        :param ofs: output file object
        :param width: maximum line width
        """
        self.line = []
        self.line_len = 0
        self.width = width
        self.ofs = ofs

    def _flush(self):
        """
        Internal function to print the current line.
        """
        self.ofs.write(' '.join(self.line) + '\n')
        self.ofs.flush()
        self.line = []
        self.line_len = 0

    def _push(self, chunk: str):
        if self.line:
            self.line_len += 1
        if self.line_len + len(chunk) > self.width:
            self._flush()
        self.line.append(chunk)
        self.line_len += len(chunk)
        if self.line_len >= self.width:
            self._flush()

    def write(self, chunk: str):
        """
        Append the chunk to the current line, flushing the line and/or breaking
        down the chunk if the resulting line would exceed the maximum width.
        :param chunk: the string to be written
        """
        if len(chunk) <= self.width:
            self._push(chunk)
        else:  # Very long chunk, gotta break it down!
            written = 0
            while written < len(chunk):
                chars_left = (self.width - self.line_len -
                              (1 if self.line else 0))
                to_write = min(chars_left, len(chunk) - written)
                self._push(chunk[written:written + to_write])
                written += to_write
