#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


version = '0.1'

# Get the long description of the project
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get all requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'MVCS',
    version = version,
    description='A simple version control system for code files',
    author = 'Mohammed Al-Dokimi',
    author_email = 'eespb3@inf.elte.hu',
    license = 'MIT',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/Aldokimi/thesis',
    py_modules = ['mvcs', 'cli'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control',
    ],
    entry_points = '''
        [console_scripts]
        mvcs = mvcs:main
    '''
)
