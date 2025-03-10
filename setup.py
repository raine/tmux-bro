from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="tmux-bro",
    version="0.1.6",
    author="raine",
    author_email="raine.virta@gmail.com",
    description="A smart tmux session manager that sets up project-specific sessions automatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raine/tmux-bro",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tmux-bro=tmux_bro.main:main",
        ],
    },
)
