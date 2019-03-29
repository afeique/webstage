"""Defines an Actor class representing a user and used to encapsulate drivers."""

import selenium
from typing import Union

class Actor():
    def __init__(self, webdriver: selenium.webdriver.Remote):
        self.webdriver = webdriver

    def go_to(self, url: str):
        self.webdriver.get(url)
        return self

    def see(self, something: Union[str, selenium.webdriver.remote.webelement.WebElement]):
        pass

    def and_see(self, something: Union[str, selenium.webdriver.remote.webelement.WebElement]):
        pass
