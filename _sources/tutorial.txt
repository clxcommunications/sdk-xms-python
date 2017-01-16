SMS REST API tutorial
=====================

The purpose of this document is to present the basic concepts of the
CLX Communications HTTP REST Messaging API and how to use it from
Python using the HTTP REST Messaging API SDK.

HTTP REST Messaging API basics
------------------------------

HTTP REST Messaging API is a REST API that is provided by CLX
Communications for sending and receiving SMS messages. It also
provides various other services supporting this task such as managing
groups of recipients, tagging, and so forth.

Note, for brevity we will in this document refer to HTTP REST
Messaging API as *XMS API* and the HTTP REST Messaging API service or
HTTP endpoint as *XMS*.

A great benefit of the XMS API is that it allows you to easily create
and send *batch SMS messages*, that is, SMS messages that can have
multiple recipients. When creating a batch message it is possible to
use *message templates*, which allows each recipient to receive a
personalized message.

To use XMS it is necessary to have a *service plan identifier* and an
*authentication token*, which can be obtained by creating an XMS
service plan.

For full documentation of the XMS API please refer to the `REST API
documentation site`_. The documentation site contains up-to-date
information about, for example, status and error codes.

.. _`REST API documentation site`:
  https://www.clxcommunications.com/docs/sms/http-rest.html

Interacting with XMS through Python
-----------------------------------

Using this Python SDK, all interaction with XMS happens through an
*XMS client*, which can be created using the service plan identifier
and authentication token. Further configuration can be performed on
the XMS client but in the typical case a service plan identifier and
authentication token is sufficient.

Once an XMS client has been created it is possible to send requests to
XMS and receive its responses. This is done by calling a suitable
method on the XMS client, supplying arguments as necessary, and
receiving the response as the return value.

This SDK has a focus on asynchronous operation and all interaction
with XMS happens asynchronously. Therefore, while synchronous methods
are supplied within the library their use is discouraged in most
practical applications.

The arguments passed to a connection method are sometimes very simple,
fetching a previously create batch simply requires the batch
identifier as argument. Other times the arguments are complicated, for
example to create the batch it may be necessary to supply a large
number of arguments that specify destination addresses, the message
body, expiry times, and so on. For such complex arguments we use
classes whose methods correspond to the different parameters that are
relevant for the request.

In general the terms used in XMS carry through to the Python API with
one major exception. The REST API uses the terms *to* and *from* to
indicate a message originator and message destination, respectively.
In the Python API these are instead denoted *recipient* and *sender*.
The cause of this name change is to have less confusing and more
idiomatic Python method and property names.

Connection management
---------------------

The first step in using the XMS SDK is to create an XMS client object,
this object is instantiated from the :class:`.Client` class and it
describes everything we need in order to talk with the XMS API
endpoint. The minimal amount of information needed are the service
plan identifier and the authentication token and, as previously
mentioned, these will be provided to you when creating an XMS service.

Assuming we have been given the service plan identifier "myplan" and
authentication token "mytoken" then an XMS client ``client`` can be
created as follows::

  client = clx.xms.Client('myserviceplan', 'mytoken')

Once created the client can be used to interact with XMS in the ways
described in the following sections of this tutorial.

By default the connection will use
``https://api.clxcommunications.com/xms`` as XMS endpoint. This can be
overridden by providing an extra argument to the :class:`.Client`
constructor. For example, the code::

  client = clx.xms.Client(
      'myserviceplan',
      'mytoken',
      'https://my.test.host:3000/my/base/path'
  )

would make the client object believe that the `batches endpoint`_
endpoint is
``https://my.test.host:3000/my/base/path/v1/myplan/batches``.

.. _`batches endpoint`:
  https://www.clxcommunications.com/docs/sms/http-rest.html#batches-endpoint)

Sending batches
---------------

Creating a batch is typically one of the first things one would like
to do when starting to use XMS. To create a batch we must specify, at
a minimum, the originating address (typically a short code), one or
more recipient addresses (typically MSISDNs), and the message body.
Sending a simple hello world message to one recipient is then
accomplished using::

  batch_params = clx.xms.api.MtBatchTextSmsCreate()
  batch_params.sender = '12345'
  batch_params.recipients = {'987654321'}
  batch_params.body = 'Hello, World!'
  result = client.create_batch(batch_params)

You will notice a few things with this code. We are using a ``client``
variable that corresponds to an XMS client that we assume has been
previously created. We are calling the
:meth:`~clx.xms.client.Client.create_batch` method on the client
with a single argument that describes the batch we wish to create.

Describing the batch is done using an :class:`.MtBatchTextSmsCreate`
object. For a batch with a binary body you would similarly describe it
using an :class:`.MtBatchBinarySmsCreate` object.

The return value of a batch create call is a
:class:`.MtBatchTextSmsResult` or :class:`.MtBatchBinarySmsResult`
object that contains not only the submitted batch information but also
information included by XMS, such that the unique batch identifier,
the creation time, etc. For example, to simply print the batch
identifier we could add the code::

  print('Batch id is %s' % result.batch_id)

It is not much harder to create a more complicated batch, for example,
here we create a parameterized message with multiple recipients and a
scheduled send time::

  batch_params = clx.xms.api.MtBatchTextSmsCreate()
  batch_params.sender = '12345'
  batch_params.recipients = {'987654321', '123456789', '567894321'}
  batch_params.body = 'Hello, ${name}!'
  batch_params.parameters['name'] = {
      '987654321': 'Mary',
      '123456789': 'Joe',
      'default': 'valued customer'
  }
  batch_params.send_at = datetime(2016, 12, 20, 10, 0, 0, 0, UTC)
  batch = client.create_batch(batch_params)

On the other hand, for the common case where we need to send a text or
binary message to a single recipient there are
:meth:`~clx.xms.client.Client.create_text_message` and
:meth:`~clx.xms.client.Client.create_binary_message` which do not
require an API object. For example::

  client.create_text_message(
      sender='1234',
      recipient='987654321',
      body='hello')

and::

  client.create_binary_message(
      sender='1234',
      recipient='987654321',
      udh=b'\xf0\x0f',
      body=b'\x00')

Internally these create batches with a single recipient and they
return values of types :class:`.MtBatchTextSmsResult` and
:class:`.MtBatchBinarySmsResult`, respectively.

Fetching batches
----------------

If you have a batch identifier and would like to retrieve information
concerning that batch then it is sufficient to use the
:meth:`~clx.xms.client.Client.fetch_batch` method. Thus, if the
desired batch identifier is available in the variable ``batch_id``
then one could write::

  batch_id = # …
  result = client.fetch_batch(batch_id)
  print('Batch id is %s' % result.batch_id)

Note, since :meth:`~clx.xms.client.Client.fetch_batch` does not know
ahead of time whether the fetched batch is textual or binary it
returns a value of the type :class:`~clx.xms.api.MtBatchSmsResult`.
This type is the base class of
:class:`~clx.xms.api.MtBatchTextSmsResult` and
:class:`~clx.xms.api.MtBatchBinarySmsResult` and you may need to use,
for example, ``isinstance`` to determine the actual type.

Listing batches
---------------

Once you have created a few batches it may be interesting to retrieve
a list of all your batches. Retrieving listings of batches is done
through a *paged result*. This means that a single request to XMS may
not retrieve all batches. As a result, when calling the
:meth:`~clx.xms.client.Client.fetch_batches` method on your XMS client
it will not simply return a list of batches but rather a
:class:`clx.xms.api.Pages` object. The pages object in turn can be
used to fetch specific pages or iterate over all available pages while
transparently performing necessary page requests.

To limit the number of batches in the list it is also possible to
supply a filter that will restrict the fetched batches, for example to
those sent after a particular date or having a specific tag or sender.

More specifically, to print the identifier of each batch sent on
2016-12-01 and having the tag "signup_notification", we may write
something like the following::

  pages = client.fetch_batches(
      tag={'signup_notification'},
      start_date=datetime.date(2016, 12, 1),
      end_date=datetime.date(2016, 12, 2));

  for page in pages:
      for batch in page:
          print('Batch ID: %s' % batch.batch_id)

Other XMS requests
------------------

We have only shown explicitly how to create, list and fetch batches
but the same principles apply to all other XMS calls within the SDK.
For example, to fetch a group one could use the previously given
instructions for fetching batches and simply use
:meth:`~clx.xms.client.Client.fetch_group` with a group identifier.

Canceling a batch and deleting a group is the same as fetching with
the exception that they do not return any result.

Handling errors
---------------

Any error that occurs during an API operation will result in an
exception being thrown. The exceptions raised explicitly by the SDK
all inherit from the :class:`~clx.xms.exceptions.ApiException` class
and they are

:class:`~clx.xms.exceptions.ErrorResponseException`
  If the XMS server responded with a JSON error object containing an
  error code and error description. See the `HTTP Errors`_ section in
  the XMS documentation.

:class:`~clx.xms.exceptions.NotFoundException`
  If the XMS server response indicated that the desired resource
  does not exist. In other words, if the server responded with
  HTTP status 404 Not Found. During a fetch batch or group
  operation this exception would typically indicate that the batch
  or group identifier is incorrect.

:class:`~clx.xms.exceptions.UnauthorizedException`
  Thrown if the XMS server determined that the authentication
  token was invalid for the service plan.

:class:`~clx.xms.exceptions.UnexpectedResponseException`
  If the XMS server responded in a way that the SDK did not expect and
  cannot handle, the complete HTTP response body can be retrieved from
  the exception object using the
  :attr:`~clx.xms.exceptions.UnexpectedResponseException.http_body`
  attribute.

Note, internally this SDK uses the Requests_ library and when
performing XMS operations one may therefore encounter exceptions
raised by Requests. See the `Requests errors and exceptions`_
documentation for more.

Due to the use of exceptions, a typical XMS operation in the Python
SDK is surrounded by a try-catch statement such as::

  try:
      # Invoke synchronous XMS client call here.
  except (requests.exceptions.RequestException, clx.xms.exceptions.ApiException) as ex:
      print('Failed to communicate with XMS: %s' % str(ex))

.. _`HTTP Errors`:
    https://www.clxcommunications.com/docs/sms/http-rest.html#http-errors
.. _Requests: http://docs.python-requests.org/en/master/
.. _`Requests errors and exceptions`:
    http://docs.python-requests.org/en/master/user/quickstart/#errors-and-exceptions
