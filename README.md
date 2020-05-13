# FileLookUpper

This is a simple project i've done to familiarize myself with python and its standard library. It exists solely for educational purposes.
So feel free to try it out and suggest ways to improve.

What it basically does is looks up directory sub structure of a given folder.
For now it simply outputs information about directory stucture in a table form according to provided options like filters and sort rules.
## Getting Started

It is supposed to run as a script inside a "lookup" package by providing it arguments like root path and processing options.

## Prerequisites

All you need to run it is standard python3 ( i personally used python3.6)

## Installing

No special installation procedures are needed at this point. Just run from source.

## Usage
from project directory
```
python -m lookup.__init__ [args]
```

## Running the tests

Tests are conducted using python unitests framework for processor.py module
Simply run tests_processor.py in the tests folder
```
python -m unittest %projectPath%/tests/test_processor.py 
```
Tests build a temporary tree structure inside tests folder to check for expected output

## Deployment

Deploy via pip using setup.py script in project root directory

## Versioning

0.1 - basic version

## License

This project is licensed under the Apache License - see the [LICENSE.md](LICENSE.md) file for details
