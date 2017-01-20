# -*- coding: utf-8 -*-

"""
XMS Client module

"""

from __future__ import absolute_import, division, print_function

try:
    from urllib.parse import quote_plus, urlencode
except ImportError:
    from urllib import quote_plus, urlencode

import logging
import requests
import clx.xms.__about__
from clx.xms import deserialize, serialize, api

class Client(object):
    """Client used to communicate with the XMS server.

    :param str service_plan_id: service plan identifier
    :param str token: authentication token
    :param str endpoint: URL to XMS endpoint
    :param float timeout: Connection and read timeout, in seconds

    This class will use the Requests_ library to communicate with XMS.
    It is intended as a long lived object and can handle multiple
    requests.

    For example, to send a simple parameterized text batch to three
    recipients we may use code such as::

      client = clx.xms.Client('{my-service-plan-id}', '{my-token}')

      try:
          batch_params = clx.xms.api.MtBatchTextSmsCreate()
          batch_params.sender = '12345'
          batch_params.recipients = ['987654321', '123456789', '567894321']
          batch_params.body = 'Hello, ${name}!'
          batch_params.parameters = {
                  'name': {
                      '987654321': 'Mary',
                      '123456789': 'Joe',
                      'default': 'valued customer'
                  }
              }

          batch = client.create_text_batch(batch_params)
          print('The batch was given ID %s' % batch.batch_id)
      except Exception as ex:
          print('Error creating batch: %s' % str(ex))

    and to fetch a batch we may use the code (with ``client`` being
    the same variable as above)::

      try:
          batch = client.fetch_batch('{a batch identifier}')
          print('The batch was sent from %s' % batch.sender())
      except Exception as ex:
          print('Error fetching batch: %s' % str(ex))

    .. _Requests: http://python-requests.org/

    """

    DEFAULT_ENDPOINT = "https://api.clxcommunications.com/xms"
    """The default XMS endpoint URL. This is the endpoint that will be
    used unless a custom one is specified in the :class:`Client`
    constructor.

    """

    DEFAULT_TIMEOUT = 30.0
    """The default timeout value in seconds. This is used unless a custom
    timeout value is specified in :attr:`timeout`.

    """

    _LOGGER = logging.getLogger('clx.xms.client')

    def __init__(self, service_plan_id, token,
                 endpoint=DEFAULT_ENDPOINT, timeout=DEFAULT_TIMEOUT):

        self._session = requests.Session()
        self._service_plan_id = service_plan_id
        self._token = token
        self._endpoint = endpoint
        self._timeout = timeout

    @property
    def service_plan_id(self):
        """The service plan identifier used for this client.

        :type: str

        """
        return self._service_plan_id

    @property
    def token(self):
        """The authentication token used for this client.

        :type: str

        """
        return self._token

    @property
    def endpoint(self):
        """The XMS endpoint used by this client.

        :type: str

        """
        return self._endpoint

    @property
    def timeout(self):
        """The timeout value used for this client. In seconds.
      The connection and read timeout, in seconds, used in
      communication with XMS. The default is specified by the constant
      :const:`DEFAULT_TIMEOUT`.

        :type: float

        """
        return self._timeout

    def _headers(self):
        return {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self._token,
            'User-Agent': "sdk-xms-python/%s; %s" %
                          (clx.xms.__about__.__version__,
                           requests.utils.default_user_agent())
        }

    def _url(self, sub_path):
        """Builds an endpoint URL for the given sub-path.

        :param str sub_path: the sub-path
        :return: an URL
        :rtype: str

        """

        return self._endpoint + '/v1/' + self._service_plan_id + sub_path

    def _batch_url(self, batch_id, sub_path=''):
        """Builds an endpoint URL for the given batch and sub-path.

        :param str batch_id: a batch identifier
        :param str sub_path: additional sub-path
        :returns: a complete URL
        :rtype: str
        :raises ValueError: if given an invalid batch ID

        """

        ebid = quote_plus(batch_id)

        if ebid == '':
            raise  ValueError("Empty batch ID given")

        return self._url('/batches/' + ebid + sub_path)

    def _group_url(self, group_id, sub_path=''):
        """Builds an endpoint URL for the given group and sub-path.

        :param str group_id: a group identifier
        :param str sub_path: additional sub-path
        :returns: a complete URL
        :rtype: str
        :raises ValueError: if given an invalid group ID

        """

        egid = quote_plus(group_id)

        if egid == '':
            raise ValueError("Empty group ID given")

        return self._url('/groups/' + egid + sub_path)

    def _check_response(self, resp):
        """Checks the given HTTP response and returns it if OK.

        If any problem is found then a suitable exception is raised.
        This method also logs the request and response at the debug
        level.

        :param Response resp: HTTP response to check

        """

        Client._LOGGER.debug('Request{%s} Response(code %d){%s}',
                             resp.request.body, resp.status_code, resp.text)

        # If "200 OK" or "201 Created". We'll here assume any 2XX code is OK.
        if resp.status_code >= 200 and resp.status_code < 300:
            return resp
        # If "400 Bad Request" or "403 Forbidden".
        elif resp.status_code == 400 or resp.status_code == 403:
            error = deserialize.error(resp)
            raise clx.xms.exceptions.ErrorResponseException(
                error.text, error.code)
        # If "404 Not Found".
        elif resp.status_code == 404:
            raise clx.xms.exceptions.NotFoundException(resp.request.url)
        # If "401 Unauthorized"
        elif resp.status_code == 401:
            raise clx.xms.exceptions.UnauthorizedException(
                self._service_plan_id, self._token)
        else:
            raise clx.xms.exceptions.UnexpectedResponseException(
                "Unexpected HTTP status %s" % resp.status_code, resp.text)

    def _delete(self, url):
        resp = self._session.delete(
            url, headers=self._headers(), timeout=self._timeout)
        return self._check_response(resp)

    def _get(self, url):
        resp = self._session.get(
            url, headers=self._headers(), timeout=self._timeout)
        return self._check_response(resp)

    def _post(self, url, fields):
        resp = self._session.post(
            url, json=fields, headers=self._headers(), timeout=self._timeout)
        return self._check_response(resp)

    def _put(self, url, fields):
        resp = self._session.put(
            url, json=fields, headers=self._headers(), timeout=self._timeout)
        return self._check_response(resp)

    def create_text_message(self, sender, recipient, body):
        """Creates a text message to a single recipient.

        This is a convenience method that creates a text batch having
        a single recipient.

        :param str sender: the message sender
        :param str recipient: the message recipient
        :param str body: the message body
        :returns: the created batch
        :rtype: MtBatchTextSmsResult

        """

        batch = api.MtBatchTextSmsCreate()
        batch.sender = sender
        batch.recipients = {recipient}
        batch.body = body
        return self.create_batch(batch)

    def create_binary_message(self, sender, recipient, udh, body):
        """Creates a text message to a single recipient.

        This is a convenience method that creates a text batch having
        a single recipient.

        :param str sender: the message sender
        :param str recipient: the message recipient
        :param binary udh: the message User Data Header
        :param binary body: the message binary body
        :returns: the created batch
        :rtype: MtBatchBinarySmsResult

        """

        batch = api.MtBatchBinarySmsCreate()
        batch.sender = sender
        batch.recipients = {recipient}
        batch.udh = udh
        batch.body = body
        return self.create_batch(batch)

    def create_batch(self, batch):
        """Creates the given batch.

        :param batch: the text or binary batch to create
        :type batch: MtBatchTextSmsCreate or MtBatchBinarySmsCreate
        :returns: the batch result
        :rtype: MtBatchTextSmsResult or MtBatchBinarySmsResult

        """

        if hasattr(batch, 'udh'):
            fields = serialize.binary_batch(batch)
        else:
            fields = serialize.text_batch(batch)

        response = self._post(self._url('/batches'), fields)
        return deserialize.batch_result(response)

    def replace_batch(self, batch_id, batch):
        """Replaces the batch with the given ID with the given batch.

        :param str batch_id: identifier of the batch
        :param batch: the replacement batch
        :type batch: MtBatchTextSmsCreate or MtBatchBinarySmsCreate
        :return: the resulting batch
        :rtype: MtBatchTextSmsResult

        """

        if hasattr(batch, 'udh'):
            fields = serialize.binary_batch(batch)
        else:
            fields = serialize.text_batch(batch)

        response = self._put(self._batch_url(batch_id), fields)
        return deserialize.batch_result(response)

    def update_batch(self, batch_id, batch):
        """Updates the text batch with the given identifier.

        :param str batch_id: identifier of the batch
        :param batch: the update description
        :type batch: MtBatchTextSmsUpdate or MtBatchBinarySmsUpdate
        :returns: the updated batch
        :rtype: MtBatchTextSmsResult

        """

        if hasattr(batch, 'udh'):
            fields = serialize.binary_batch_update(batch)
        else:
            fields = serialize.text_batch_update(batch)

        result = self._post(self._batch_url(batch_id), fields)
        return deserialize.batch_result(result)

    def cancel_batch(self, batch_id):
        """Cancels the batch with the given batch identifier.

        :param str batch_id: the batch identifier
        :returns: nothing

        """

        self._delete(self._batch_url(batch_id))

    def fetch_batch(self, batch_id):
        """Fetches the batch with the given batch identifier.

        :param str batch_id: batch identifier
        :returns: the corresponding batch
        :rtype: MtBatchSmsResult

        """

        result = self._get(self._batch_url(batch_id))
        return deserialize.batch_result(result)

    def fetch_batches(self,
                      page_size=None,
                      senders=None,
                      tags=None,
                      start_date=None,
                      end_date=None):
        """Fetch the batches matching the given filter.

        Note, calling this method does not actually cause any network
        traffic. Listing batches in XMS may return the result over
        multiple pages and this call therefore returns an object of
        the type :class:`.Pages`, which will fetch result pages as
        needed.

        :param int page_size: Maximum number of batches to retrieve per page.
        :param senders: Fetch only batches having one of these senders.
        :type senders: set[str] or None
        :param tags: Fetch only batches having one or more of these tags.
        :type tags: set[str] or None
        :param start_date: Fetch only batches sent at or after this date.
        :type start_date: date or None
        :param end_date: Fetch only batches sent before this date.
        :type end_date: date or None
        :returns: the result pages
        :rtype: Pages

        """

        def fetcher(page):
            """Helper"""

            params = {'page': page}

            if page_size:
                params['page_size'] = page_size

            if senders:
                params['from'] = ','.join(sorted(senders))

            if tags:
                params['tags'] = ','.join(sorted(tags))

            if start_date:
                params['start_date'] = start_date.isoformat()

            if end_date:
                params['end_date'] = end_date.isoformat()

            query = urlencode(params)
            result = self._get(self._url('/batches?' + query))
            return deserialize.batches_page(result)

        return api.Pages(fetcher)

    def create_batch_dry_run(self, batch, num_recipients=None):
        """Simulates sending the given batch.

        The method takes an optional argument for instructing XMS to
        respond with per-recipient statistics, if non-null then this
        number of recipients will be returned in the result.

        :param MtBatchSmsCreate batch: the batch to simulate
        :param num_recipients:
            number of recipients to show in per-recipient result
        :type num_recipients: int or None
        :returns: result of dry-run
        :rtype: MtBatchDryRunResult

        """

        if hasattr(batch, 'udh'):
            fields = serialize.binary_batch(batch)
        else:
            fields = serialize.text_batch(batch)

        path = '/batches/dry_run'

        if num_recipients:
            path += '?per_recipient=true'
            path += '&number_of_recipients=%d' % num_recipients

        response = self._post(self._url(path), fields)
        return deserialize.batch_dry_run_result(response)

    def fetch_batch_tags(self, batch_id):
        """Fetches the tags associated with the given batch.

        :param str batch_id: the batch identifier
        :returns: a set of tags
        :rtype: set[str]

        """

        result = self._get(self._batch_url(batch_id, '/tags'))
        return deserialize.tags(result)

    def replace_batch_tags(self, batch_id, tags):
        """Replaces the tags of the given batch.

        :param str batch_id: identifier of the batch
        :param set[str] tags: the new set of batch tags
        :returns: the new batch tags
        :rtype: set[str]

        """

        fields = serialize.tags(tags)
        result = self._put(self._batch_url(batch_id, '/tags'), fields)
        return deserialize.tags(result)

    def update_batch_tags(self, batch_id, tags_to_add, tags_to_remove):
        """Updates the tags of the given batch.

        :param str batch_id: batch identifier
        :param set[str] tags_to_add: tags to add to batch
        :param set[str] tags_to_remove: tags to remove from batch
        :returns: the updated batch tags
        :rtype: set[str]

        """

        fields = serialize.tags_update(tags_to_add, tags_to_remove)
        result = self._post(self._batch_url(batch_id, '/tags'), fields)
        return deserialize.tags(result)

    def fetch_delivery_report(self, batch_id, kind=None,
                              status=None, code=None):
        """Fetches a delivery report for a batch.

        The report type can be one of ``None``, "full", or "summary".
        When "full" the report includes the individual recipients.
        When ``None`` then the XMS default value is used.

        The report can be further limited by status and code. For
        example, to retrieve a summary report limited to messages
        having delivery status "Delivered" or "Failed" and codes "0",
        "11", or "400", one could call::

          client.fetch_delivery_report(
              'MyBatchId',
              'summary',
              {'Delivered', 'Failed'},
              {0, 11, 400});

        If the non-identifier parameters are left unspecified then the
        XMS defaults are used. In particular, all statuses and codes
        are included in the report.

        :param str batch_id: identifier of the batch
        :param kind: delivery report type
        :type kind: str or None
        :param set[str] status: statuses to fetch
        :param set[int] code: codes to fetch
        :returns: the batch delivery report
        :rtype: BatchDeliveryReport

        """

        params = {}

        if kind:
            params['type'] = kind

        if status:
            params['status'] = ','.join(sorted(status))

        if code:
            params['code'] = ','.join([str(i) for i in sorted(code)])

        path = '/delivery_report'

        if params:
            path += '?' + urlencode(params)

        result = self._get(self._batch_url(batch_id, path))
        return deserialize.batch_delivery_report(result)

    def fetch_recipient_delivery_report(self, batch_id, recipient):
        """Fetches a delivery report for a specific batch recipient.

        :param str batch_id: the batch identifier
        :param str recipient: the batch recipient
        :returns: the delivery report
        :rtype: BatchRecipientDeliveryReport
        """

        path = '/delivery_report/' + quote_plus(recipient)
        result = self._get(self._batch_url(batch_id, path))
        return deserialize.batch_recipient_delivery_report(result)

    def create_group(self, group):
        """Creates the given group.

        :param GroupCreate group: group description
        :returns: the created group
        :rtype: GroupResult

        """

        fields = serialize.group_create(group)
        response = self._post(self._url('/groups'), fields)
        return deserialize.group_result(response)

    def replace_group(self, group_id, group):
        """Replaces the group with the given group identifier.

        :param str group_id: identifier of the group
        :param GroupCreate group: new group description
        :returns: the group after replacement
        :rtype: GroupResult

        """

        fields = serialize.group_create(group)
        result = self._put(self._group_url(group_id), fields)
        return deserialize.group_result(result)

    def update_group(self, group_id, group):
        """Updates the group with the given identifier.

        :param str group_id: identifier of the group
        :param GroupUpdate group: the update description
        :returns: the updated batch
        :rtype: GroupResult

        """

        fields = serialize.group_update(group)
        result = self._post(self._group_url(group_id), fields)
        return deserialize.group_result(result)

    def delete_group(self, group_id):
        """Deletes the group with the given group identifier.

        :param str group_id: the group identifier
        :returns: Nothing

        """

        self._delete(self._group_url(group_id))

    def fetch_group(self, group_id):
        """Fetches the group with the given group identifier.

        :param str group_id: group identifier
        :returns: the corresponding group

        """

        result = self._get(self._group_url(group_id))
        return deserialize.group_result(result)

    def fetch_groups(self, page_size=None, tags=None):
        """Fetch the groups matching the given filter.

        Note, calling this method does not actually cause any network
        traffic. Listing groups in XMS may return the result over
        multiple pages and this call therefore returns an object of
        the type :class:`.Pages`, which will fetch result pages as
        needed.

        :param page_size: Maximum number of groups to retrieve per page.
        :type page_size: int or None
        :param tags: Fetch only groups having or or more of these tags.
        :type tags: set[str] or None
        :returns: the result pages
        :rtype: Pages

        """

        def fetcher(page):
            """Helper"""

            params = {'page': page}

            if page_size:
                params['page_size'] = page_size

            if tags:
                params['tags'] = ','.join(sorted(tags))

            query = urlencode(params)
            result = self._get(self._url('/groups?' + query))
            return deserialize.groups_page(result)

        return api.Pages(fetcher)

    def fetch_group_members(self, group_id):
        """Fetches the that belong to the given group.

        :param str group_id: the group identifier
        :returns: a set of MSISDNs
        :rtype: set[str]

        """

        result = self._get(self._group_url(group_id, '/members'))
        return deserialize.group_members(result)

    def fetch_group_tags(self, group_id):
        """Fetches the tags associated with the given group.

        :param str group_id: the group identifier
        :returns: a set of tags
        :rtype: set[str]

        """

        result = self._get(self._group_url(group_id, '/tags'))
        return deserialize.tags(result)

    def replace_group_tags(self, group_id, tags):
        """Replaces the tags of the given group.

        :param str group_id: identifier of the group
        :param set[str] tags: the new set of group tags
        :returns: the new group tags
        :rtype: set[str]

        """

        fields = serialize.tags(tags)
        result = self._put(self._group_url(group_id, '/tags'), fields)
        return deserialize.tags(result)

    def update_group_tags(self, group_id, tags_to_add, tags_to_remove):
        """Updates the tags of the given group.

        :param str group_id: group identifier
        :param set[str] tags_to_add: tags to add to group
        :param set[str] tags_to_remove: tags to remove from group
        :returns: the updated group tags
        :rtype: set[str]

        """

        fields = serialize.tags_update(tags_to_add, tags_to_remove)
        result = self._post(self._group_url(group_id, '/tags'), fields)
        return deserialize.tags(result)

    def fetch_inbound(self, inbound_id):
        """Fetches the inbound message with the given identifier.

        The returned message is either textual or binary.

        :param str inbound_id: message identifier
        :returns: the fetched message
        :rtype: MoTextSms or MoBinarySms

        """

        eiid = quote_plus(inbound_id)

        if not eiid:
            raise ValueError("Empty inbound ID given")

        result = self._get(self._url("/inbounds/" + eiid))
        return deserialize.mo_sms(result)

    def fetch_inbounds(self,
                       page_size=None,
                       recipients=None,
                       start_date=None,
                       end_date=None):
        """Fetch inbound messages matching the given filter.

        Note, calling this method does not actually cause any network
        traffic. Listing inbound messages in XMS may return the result
        over multiple pages and this call therefore returns an object
        of the type :class:`.Pages`, which will fetch result pages as
        needed.

        :param page_size: The maximum number of messages to retrieve per page.
        :type page_size: int or None
        :param recipients: Fetch only messages having one of these recipients.
        :type recipients: set[str] or None
        :param start_date: Fetch only messages received at or after this date.
        :type start_date: date or None
        :param end_date: Fetch only messages received before this date.
        :type end_date: date or None
        :returns: the result pages
        :rtype: Pages

        """

        def fetcher(page):
            """Helper"""

            params = {'page': page}

            if page_size:
                params['page_size'] = page_size

            if recipients:
                params['to'] = ','.join(sorted(recipients))

            if start_date:
                params['start_date'] = start_date.isoformat()

            if end_date:
                params['end_date'] = end_date.isoformat()

            query = urlencode(params)
            result = self._get(self._url('/inbounds?' + query))
            return deserialize.inbounds_page(result)

        return api.Pages(fetcher)
