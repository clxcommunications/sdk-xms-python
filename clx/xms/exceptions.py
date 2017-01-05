# -*- coding: utf-8 -*-

"""Collection of exceptions raised by the XMS SDK.
"""

class ApiException(Exception):
    """Base class for exceptions thrown within the XMS SDK"""

class UnexpectedResponseException(ApiException):
    """Raised when XMS gave an unexpected response"""
