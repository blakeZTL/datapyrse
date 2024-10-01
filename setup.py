# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, import-error, unspecified-encoding


from setuptools import setup, find_packages  # type: ignore

# Read the requirements from the requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="datapyrse",
    version="0.8.0",
    packages=find_packages(),
    package_data={
        "datapyrse": ["py.typed", "typings/**/*.pyi"],
    },
    install_requires=requirements,
)
