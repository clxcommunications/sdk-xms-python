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

class NotFoundException(ApiException):
    """Exception indicating that a requested resources did not exist in
    XMS.

    This exception is thrown, for example, when attempting to retrieve
    a batch with an invalid batch identifier.

    :param url: URL to the missing resource.
    :vartype url: str

    """

    def __init__(self, url):
        ApiException.__init__(self, 'No resource found at "%s"' % url)

class UnauthorizedException(ApiException):
    """Exception indicating that XMS did not accept the service plan ID
    and authentication token.

    :param service_plan_id: the service plan identifier
    :vartype service_plan_id: str
    :param token: the authentication token
    :vartype token: str

    """

    def __init__(self, service_plan_id, token):
        fmt = 'Authentication failed with service plan "%s"'
        ApiException.__init__(self, fmt % service_plan_id)

        self._service_plan_id = service_plan_id
        self._token = token

    @property
    def service_plan_id(self):
        """The service plan identifier that did not pass authentication.

        type: *str*

        """
        return self._service_plan_id

    @property
    def token(self):
        """The authentication token that was not accepted.

        type: *str*

        """
        return self._token
