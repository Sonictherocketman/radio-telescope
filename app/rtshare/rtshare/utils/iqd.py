import gzip


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
