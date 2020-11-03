import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = '0.2'
setuptools.setup(
    name="FileLookUpper",
    version=version,
    author="Gusev Anton",
    author_email="kaeldevop@gmail.com",
    description="script for listing files/directories name according to filters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Helther666/FileLookUpper.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "LICENSE :: OSI APPROVED :: APACHE SOFTWARE LICENSE",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    #test_suite='nose.collector',
    #tests_require=['nose', 'simplejson'],
)