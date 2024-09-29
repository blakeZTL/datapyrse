from setuptools import setup

# Read the requirements from the requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="datapyrse",
    version="0.6.0",
    packages=["datapyrse"],
    install_requires=requirements,
)
