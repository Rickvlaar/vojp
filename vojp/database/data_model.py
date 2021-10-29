from sqlalchemy import Column, Integer, String
from vojp.database import Base


class UserSettings(Base):
    __tablename__ = 'UserSettings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    saved_input_device = Column(String)
    saved_output_device = Column(String)
    input_sample_rate = Column(Integer)
    output_sample_rate = Column(Integer)
    output_buffer_size = Column(Integer)
    packet_length = Column(Integer)

    def __repr__(self):
        return self.attributes()

    def __str__(self):
        return str(self.attributes())

    def attributes(self):
        return {key: value for key, value in self.__dict__.items() if key[:1] != '_'}
