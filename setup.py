"""Setup package for FactoryGame
"""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="factorygame-dave22153",
    version="0.2.0",
    description="Python game engine to have a 2d movable \"graph\".",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dave22153",
    author_email="dkanekanian@gmail.com",
    url="https://gitlab.com/factorygame/factorygame",
    packages=["factorygame", "factorygame.core", "factorygame.utils"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"],
    python_requires=">=3.2")
