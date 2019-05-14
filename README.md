# Webstage

Webstage is a simple BDD-style framework running on top of pytest and selenium.

## Setup

### Python

[Miniconda] is recommended. It is cross-platform, fast to download,
 and has tools for managing Python environments out-of-the-box. Its
 package manager can install precompiled packages which is handy for
 Windows systems.

[Anaconda] is the full-featured download which comes with all the pre-compiled
 libraries supported by `conda`. It is considerably bigger as a result.

[Anaconda]: https://www.anaconda.com/distribution/
[Miniconda]: https://docs.conda.io/en/latest/miniconda.html

### Environments

It is recommended to use isolated Python environments. To setup and manage
 Python environments using `conda`, refer to:

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

Run the selenium standalone server in a terminal. Then navigate to the source directory and run:

    pytest
