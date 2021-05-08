import numpy as np
import scipy as sp
import numpy.typing as npt

from typing import NamedTuple


class Audio(NamedTuple):
    waveform: npt.ArrayLike
    samplerate: int


def loop(
    *,
    audio: Audio,
    beats: npt.ArrayLike,
    start: int,
    steps: int,
    duration: float,
    crossfade: int,
) -> npt.ArrayLike:

    # Slice out audio segment to loop.
    clicks = beats[start : min(start + steps + 1, len(beats))]
    segment = audio.waveform[clicks[0] : clicks[-1]]

    n = len(segment)
    m = np.ceil(duration * audio.samplerate).astype(int)

    # Take fade-in/out material from outside audio segment.
    overlap = np.ceil(crossfade/1000 * audio.samplerate).astype(int)
    left = audio.waveform[clicks[0] - overlap : clicks[0]]
    right = audio.waveform[clicks[-1] : clicks[-1] + overlap]
    left = np.pad(left, (overlap - len(left), 0), "constant")
    right = np.pad(right, (0, overlap - len(right)), "constant")

    # TODO
    # assert len(left) == overlap and len(right) == overlap

    # Combine audio segment with fade-in/out material.
    window_length = 2 * overlap + n
    cosine_ratio = 2 * overlap / window_length
    window = sp.signal.tukey(window_length, cosine_ratio)
    tapered = window * np.concatenate((left, segment, right))

    # Overlap-add together the audio segments.
    repeated = np.zeros(m, dtype=np.float32)
    for i in range(overlap, m - overlap - n, n):
        l = i - overlap
        r = i + n + overlap
        d = r - l
        repeated[l:r] += tapered[:d]

    # TODO
    # assert max(repeated) == 1.0 and min(repeated) == -1.0

    return segment, repeated, overlap, window
