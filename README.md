# Music loop generation with LibROSA and NumPy
This is a Streamlit app that showcases a method for looping user-selected musical bars up to the requested duration, for a given audio file.

To achieve this, we rely on a builtin tempo estimation method in LibROSA to guesstimate where the beats are in the audio file. Then we simply repeat the extracted segment with a small cross-fade between the repetitions in order to hide artifacts. Depending on the input signal, this often sounds surprisingly useful despite being a very simple approach.

## Develop
Start Visual Studio Code in this directory with Google's Cloud Code extension.

### Local
Run @command:cloudcode.runCloudRunApp and browse to the app's URL.

### Deploy
Run @command:cloudcode.deployCloudRunApp and fill in the settings.
