"""This module is used exclusively for storing and testing snippets
directly in the python interpreter, for REPL.
"""

import sure
import expects
from selenium import webdriver

command_executor = "http://127.0.0.1:4444/wd/hub"
desired_capabilities = {
    "browserName": "chrome",
    "chromeOptions": {
        "args": [
            "--disable-extensions",
            "--disable-web-security"
        ]
    }
}

driver = webdriver.Remote(command_executor, desired_capabilities)
driver.maximize_window()
driver.get("http://higgs-boson")
driver.get("/configure/device")