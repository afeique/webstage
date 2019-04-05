"""Defines an encapsulated selenium webelement with english-language methods for searching and asserting."""

from selenium.webdriver.remote.webelement import WebElement


class Element(WebElement):
    """Encapsulates a selenium webelement with additional information and methods for assertions."""

    def __init__(self, webElement: WebElement):
        self.webElement = webElement

    def __getattr__(self, attr: str):
        return getattr(self.webElement, attr)

    def andHasText(self, text: str):
        """Check for text in a given element"""
        pass

    def andHasHtml(self, html: str):
        """Check for HTML in a given element"""
        pass
