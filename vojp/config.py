import os
import platform

if 'basedir' not in os.environ:
    basedir = os.path.abspath(os.path.dirname(__file__))
    os.environ['basedir'] = basedir

basedir = os.environ['basedir']


class Config(object):
    RECORDING_DIR = basedir + '/recordings'
    LOG_DIR = basedir + '/logs'
    WIN_DLL_DIR = basedir + '/windows_dll'
    CONFIG_FILE = basedir + '/vojp_config.ini'
    DATABASE_DIR = basedir + '/database'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(DATABASE_DIR,
                                                                                            'vojp.db')


def setup_environment():
    from database import util as db_util

    if not os.path.exists(basedir):
        os.makedirs(basedir)

    if not os.path.exists(Config.RECORDING_DIR):
        os.makedirs(Config.RECORDING_DIR)

    if not os.path.exists(Config.LOG_DIR):
        os.makedirs(Config.LOG_DIR)

    if not os.path.exists(Config.DATABASE_DIR):
        os.makedirs(Config.DATABASE_DIR)

    if platform.system() == 'Windows':
        os.add_dll_directory(Config.WIN_DLL_DIR)

    if not db_util.check_data_model():
        db_util.create_data_model()
