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
        self.line = ''
        self.width = width
        self.ofs = ofs

    def _flush(self):
        """
        Internal function to print the current line.
        """
        self.ofs.write(self.line + '\n')
        self.ofs.flush()
        self.line = ''

    def write(self, chunk: str):
        """
        Append the chunk to the current line, flushing the line and/or breaking
        down the chunk if the resulting line would exceed the maximum width.
        :param chunk: the string to be written
        """
        if len(chunk) <= self.width:
            append_len = len(self.line) + len(chunk) + (1 if self.line else 0)
            if append_len <= self.width:
                if self.line:
                    self.line += ' '
                self.line += chunk
            else:
                self._flush()
                self.line += chunk
        else:  # Very long chunk, gotta break it down!
            written = 0
            while written < len(chunk):
                append_len = min(self.width, len(chunk) - written)
                if self.line:
                    append_len -= (len(self.line) + 1)
                if append_len < 1:
                    self._flush()
                    continue
                if self.line:
                    self.line += ' '

                self.line += chunk[written:written + append_len]
                written += append_len
                self._flush()
