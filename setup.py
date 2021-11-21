"""
Setup auto_utils
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = [
    'autoutils',
    # 'matrixcli'
]

install_requires = [
    "persiantools~=1.5.1",
    "redis~=3.5.3",
    'requests~=2.25.1',
    'urllib3~=1.26.2',
    "sshtunnel~=0.4.0",
    "paramiko~=2.7.2",
    "func-timeout~=4.3.5",
    "blessings~=1.7"
]

setup(
    name="autoutils",
    version="0.0.1",
    author="Reza Zeiny",
    author_email="rezazeiny1998@gmail.com",
    description="Some Good Function",
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rezazeiny/autoutils",
    packages=packages,
    platforms=['linux'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
