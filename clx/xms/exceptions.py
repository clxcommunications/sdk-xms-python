# -*- coding: utf-8 -*-

"""Collection of exceptions raised by the XMS SDK.

The exceptions raised by the API all inherit from the base class
:class:`ApiException`.

"""

from __future__ import absolute_import, division, print_function

class ApiException(Exception):
    """Base class for exceptions thrown within the XMS SDK"""

class UnexpectedResponseException(ApiException):
    """Raised when XMS gave an unexpected response

    :param message: useful message explaining the problem
    :type message: str

    :param http_body: the unexpected HTTP body
    :type http_body: str

    .. attribute:: http_body

      The unexpected HTTP body.

      :type: str
    """

    def __init__(self, message, http_body):
        ApiException.__init__(self, message)
        self.http_body = http_body

class ErrorResponseException(ApiException):
    """Exception used when XMS responded with an error message.

    :param message: the human readable error message
    :type message: str

    :param code: the machine readable error code
    :type code: str

    .. attribute:: error_code

      The machine readable error code.

      :type: str
    """

    def __init__(self, message, code):
        ApiException.__init__(self, message)
        self.error_code = code

class NotFoundException(ApiException):
    """Exception indicating that a requested resources did not exist in
    XMS.

    This exception is thrown, for example, when attempting to retrieve
    a batch with an invalid batch identifier.

    :param url: URL to the missing resource.
    :type url: str

    .. attribute:: url

      The failing URL.

      :type: str

    """

    def __init__(self, url):
        ApiException.__init__(self, 'No resource found at "%s"' % url)
        self.url = url

class UnauthorizedException(ApiException):
    """Exception indicating that XMS did not accept the service plan ID
    and authentication token.

    :param service_plan_id: the service plan identifier
    :type service_plan_id: str
    :param token: the authentication token
    :type token: str

    .. attribute:: service_plan_id

      The service plan identifier that did not pass authentication.

      :type: str

    .. attribute:: token

      The authentication token that was not accepted.

      :type: str

    """

    def __init__(self, service_plan_id, token):
        fmt = 'Authentication failed with service plan "%s"'
        ApiException.__init__(self, fmt % service_plan_id)

        self.service_plan_id = service_plan_id
        self.token = token
