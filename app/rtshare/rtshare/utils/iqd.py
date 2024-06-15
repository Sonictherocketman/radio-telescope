import base64
import gzip
import math


COMMENT = '#'
SEPARATOR = ':'


def get_header(file):
    if file.name.endswith('.gz'):
        content = gzip.decompress(file.read())
        lines = content.decode('utf-8').split('\n')
    else:
        lines = file

    headers = []
    for line in lines:
        line = line.strip()

        if line.startswith(COMMENT):
            headers.append(line[1:].split(SEPARATOR, 1))
        elif not line:
            continue
        else:
            # Stop after the first line that isn't either blank or a comment.
            break

    file.seek(0)

    return {
        key.lower().strip(): value.strip()
        for (key, value) in headers
    }


def get_data(file, as_complex=True):
    if file.name.endswith('.gz'):
        content = gzip.decompress(file.read())
        lines = content.decode('utf-8').split('\n')
    else:
        lines = file

    encoded_data = ''.join([
        line for line in lines
        if not line.startswith('#')
    ])
    file.seek(0)

    data = [
        int(oct(b), 8)
        for b in base64.b64decode(encoded_data)
    ]

    def _get_entries():
        for i_raw, q_raw in zip(data[0::1], data[1::2]):
            n = 0
            i, q = (
                (i_raw / (255 / 2)) - 1,
                (q_raw / (255 / 2)) - 1,
            )
            # This gives Amplitude, Power (which is more useful) is just I^2 + Q^2.
            # dB is then log10(P)
            # https://dsp.stackexchange.com/questions/19615/converting-raw-i-q-to-db
            v = math.sqrt(i**2 + q**2)
            if as_complex:
                yield complex(i, q), v
            else:
                yield i, q, v

    return list(_get_entries())
