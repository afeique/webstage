"""Defines an Actor class representing a user and used to encapsulate drivers."""

from typing import Union
from urllib.parse import urlparse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Remote as WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .config import Config
from .element import Element


class Actor():
    """Encapsulates the selenium remote webdriver class"""

    def __init__(self, driver: WebDriver, config: Config):
        self.driver = driver
        self.base_url = config.base_url

        self.driver.maximize_window()
        self.driver.get(config.base_url)

    # def __getattr__(self, attr: str):
    #     # passthru unknown attribute calls to the encapsulated webdriver
    #     return self.driver.__getattribute__(attr)

    def finish(self):
        """Cleanup"""
        self.driver.close()

    def goto(self, url: str):
        """Go to a particular url, or a path under the base url"""
        parsed_url = urlparse(url)
        # if there is no scheme and netloc, this is a path under the base url
        if not parsed_url.scheme and not parsed_url.path:
            # prepend the base url
            url = f'{self.base_url}/{parsed_url.path.lstrip("/")}'
            parsed_url = urlparse(url)
        self.driver.get(url)

    def see(self, something: Union[str, WebElement]) -> Element:
        """Check if a particular element exists on the page"""
        if type(something) is str:
            # convert everything to an xpath
            # id
            if something.startswith("#"):
                return Element(self.driver.find_element_by_id(something))
            # class
            if something.startswith("."):
                return Element(self.driver.find_element_by_class_name(something))
            # xpath
            if something.startswith("//"):
                return Element(self.driver.find_element_by_xpath(something))
            # CSS selector
            try:
                return Element(self.driver.find_element_by_css_selector(something))
            except NoSuchElementException:
                return Element(self.driver.find_element_by_name(something))

    def see_link(self, text: str):
        """See a link with given text"""
        return Element(self.driver.find_element_by_partial_link_text(text))
