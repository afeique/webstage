"""Defines an Actor class representing a user and used to encapsulate drivers."""

import selenium
from typing import Union

from .webelement import WebElement

class Actor(selenium.webdriver.Remote):
    def __init__(self, baseUrl: str):
        self.webdriver = webdriver
        self.baseUrl = baseUrl

    def __getattr__(self, attr: str):
        """Passthrough calls to unknown attributes to the encapsulated webdriver"""
        if hasattr(self.webdriver, attr):
            return getattr(self.webdriver, attr)
        return super().__getattribute__(attr)

    def goto(self, url: str):
        """Go to a particular url, or a page under the base url"""
        if url.startswith("http://")
        self.webdriver.get(url)

    def see(self, something: Union[str, selenium.webdriver.remote.webelement.WebElement]):
        if type(something) is str:
            # convert everything to an xpath
            # id
            if something.startswith("#"):
                return WebElement(self.webdriver.find_element_by_id(something))
            # class
            elif something.startswith("."):
                return WebElement(self.webdriver.find_element_by_class(something))
            # xpath
            elif something.startswith("//"):
                return WebElement(self.webdriver.find_element_by_xpath(something))
            else:
                try:
                    return WebElement(self.webdriver.find_element_by_css_selector(something))
                except selenium.common.exceptions.NoSuchElementException:
                    return WebElement(self.webdriver.find_element_by_name(something))

    def andSee(self, something: Union[str, selenium.webdriver.remote.webelement.WebElement]):
        """Alias for see()."""
        return self.see(something)

    def sees(self, something: Union[str, selenium.webdriver.remote.webelement.WebElement]):
        """Alias for see()."""
        return self.see(something)

    def seeLink(self, text: str):
        return WebElement(self.webdriver.find_element_by_partial_link_text(text))

