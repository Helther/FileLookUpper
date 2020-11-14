import setuptools
from lookup.__main__ import programVersion
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FileLookUpper",
    version=programVersion,
    author="Gusev Anton",
    author_email="kaeldevop@gmail.com",
    description="script for listing files/directories name according to filters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Helther/FileLookUpper.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "LICENSE :: OSI APPROVED :: APACHE SOFTWARE LICENSE",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)