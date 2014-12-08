#!/usr/bin/env python

from setuptools import setup


setup(
    name='yawndb',
    version='0.2.0',
    author='Kagami Hiiragi',
    author_email='kagami@genshiken.org',
    description='Python library for interacting with YAWNDB',
    packages=['yawndb'],
    url='http://selectel.io',
    install_requires=[
        'twisted',
    ],
    zip_safe=False,
)
