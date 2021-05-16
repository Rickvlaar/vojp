import time
from os import getpid


class AudioUDPObject(object):

    def __init__(self, sample_rate, frame_size, audio_packet=b''):
        self.client_id = getpid()
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.audio_packet = audio_packet
        self.created_at = time.time_ns()
        self.sent_at = None
        self.output_at = None
        self.end_to_end_latency = None

    def determine_e2e_latency(self):
        self.end_to_end_latency = round((time.time_ns() - self.created_at) / 1e6, 0)
