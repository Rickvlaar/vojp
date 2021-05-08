import os
from pathlib import Path

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    RECORDING_DIR = basedir + '/recordings'
    LOG_DIR = basedir + '/logs'
    WIN_DLL_DIR = basedir + '/windows_dll'

    CONFIG_FILE = basedir + '/vojp_config.ini'

    DATABASE_DIR = basedir + '/database'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(DATABASE_DIR,
                                                                                            'vojp.db')
