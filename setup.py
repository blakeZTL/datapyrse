from setuptools import setup, find_packages

# Read the requirements from the requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="datapyrse",
    version="0.5.0",
    packages=["datapyrse", "datapyrse.core"],
    install_requires=requirements,
)
