"""Defines an encapsulated selenium webelement with english-language methods for searching and asserting."""

from selenium.webdriver.remote.webelement import WebElement


class Element(WebElement):
    """Encapsulates a selenium webelement with additional information and methods for assertions."""

    def __init__(self, web_element: WebElement):
        self.web_element = web_element

    def __getattr__(self, attr: str):
        return getattr(self.web_element, attr)

    def and_has_text(self, text: str):
        """Check for text in a given element"""
        pass

    def and_has_html(self, html: str):
        """Check for HTML in a given element"""
        pass
