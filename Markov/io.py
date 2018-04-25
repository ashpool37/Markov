import typing


class WordWriter:
    def __init__(self, ofs: typing.TextIO, width: int = 80):
        self.line = ''
        self.width = width
        self.ofs = ofs

    def _flush(self):
        self.ofs.write(self.line + '\n')
        self.ofs.flush()
        self.line = ''

    def write(self, chunk: str):
        if len(chunk) <= self.width:
            append_len = len(self.line) + len(chunk) + (1 if self.line else 0)
            if append_len <= self.width:
                if self.line:
                    self.line += ' '
                self.line += chunk
            else:
                self._flush()
                self.line += chunk
        else: # Very long chunk, gotta break it down!
            written = 0
            while (written < len(chunk)):
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
