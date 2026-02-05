"""
Random Video Picker - A simple, cross-platform desktop application for randomly selecting and playing videos.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="random-video-picker",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple, cross-platform desktop application for randomly selecting and playing videos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/z-jensen/Random-Video-Picker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "Pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "random-video-picker=random_video_picker:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["README.md", "LICENSE", "*.txt"],
    },
)
