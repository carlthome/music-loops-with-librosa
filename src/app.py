import io
import base64

import librosa as lr
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import soundfile as sf
import streamlit as st

from loop import loop, Audio

title = "Music Loop Generation"

st.set_page_config(page_title=title, page_icon="random", layout='centered', initial_sidebar_state='collapsed')

st.title(title)
st.write("Here's a simple example of creating music loops with librosa and NumPy/SciPy.")

plt.style.use("dark_background")


ALLOWED_AUDIO_FILE_EXTENSIONS = [
    "aac",
    "au",
    "flac",
    "m4a",
    # TODO "mp3",
    "ogg",
    "wav",
]
MAX_DURATION = 60.0
SAMPLERATE = 44100


def display_audio(waveform: npt.ArrayLike):
    with io.BytesIO() as f:
        sf.write(f, waveform, SAMPLERATE, format="ogg")
        ogg = f.getvalue()

    st.audio(ogg)
    data = base64.b64encode(ogg).decode()
    st.markdown(f'<a href="data:application/octet-stream;base64,{data}" download="audio.ogg">Download</a>', unsafe_allow_html=True)


uploaded_file = st.file_uploader(
    label="Source audio file",
    type=ALLOWED_AUDIO_FILE_EXTENSIONS,
    help="Upload an audio file to extract loops from.",
)
if uploaded_file is None:
    uploaded_file = "example.ogg"
    st.warning(f"No file uploaded. Using {uploaded_file} instead.")
else:
    st.success("Uploaded audio file")

with st.sidebar:
    st.header("Tempo estimation")

    st.subheader("Source audio")
    waveform, sr = lr.load(
        uploaded_file, sr=SAMPLERATE, duration=MAX_DURATION, res_type="kaiser_fast"
    )
    display_audio(waveform)

    harmonic, percussive = lr.effects.hpss(waveform)

    st.subheader("Harmonic elements")
    display_audio(harmonic)

    st.subheader("Percussive elements")
    display_audio(percussive)

    st.subheader("Click-track")

    tempo, beats = lr.beat.beat_track(percussive, SAMPLERATE, units="samples")
    st.write(f"Estimated {tempo:.0f} BPM with {len(beats)} guessed beats.")

    click_track = lr.clicks(beats / SAMPLERATE, sr=SAMPLERATE, length=len(waveform))
    display_audio(waveform + click_track)


col1, col2 = st.beta_columns(2)
with col1:
    with st.form(key='loop_controls'):
        st.subheader("Loop controls")
        duration = st.slider("Target duration (s)", 1.0, 60.0, 10.0)
        start = st.slider("Downbeat", 0, len(beats), 0)
        steps = st.slider("Beats", 0, 32, 4)
        crossfade = st.slider("Crossfade (ms)", 0, 1000, 50)
        submit_button = st.form_submit_button(label='Loop')

segment, audio, overlap, window = loop(
    audio=Audio(waveform=waveform, samplerate=SAMPLERATE),
    beats=beats,
    start=start,
    steps=steps,
    duration=duration,
    crossfade=crossfade,
)

with col2:
    fig, axs = plt.subplots(nrows=2)

    ax = axs[0]
    ax.plot(audio, zorder=1)
    ax.vlines(np.arange(0, len(audio), len(segment)), -1.0, 1.0, zorder=2)
    ax.plot(np.arange(-overlap, len(window) - overlap), window, zorder=3)

    ax = axs[1]
    ax.plot(segment)
    st.pyplot(fig)

    display_audio(audio)
