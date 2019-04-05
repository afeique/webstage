"""Defines a Config class for storing configuration options."""

import os
import sys
import json
import requests
from urllib.parse import urlparse


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
                self.exit(f"Created default {configFile}, please update it.")
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
            msg = f"The following required options are missing from {configFile}:\n" +\
                '"' + {', "'.join(missingOptions)} + '"\n\n' +\
                f"Some options can be passed in via commandline args:\n" +\
                '"--' + {', "--'.join(missingCliOptions)} + '"'
            self.exit(msg)

        # set warning message for missing webdriver option or args
        webdriverMsg = ""
        if not hasattr(self, "webdriver"):
            webdriverMsg = f'The "webdriver" options are missing from {configFile}'
        else:
            # check remote webdriver args
            missingWebdriverArgs = []
            for requiredArg in self.REQUIRED_WEBDRIVER_ARGS:
                if requiredArg not in self.webdriver:
                    missingWebdriverArgs.append(requiredArg)

            # set warning message if any webdriver args are missing
            if any(missingWebdriverArgs):
                webdriverMsg = \
                    f'The following "webdriver" options are missing from {configFile}:\n"' +\
                    {', "'.join(missingWebdriverArgs)} + '"\n\n'

        # write webdriver defaults to config file if they are unspecified
        if webdriverMsg:
            self.webdriver = self.default["webdriver"]
            self.save(configFile)
            webdriverMsg += f'Wrote default "webdriver" options to ' +\
                f'{configFile}:\n' + self.DEFAULT_WEBDRIVER_ARGS +\
                f'\n\nPlease update {configFile} and re-run'
            self.exit(webdriverMsg)

        # use urllib.parse.urlparse to check the scheme
        parsedUrl = urlparse(self.baseUrl.rstrip("/"))
        # if http:// or https:// not specified, assume http://
        # but only if there is either a netloc or path (something more than just a scheme)
        if not parsedUrl.scheme and (parsedUrl.netloc or parsedUrl.path):
            self.baseUrl = "http://" + self.baseUrl
            parsedUrl = urlparse(self.baseUrl)
        elif parsedUrl.scheme not in ["http", "https"]:
            # error if non HTTP scheme is given
            msg = f'\nBase URL in {configFile} must be HTTP or HTTPS, ' +\
                f'"\n{parsedUrl.scheme.upper()}" given:\n{self.baseUrl}'
            self.exit(msg)

        #  ensure there is a netloc or path after the http(s)://
        if not (parsedUrl.netloc or parsedUrl.path):
            msg = f'\nInvalid URL in {configFile}:\n{self.baseUrl}'
            self.exit(msg)

        # if the base URL is valid, test it with a GET request to make sure it works
        # http://docs.python-requests.org/en/master/api#requests.Response
        r = None  # holds the response object
        try:
            r = requests.get(self.baseUrl)
        except requests.exceptions.RequestException as e:
            self.exit(f'\nProblem with {configFile}:\n' + str(e))

        msg = f'Unreachable base URL in {configFile}:\n{self.baseUrl}'
        if r is not None:
            if r.status_code != 200 or r.headers["content-type"] != "text/html; charset=UTF-8":
                msg += f'\nGot HTTP status: {r.status_code} {r.reason}' +\
                    f'\nContent-Type: {r.headers["content-type"]}'
                self.exit(msg)
        else:
            self.exit(msg)

    def exit(self, msg: str) -> None:
        """Exit using self.exit if we're running a pytest session, else just exit"""
        # space out whatever comes after the exit message
        msg = f'\n\n!!!\n{msg}\n\n!!!\n\n'
        # if we're running from within a pytest session
        if "pytest" in sys.modules:
            import pytest
            pytest.exit(msg)
        exit(msg)

    def save(self, configFile: str = None) -> None:
        """Saves Config options to JSON."""
        output = {}
        for opt in self.ALL_OPTIONS:
            output[opt] = getattr(self, opt)
        if configFile:
            with open(configFile, 'w') as f:
                f.write(json.dumps(output, indent=4))
