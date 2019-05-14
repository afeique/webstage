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

    CLI_OPTIONS = ["base_url", "username", "password"]
    REQUIRED_OPTIONS = CLI_OPTIONS
    ALL_OPTIONS = REQUIRED_OPTIONS + ["webdriver"]
    REQUIRED_WEBDRIVER_ARGS = ["command_executor", "desired_capabilities"]

    default = {
        "base_url": "http://",
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
        self.base_url = self.default["base_url"]
        self.username = self.default["username"]
        self.password = self.default["password"]
        self.webdriver = self.default["webdriver"]

        # create config file with reasonable defaults if it doesn't exist
        if not os.path.isfile(config_file):
            with open(config_file, 'w') as f:
                f.write(self.DEFAULT_CONFIG)
                self.exit(f"Created default {config_file}, please update it.")
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
        missingOptions = []
        missing_cli_options = []
        for required_option in self.REQUIRED_OPTIONS:
            if not hasattr(self, required_option):
                missingOptions.append(required_option)
                if required_option in self.CLI_OPTIONS:
                    missing_cli_options.append(required_option)

        # exit with error message if any required options are missing
        if any(missingOptions):
            msg = f"The following required options are missing from {config_file}:\n" +\
                '"' + {', "'.join(missingOptions)} + '"\n\n' +\
                f"Some options can be passed in via commandline args:\n" +\
                '"--' + {', "--'.join(missing_cli_options)} + '"'
            self.exit(msg)

        # set warning message for missing webdriver option or args
        webdriver_msg = ""
        if not hasattr(self, "webdriver"):
            webdriver_msg = f'The "webdriver" options are missing from {config_file}'
        else:
            # check remote webdriver args
            missing_webdriver_args = []
            for requiredArg in self.REQUIRED_WEBDRIVER_ARGS:
                if requiredArg not in self.webdriver:
                    missing_webdriver_args.append(requiredArg)

            # set warning message if any webdriver args are missing
            if any(missing_webdriver_args):
                webdriver_msg = \
                    f'The following "webdriver" options are missing from {config_file}:\n"' +\
                    {', "'.join(missing_webdriver_args)} + '"\n\n'

        # write webdriver defaults to config file if they are unspecified
        if webdriver_msg:
            self.webdriver = self.default["webdriver"]
            self.save(config_file)
            webdriver_msg += f'Wrote default "webdriver" options to ' +\
                f'{config_file}:\n' + self.DEFAULT_WEBDRIVER_ARGS +\
                f'\n\nPlease update {config_file} and re-run'
            self.exit(webdriver_msg)

        # use urllib.parse.urlparse to check the scheme
        parsed_url = urlparse(self.base_url.rstrip("/"))
        # if http:// or https:// not specified, assume http://
        # but only if there is either a netloc or path (something more than just a scheme)
        if not parsed_url.scheme and (parsed_url.netloc or parsed_url.path):
            self.base_url = "http://" + self.base_url
            parsed_url = urlparse(self.base_url)
        elif parsed_url.scheme not in ["http", "https"]:
            # error if non HTTP scheme is given
            msg = f'\nBase URL in {config_file} must be HTTP or HTTPS, ' +\
                f'"\n{parsed_url.scheme.upper()}" given:\n{self.base_url}'
            self.exit(msg)

        #  ensure there is a netloc or path after the http(s)://
        if not (parsed_url.netloc or parsed_url.path):
            msg = f'\nInvalid URL in {config_file}:\n{self.base_url}'
            self.exit(msg)

        # if the base URL is valid, test it with a GET request to make sure it works
        # http://docs.python-requests.org/en/master/api#requests.Response
        r = None  # holds the response object
        try:
            r = requests.get(self.base_url)
        except requests.exceptions.RequestException as e:
            self.exit(f'\nProblem with {config_file}:\n' + str(e))

        msg = f'Unreachable base URL in {config_file}:\n{self.base_url}'
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
        msg = f'\n\n!!!\n\n{msg}\n\n!!!\n\n'
        # if we're running from within a pytest session
        if "pytest" in sys.modules:
            import pytest
            pytest.exit(msg)
        exit(msg)

    def save(self, config_file: str = None) -> None:
        """Saves Config options to JSON."""
        output = {}
        for opt in self.ALL_OPTIONS:
            output[opt] = getattr(self, opt)
        if config_file:
            with open(config_file, 'w') as f:
                f.write(json.dumps(output, indent=4))
