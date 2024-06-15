
hz_conversion = (
    ('Hz', 1),
    ('KHz', 1_000),
    ('MHz', 1_000_000),
    ('GHz', 1_000_000_000),
)


def display_hz(frequency):
    unit, value = sorted([
        (unit, (frequency / mod))
        for unit, mod in hz_conversion
        if mod >= 1
    ], reverse=True)[0]
    return f'{value}{unit}'
