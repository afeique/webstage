"""Defines a Config class for storing configuration options."""

import os
import json
import pytest


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
            with open(config_file, 'w') as f:
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
