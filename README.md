# Webstage

***Pre-Alpha***

Webstage is a simple BDD-style framework written on top of Selenium and Pytest. Bootstraps libraries so developers can get up-and-running with minimal boilerplate code.

Additionally, it provides some basic abstraction to Python Selenium bindings using an actor model similar to [Codeception](https://codeception.com/).

## Setup

1. Clone this repo
   - `git clone git@github.com:afeique/webstage`
2. 

## Appendices

### Python Setup

It is recommended to install [Miniconda] for running Python. It is cross-platform, fast to download, and has tools for managing Python environments out-of-the-box. Its package manager can install precompiled packages which is handy for Windows systems.

[Anaconda] is the full-featured download which comes with all the pre-compiled libraries supported by `conda`. It is considerably larger than [Miniconda].

When installing `conda`, make sure it is installed to your `PATH`. On Linux and OSX, this means modifying your `.bashrc` or `bash_profile`.

[Anaconda]: https://www.anaconda.com/distribution/
[Miniconda]: https://docs.conda.io/en/latest/miniconda.html

### Python Environment Setup

It is recommended to use sandboxed Python environments for development. To setup and manage Python environments using `conda`, refer to:

- [Managing Conda Environments](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
- [Official Cheat-sheet](https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf)
- [Continuum Cheat-sheet](http://know.continuum.io/rs/387-XNW-688/images/conda-cheatsheet.pdf)

####Basic Commands

A simple environment can be created using conda: 

````
conda create -n webstage-project python=3.7
````

The command can then be activated using:

```
conda activate webstage-project
```

- On Linux: `source activate webstage-project`

### Required Packages

There is a `requirements.txt` which contains a list of the requisite packages to get up and running on
 a new environment. To install the packages listed, use:

    pip install -r requirements.txt

### Selenium Standalone Server

Whether you will tests on a remote host or localhost, you must install [Java JDK] for the platform and the [Selenium standalone server].

[Java JDK]: https://www.oracle.com/technetwork/java/javase/downloads/index.html
[Selenium standalone server]: https://www.seleniumhq.org/download/

## Run Tests

1. Run the selenium standalone server in a separate terminal

2. Then navigate to the source directory and run:

   ```
   pytest
   ```

   - On first-run, a `config.json` will be created for you. Modify it and fill out the `base_url`.
   - Re-run `pytest`