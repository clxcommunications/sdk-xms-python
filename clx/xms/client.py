# -*- coding: utf-8 -*-

"""
XMS Client module
"""

import logging
# from datetime import datetime
from urllib import quote_plus, urlencode
import requests
import clx.xms.__about__
from clx.xms import deserialize
from clx.xms import serialize

class Client(object):
    """Client used to communicate with the XMS server.

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
          print('Error creating batch: %s' % ex.getMessage())

    and to fetch a batch we may use the code (with ``client`` being
    the same variable as above)::

      try:
          batch = client.fetch_batch('{a batch identifier}')
          print('The batch was sent from %s' % batch.sender())
      except Exception as ex:
          print('Error fetching batch: %s' % ex.getMessage())

    .. _Requests: http://python-requests.org/

    """

    # DEFAULT_ENDPOINT = "https://api.clxcommunications.com/xms"
    DEFAULT_ENDPOINT = "http://localhost:8000/xms"

    _LOGGER = logging.getLogger('clx.xms.client')

    def __init__(self, service_plan_id, token, endpoint=DEFAULT_ENDPOINT):
        """
        :param service_plan_id: service plan identifier.
        :param token: authentication token
        :param endpoint: URL to XMS endpoint
        """

        self._session = requests.Session()
        self._service_plan_id = service_plan_id
        self._token = token
        self._endpoint = endpoint

    def _headers(self):
        return {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self._token,
            'XMS-SDK-Version': clx.xms.__about__.__version__
        }

    def _url(self, sub_path):
        """Builds an endpoint URL for the given sub-path.

        :param sub_path: the sub-path
        :return: an URL
        :rtype: str
        """

        return self._endpoint + '/v1/' + self._service_plan_id + sub_path

    def _batch_url(self, batch_id, sub_path=''):
        """Builds an endpoint URL for the given batch and sub-path.

        :param batch_id: a batch identifier
        :param sub_path: additional sub-path
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

        :param group_id: a group identifier
        :param sub_path: additional sub-path
        :returns: a complete URL
        :rtype: str
        :raises ValueError: if given an invalid group ID

        """

        egid = quote_plus(group_id)

        if egid == '':
            raise ValueError("Empty group ID given")

        return self._url('/groups/' + egid + sub_path)

    def _check_response(self, resp):
        Client._LOGGER.debug('Request{%s} Response(code %d){%s}',
                             resp.request.body, resp.status_code, resp.text)

        # If "200 OK" or "201 Created".
        if resp.status_code == 200 or resp.status_code == 201:
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

        return resp

    def _delete(self, url):
        resp = self._session.delete(url, headers=self._headers())
        return self._check_response(resp)

    def _get(self, url):
        resp = self._session.get(url, headers=self._headers())
        return self._check_response(resp)

    def _post(self, url, fields):
        resp = self._session.post(url, json=fields, headers=self._headers())
        return self._check_response(resp)

    def _put(self, url, fields):
        resp = self._session.put(url, json=fields, headers=self._headers())
        return self._check_response(resp)

    def create_batch(self, batch):
        """Creates the given batch.

        :param batch: the text or binary batch to create
        :vartype batch: clx.xms.api.MtBatchTextSmsCreate or
            clx.xms.api.MtBatchBinarySmsCreate
        :returns: the batch result
        :rtype: clx.xms.api.MtBatchTextSmsResult or
            clx.xms.api.MtBatchBinarySmsResult
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
        :param MtBatchTextSmsCreate batch: the replacement batch
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

        :param string batch_id: identifier of the batch
        :param MtBatchTextSmsUpdate batch: the update description
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

        :param string batch_id: the batch identifier
        :returns: nothing

        """

        self._delete(self._batch_url(batch_id))

    def _create_batch(self, batch, sender, recipients, kwargs):
        batch.sender = sender
        batch.recipients = recipients

        if 'tags' in kwargs:
            batch.tags = kwargs['tags']

        if 'send_at' in kwargs:
            batch.send_at = kwargs['send_at']

        if 'expire_at' in kwargs:
            batch.expire_at = kwargs['expire_at']

        return self.create_batch(batch)

    def create_text_batch(self, sender, recipients, body, **kwargs):
        """
        Creates a text batch.
        """

        batch = clx.xms.api.MtBatchTextSmsCreate()
        batch.body = body
        return self._create_batch(batch, sender, recipients, kwargs)

    def create_binary_batch(self, sender, recipients, udh, body, **kwargs):
        """
        Creates a binary batch.
        """

        batch = clx.xms.api.MtBatchBinarySmsCreate()
        batch.body = body
        batch.udh = udh
        return self._create_batch(batch, sender, recipients, kwargs)

    def fetch_batch(self, batch_id):
        """Fetches the batch with the given batch identifier.

        :param string $batchId batch identifier
        :type batch_id: str
        :returns: the corresponding batch
        :rtype: MtBatchSmsResult

        """

        result = self._get(self._batch_url(batch_id))
        return deserialize.batch_result(result)

    def create_batch_dry_run(self, batch, num_recipients=None):
        """Simulates sending the given batch.

        The method takes an optional argument for instructing XMS to
        respond with per-recipient statistics, if non-null then this
        number of recipients will be returned in the result.

        :param batch: the batch to simulate
        :vartype batch: MtBatchSmsCreate

        :param num_recipients: number of recipients to show in
            per-recipient result
        :vartype num_recipients: int or None
        :return: result of dry-run
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

        :param string batch_id: the batch identifier
        :returns: a list of tags
        :rtype: list[str]

        """

        result = self._get(self._batch_url(batch_id, '/tags'))
        return deserialize.tags(result)

    def fetch_delivery_report(self, batch_id, kind=None,
                              status=None, code=None):
        """Fetches a delivery report for a batch.

        The report type can be either "full" or "summary" and when
        "full" the report includes the individual recipients.

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

        :param batch_id: identifier of the batch
        :vartype batch_id: str

        :param kind: delivery report type
        :vartype kind: str or None

        :param status: statuses to fetch
        :vartype status: set[str]

        :param code: codes to fetch
        :vartype code: set[int]

        :returns: the batch delivery report
        :rtype: BatchDeliveryReport

        """

        params = {}

        if kind:
            params['type'] = kind

        if status:
            params['status'] = ','.join(status)

        if code:
            params['code'] = ','.join(code)

        path = '/delivery_report'

        if params:
            path += '?' + urlencode(params)

        result = self._get(self._batch_url(batch_id, path))
        return deserialize.batch_delivery_report(result)

    def fetch_recipient_delivery_report(self, batch_id, recipient):
        """Fetches a delivery report for a specific batch recipient.

        :param batch_id: the batch identifier
        :vartype batch_id: str

        :param recipient: the batch recipient
        :vartype recipient: str

        :returns: the delivery report
        :rtype: BatchRecipientDeliveryReport
        """

        path = '/delivery_report/' + quote_plus(recipient)
        result = self._get(self._batch_url(batch_id, path))
        return deserialize.batch_recipient_delivery_report(result)

    def create_group(self, group):
        """Creates the given group.

        :param group: group description
        :vartype group: GroupCreate
        :return: the created group
        :rtype: GroupResult

        """

        fields = serialize.group_create(group)
        response = self._post(self._url('/groups'), fields)
        return deserialize.group_result(response)
