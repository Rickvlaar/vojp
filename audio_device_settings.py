import sounddevice as sd


def override_default(sample_rate=sd.default.samplerate):
    if sample_rate:
        sd.default.samplerate = sample_rate