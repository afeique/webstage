"""Defines a Config class for storing configuration options."""

import os
import json
import pytest
import requests
import validators


class PytestConfig():
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

    CLI_OPTIONS = ["baseUrl", "username", "password"]
    REQUIRED_OPTIONS = CLI_OPTIONS
    ALL_OPTIONS = REQUIRED_OPTIONS + ["webdriver"]
    REQUIRED_WEBDRIVER_ARGS = ["command_executor", "desired_capabilities"]

    default = {
        "baseUrl": "http://",
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

    def __init__(self, configFile: str):
        """Inits Config object with options from config file."""
        self.baseUrl = self.default["baseUrl"]
        self.username = self.default["username"]
        self.password = self.default["password"]
        self.webdriver = self.default["webdriver"]

        # create config file with reasonable defaults if it doesn't exist
        if not os.path.isfile(configFile):
            with open(configFile, 'w') as f:
                f.write(self.DEFAULT_CONFIG)
                pytest.exit(f"Created default {configFile}, please update it.")
        self.load(configFile)

    def load(self, configFile: str) -> None:
        """Load options from a config file, overwriting attributes."""
        self.file = configFile
        # load options from config file
        with open(configFile) as f:
            cfg = json.loads(f.read())

        # populate object attributes with values loaded from config file
        for key in cfg:
            # overwrite existing attribute values
            setattr(self, key, cfg[key])

        # ensure required options are specified, compile list of missing options
        missingOptions = []
        missingCliOptions = []
        for requiredOption in self.REQUIRED_OPTIONS:
            if not hasattr(self, requiredOption):
                missingOptions.append(requiredOption)
                if requiredOption in self.CLI_OPTIONS:
                    missingCliOptions.append(requiredOption)

        # exit with error message if any required options are missing
        if any(missingOptions):
            msg = \
                f"\nThe following required options are missing from {configFile}:\n" +\
                '"' + {', "'.join(missingOptions)} + '"\n\n' +\
                f"Some options can be passed in via commandline args:\n" +\
                '"--' + {', "--'.join(missingCliOptions)} + '"'
            pytest.exit(msg)

        # set warning message for missing webdriver option or args
        webdriverMsg = ""
        if not hasattr(self, "webdriver"):
            webdriverMsg = f'\n\nThe "webdriver" option is missing from ' +\
                f'{configFile}\n\n'
        else:
            # check remote webdriver args
            missingWebdriverArgs = []
            for requiredArg in self.REQUIRED_WEBDRIVER_ARGS:
                if requiredArg not in self.webdriver:
                    missingWebdriverArgs.append(requiredArg)

            # set warning message if any webdriver args are missing
            if any(missingWebdriverArgs):
                webdriverMsg = \
                    f'\n\nThe following "webdriver" arguments are missing from {configFile}:\n"' +\
                    {', "'.join(missingWebdriverArgs)} + '"\n\n'

        # cleanup
        self.baseUrl = self.baseUrl.rstrip("/")

        # write webdriver defaults to config file if they are unspecified
        if webdriverMsg:
            self.webdriver = self.default["webdriver"]
            self.save(configFile)
            webdriverMsg += f'Wrote "webdriver" arguments to ' +\
                f'{configFile}:\n' + self.DEFAULT_WEBDRIVER_ARGS +\
                f'\n\nPlease update {configFile}'
            pytest.exit(webdriverMsg)

        # validate the base URL in the config to ensure it's a real URL
        # https://validators.readthedocs.io/en/latest/#module-validators.url
        if not validators.url(self.baseUrl):
            msg = f'\nInvalid base URL "{self.baseUrl}" in {configFile}'
            pytest.exit(msg)

        # if the base URL is valid, test it with an HTTP GET to make sure it works
        # http://docs.python-requests.org/en/master/api#requests.Response
        r = None  # holds the response object
        try:
            r = requests.get(self.baseUrl)
        except requests.exceptions.RequestException as e:
            pytest.exit(f'\nProblem with {configFile}:\n' + str(e))

        msg = f'\nUnreachable base URL "{self.baseUrl}" in {configFile}'
        if r is not None:
            if r.status_code != 200 or r.headers["content-type"] != "text/html; charset=UTF-8":
                msg += f'\nGot HTTP status: {r.status_code} {r.reason}' +\
                    f'\nContent-Type: {r.headers["content-type"]}'
                pytest.exit(msg)
        else:
            pytest.exit(msg)

    def save(self, configFile: str = None) -> None:
        """Saves Config options to JSON."""
        output = {}
        for opt in self.ALL_OPTIONS:
            output[opt] = getattr(self, opt)
        if configFile:
            with open(configFile, 'w') as f:
                f.write(json.dumps(output, indent=4))
