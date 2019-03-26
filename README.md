# Siris OS 2 Acceptance Tests

These are acceptance tests which can be run using `pytest`. Many of these tests
 rely on the `RemoteWebdriver` in [selenium-python] for browser instrumentation.
 The [selenium standalone server] is required, either on a remote host or the
 localhost, to run the `RemoteWebdriver`.

[selenium-python]: https://selenium-python.readthedocs.io/
[selenium standalone server]: https://www.seleniumhq.org/download/

## Setup

### Python

It is recommended to install [Miniconda] and use `conda` to manage your Python
 installations using virtual environments. [Miniconda] is cross-platform, fast to
 download, and easy to get up and running. The `conda` package manager can easily
 install precompiled which is particularly handy for Windows systems.

[Anaconda] is the full-featured download which comes with all the pre-compiled
libraries supported by `conda`. It is considerably bigger as a result.

[Anaconda]: https://www.anaconda.com/distribution/
[Miniconda]: https://docs.conda.io/en/latest/miniconda.html

### Virtual Environments

To setup and manage virtual environments using `conda`, refer to:

- [Official Cheat-sheet](https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf)
- [Continuum Cheat-sheet](http://know.continuum.io/rs/387-XNW-688/images/conda-cheatsheet.pdf)
- [Official Docs](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)

### Required Packages

There is a `requirements.txt` which contains a list of the requisite packages to get up and running on
 a new environment. To install the packages listed, use:

    pip install -r requirements.txt

### Selenium Standalone Server

Whether you will tests on a remote host or localhost, you must install [Java JDK] for the platform
and the [selenium standalone server].

[Java JDK]: https://www.oracle.com/technetwork/java/javase/downloads/index.html
[selenium standalone server]: https://www.seleniumhq.org/download/

## Run Tests

Simply run `pytest` from within the directory.