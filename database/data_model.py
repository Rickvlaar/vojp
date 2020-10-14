from sqlalchemy import Column, Integer, String, Date
from database import Base


class UserSettings(Base):

    def __init__(self, saved_input_device, saved_output_device, input_sample_rate, output_sample_rate):
        self.saved_input_device = saved_input_device
        self.saved_output_device = saved_output_device
        self.input_sample_rate = input_sample_rate
        self.output_sample_rate = output_sample_rate

    def __repr__(self):
        return self.attributes()

    def __str__(self):
        return str(self.attributes())

    def attributes(self):
        return {key: value for key, value in self.__dict__.items() if key[:1] != '_'}
