from os import path
from pathlib import Path
import sys
import zipapp


def create_zip():
    basedir = path.abspath(path.dirname(__file__))

    zipapp.create_archive(source=basedir + '/build',
                          target='vojpzipp.pyz',
                          filter=file_filter,
                          main='vojp.main:run')


def file_filter(file_path: Path):
    ignored_file_stems = {'build',
                          'dist',
                          'out',
                          'node_modules',
                          'gui',
                          'include',
                          'build',
                          'vojpzipp',
                          '__pycache__',
                          '.git',
                          '.idea',
                          'venv'}
    if file_path.stem in ignored_file_stems:
        return False
    else:
        return True

# This command be holy:
# python -m pip install -r requirements.txt --target build/vojp --upgrade --no-cache-dir --no-binary :all: --force-reinstall

