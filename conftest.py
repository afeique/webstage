"""Configures pytest for running Datto acceptance tests. Reasonable option
defaults are stored in a configuration file and certain options can be
overridden from the commandline.

Selenium RemoteWebdriver is used for browser instrumentation.
The datto.Actor class extends the RemoteWebdriver class and adds methods
for BDD-oriented syntax and acceptance testing.

To run an instance of a RemoteWebdriver, either a local instance of the 
Selenium standalone server must be running or a remote Selenium server 
must be specified as the command_executor.

The RemoteWebdriver is the only supported type of webdriver class for
simplicity and flexibility. It supports a dictionary configuration for
specifying browser and desired capabilities.

The following fixtures are defined in this file:
* A session-level "config" fixture:
    - Loads options from the configuration file
    - Stores options in a Config object as attributes
    - Passes (arbitrary) options around using the Config object
    - Needs to be injected into tests that rely on config
* A session level "login" autouse fixture:
    - Sets up a Selenium webdriver instance using chromedriver
    - Logs into the web UI of the Datto device-under-test (DUT)
    - Is loaded automatically and does not have to be injected
* A module level fixture:
    - Restores the device to a known "vanilla" state

Tests should be organized based on idempotent modules which
run a sequence of tests and return the device to a known state.

The tests defined within modules can be incremental, meaning
each test defines a step and the steps must be run in order.
Use the `[@pytest.mark.incremental]` decorator and organize
the tests within a class.

Tests within module can also be organized as functions which
specify their dependency on previous tests using plugins such as:
* [pytest-depends]
* [pytest-dependency]

More rudimentary ordering, such as what test should always be run
first, what test should be run last, can be specified using [pytest-ordering].

When defining tests in modules, there are two ways to organize them:
* A collection of categorically related idempotent tests
    - The order of these tests does not matter
    - Each test returns the DUT to a known state
    - These tests can be defined as functions, no class is needed
* An incremental set of test steps in a class
    - These steps must be executed in order
    - DUT is returned to a known state after all the steps

.. _@pytest.mark.incremental:
   https://docs.pytest.org/en/latest/example/simple.html#incremental-testing-test-steps
.. pytest-depends
   https://pypi.org/project/pytest-depends/
.. pytest-dependency
   https://pytest-dependency.readthedocs.io/en/latest/
.. pytest-ordering
   https://pytest-ordering.readthedocs.io/en/develop/
"""

import argparse
from datetime import datetime

import pytest
from urllib3.exceptions import MaxRetryError
from selenium.webdriver import Remote as WebDriver
from py.xml import html

import webstage

# defines config filename to store options in
CONFIG_FILE = "config.json"


@pytest.fixture(scope="session", autouse=True)
def config(pytestconfig) -> webstage.Config:
    """Fixture returning a Config object for the session."""
    # yield the existing Config object in pytestconfig
    yield pytestconfig.getoption("cfg")


@pytest.fixture(scope="session", autouse=True)
def lead_actor(config) -> webstage.Actor:
    """Yields a lead actor to use for the entire performance.

    A webstage.Actor encapsulates a webdriver instance. On init, the actor 
    logs in as the configured user at the specified base URL.
    """

    # create a new  RemoteWebdriver instance using the args in the config
    msg = ""
    try:
        actor = webstage.Actor(WebDriver(**config.webdriver), config)
    except MaxRetryError:
        msg = f"\nCould not connect to selenium server: " +\
            config.webdriver["command_executor"] +\
            "\nEnsure the server is installed and running."

    # performing pytest.exit() outside the try-except is faster for some reason
    if msg:
        pytest.exit(msg)

    yield actor

    # session teardown, close browser window
    actor.finish()


@pytest.fixture(scope="function")
def I(lead_actor) -> webstage.Actor:
    """Perform cleanup between acts"""
    yield lead_actor

@pytest.fixture(scope="module", autouse=True)
def reset():
    """Fixture to reset DUT to known state."""


def pytest_addoption(parser):
    """Add commandline options to pytest and load configuration file."""
    cfg = webstage.Config(CONFIG_FILE)

    # pass loaded config object through hidden arg
    parser.addoption(
        "--cfg", action="store_const", const=cfg, default=cfg,
        help=argparse.SUPPRESS
    )
    # add options that can be passed in via the command line as args
    parser.addoption("--base-url", action="store", dest="base_url", default=cfg.base_url,
        help="Base URL of device, defaults to value in config.json")
    parser.addoption("--username", action="store", dest="username", default=cfg.username,
        help="Username for logging in, defaults to value in config.json")
    parser.addoption("--password", action="store", dest="password", default=cfg.password,
        help="Password for logging in, defaults to value in config.json")


def pytest_collection_modifyitems(config, items):
    """Ensure required options are specified and modify tests."""
    # get previously loaded config object
    cfg = config.getoption("cfg")

    # override config object options with commandline options
    for cli_option in cfg.CLI_OPTIONS:
        value = config.getoption(cli_option)
        if value:
            setattr(cfg, cli_option, value)


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    """Update HTML report table headers."""
    cells.insert(2, html.th("Description"))
    cells.insert(1, html.th("Time", class_="sortable time", col="time"))
    cells.pop()


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    """Add description and time columns to HTML report."""
    cells.insert(2, html.td(report.description))
    cells.insert(1, html.td(datetime.utcnow(), class_="col-time"))
    cells.pop()


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """Add test docstrings as descriptions in the HTML report."""
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)
