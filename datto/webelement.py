"""Defines an encapsulated selenium webelement with english-language methods for searching and asserting."""

import selenium
from typing import Union

class WebElement():
    """Encapsulates a selenium webelement with additional information and methods for assertions."""

    def __init__(self, something: selenium.webdriver.remote.webelement.WebElement):
        pass

    def and_it_has_text(self, something: str):
        pass

    def and_it_has_html(self, something: str):
        pass
