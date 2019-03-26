"""This module configures pytest for running Datto acceptance tests.
It stores option defaults in a configuration file and accepts commandline
parameters.

Selenium RemoteWebdriver is used for browser instrumentation.
Either a local instance of the Selenium standalone server must be running
or a remote Selenium server must be specified as the command_executor.

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

import os
import json
import argparse
from datetime import datetime

import pytest
import requests
from py.xml import html
from selenium import webdriver


# defines config filename to store options in
CONFIG_FILE = "config.json"


class Config():
    """Stores configuration options passed between tests.

    Options are stored in a configuration file. These options
    are loaded by pytest. If the file doesn't exist or is empty,
    it is automatically created by pytest with reasonable defaults.

    Certain configuration options can be overridden by passing
    in commandline arguments through pytest. These options include:
    * url
    * username
    * password

    Attributes:
        url (str): The base URL of the DUT.
        username (str): Username to use for test session.
        password (str): Password to use for test session.
    """

    commandline_options = ["url", "username", "password"]
    required_options = commandline_options
    all_options = required_options + ["webdriver"]
    required_webdriver_args = ["command_executor", "desired_capabilities"]

    default = {
        "url": "http://",
        "username": "datto",
        "password": "datto100",
        "webdriver": {
            "command_executor": "http://127.0.0.1:4444/wd/hub",
            "desired_capabilities": {
                "browserName": "chrome",
                "chromeOptions": {
                    "args": [
                        "--disable-extensions",
                        "--disable-web-security"
                    ]
                }
            }
        }
    }

    DEFAULT_CONFIG = json.dumps(default, indent=4)
    DEFAULT_WEBDRIVER_ARGS = json.dumps(default["webdriver"], indent=4) +\
        "\n\nSee: https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities"

    def __init__(self, config_file: str):
        """Inits Config object with options from config file."""
        self.url = self.default["url"]
        self.username = self.default["username"]
        self.password = self.default["password"]
        self.webdriver = self.default["webdriver"]

        # create config file with reasonable defaults if it doesn't exist
        if not os.path.isfile(config_file):
            with open(CONFIG_FILE, 'w') as f:
                f.write(self.DEFAULT_CONFIG)
                pytest.exit(f"Created default {config_file}, please update it.")
        self.load(config_file)

    def load(self, config_file: str) -> None:
        """Load options from a config file, overwriting attributes."""
        self.file = config_file
        # load options from config file
        with open(config_file) as f:
            cfg = json.loads(f.read())

        # populate object attributes with values loaded from config file
        for key in cfg:
            # overwrite existing attribute values
            setattr(self, key, cfg[key])

        # ensure required options are specified, compile list of missing options
        missing_options = []
        missing_commandline_options = []
        for required_opt in self.required_options:
            if not hasattr(self, required_opt):
                missing_options.append(required_opt)
                if required_opt in self.commandline_options:
                    missing_commandline_options.append(required_opt)

        # exit with error message if any required options are missing
        if any(missing_options):
            msg = \
                f"\nThe following required options are missing from {config_file}:\n" +\
                '"' + {', "'.join(missing_options)} + '"\n\n' +\
                f"Some options can be passed in via commandline args:\n" +\
                '"--' + {', "--'.join(missing_commandline_options)} + '"'
            pytest.exit(msg)

        # set warning message for missing webdriver option or args
        webdriver_msg = ""
        if not hasattr(self, "webdriver"):
            webdriver_msg = f'\n\nThe "webdriver" option is missing from ' +\
                f'{config_file}\n\n'
        else:
            # check remote webdriver args
            missing_webdriver_args = []
            for required_arg in self.required_webdriver_args:
                if required_arg not in self.webdriver:
                    missing_webdriver_args.append(required_arg)

            # set warning message if any webdriver args are missing
            if any(missing_webdriver_args):
                webdriver_msg = \
                    f'\n\nThe following "webdriver" arguments are missing from {config_file}:\n"' +\
                    {', "'.join(missing_webdriver_args)} + '"\n\n'

        # cleanup
        if not self.url.endswith("/"):
            self.url += "/"

        # write webdriver defaults to config file if they are unspecified
        if webdriver_msg:
            self.webdriver = self.default["webdriver"]
            self.save(config_file)
            webdriver_msg += f'Wrote "webdriver" arguments to ' +\
                f'{config_file}:\n' + self.DEFAULT_WEBDRIVER_ARGS
            pytest.exit(webdriver_msg)

    def save(self, config_file: str = None) -> None:
        """Saves Config options to JSON."""
        output = {}
        for opt in self.all_options:
            output[opt] = getattr(self, opt)
        if config_file:
            with open(config_file, 'w') as f:
                f.write(json.dumps(output, indent=4))


@pytest.fixture(scope="session", autouse=True)
def config(pytestconfig) -> Config:
    """Fixture returning a Config object for the session."""
    # yield the existing Config object in pytestconfig
    yield pytestconfig.getoption("cfg")


@pytest.fixture(scope="session", autouse=True)
def session(config) -> object:
    """Create a webdriver instance and login the configured user."""
    # test the base URL in the config to ensure it works
    # http://docs.python-requests.org/en/master/api/#requests.Response
    r = None  # holds the response object
    try:
        r = requests.get(config.url)
    except requests.exceptions.RequestException as e:
        pytest.exit(f'\nProblem with {config.file}:\n' + str(e))

    if r is not None and r.status_code != 200:
        msg = f'\nInvalid URL "{config.url}" in {config.file}:\n' +\
            f'Got HTTP status: {r.status_code} {r.reason}'
        pytest.exit(msg)

    # create a new  RemoteWebdriver instance using the args in the config
    driver = webdriver.Remote(**config.webdriver)
    driver.maximize_window()
    driver.get(config.url)

    # login
    driver.find_element_by_id("username").send_keys(config.username)
    driver.find_element_by_id("password").send_keys(config.password)
    driver.find_element_by_id("loginButton").click()

    yield driver

    # session teardown, close browser window
    driver.close()


@pytest.fixture(scope="module", autouse=True)
def reset():
    """Fixture to reset DUT to known state."""


def pytest_addoption(parser):
    """Add commandline options to pytest and load configuration file."""
    cfg = Config(CONFIG_FILE)

    # pass loaded config object through hidden arg
    parser.addoption(
        "--cfg", action="store_const", const=cfg, default=cfg,
        help=argparse.SUPPRESS
    )
    # add options that can be passed in via the command line as args
    parser.addoption("--url", action="store", default=cfg.url,
        help="URL of device, defaults to value in config.yaml")
    parser.addoption("--username", action="store", default=cfg.username,
        help="Username for logging in, defaults to value in config.yaml")
    parser.addoption("--password", action="store", default=cfg.password,
        help="Password for logging in, defaults to value in config.yaml")


def pytest_collection_modifyitems(config, items):
    """Ensure required options are specified and modify tests."""
    # get previously loaded config object
    cfg = config.getoption("cfg")

    # override config object options with commandline options
    for commandline_opt in cfg.commandline_options:
        value = config.getoption(commandline_opt)
        if value:
            setattr(cfg, commandline_opt, value)


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
