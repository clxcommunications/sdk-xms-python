# -*- coding: utf-8 -*-

"""Collection of exceptions raised by the XMS SDK.
"""

class ApiException(Exception):
    """Base class for exceptions thrown within the XMS SDK"""

class UnexpectedResponseException(ApiException):
    """Raised when XMS gave an unexpected response"""

class ErrorResponseException(ApiException):
    """Exception used when XMS responded with an error message.

    :param message: the human readable error message
    :vartype message: str

    :param code: the machine readable error code
    :vartype code: str
    """

    def __init__(self, message, code):
        ApiException.__init__(self, message, code)
