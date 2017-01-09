# This setup is based on the recommendations from the
# https://packaging.python.org/ documentation.

from setuptools import setup, find_packages
from codecs import open
from os import path

def read(fname):
    here = path.abspath(path.dirname(__file__))
    return open(path.join(here, fname), encoding = 'utf-8').read()

def readAbout():
    """Reads the fields of the about file."""
    fields = {}
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, 'clx', 'xms', '__about__.py')) as f:
        exec(f.read(), fields)
    return fields

setup(

    name='sdk-xms',
    version=readAbout()['__version__'],
    description='Library for CLX Communications HTTP REST Messaging API',
    long_description=read('README.rst'),
    url='https://github.com/clxcommunications/sdk-xms-python',

    author='Robert Helgesson',
    author_email='robert@chaitsa.com',

    packages=['clx.xms'],

    install_requires=['requests >= 2.4.2', 'iso8601 >= 0.1.9'],

    license='Apache License, Version 2.0',

    keywords='',

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications :: Telephony',
        'Topic :: Communications'
    ]

)
