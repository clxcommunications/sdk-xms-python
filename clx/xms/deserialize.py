# -*- coding: utf-8 -*-

"""JSON deserializer for API classes.

Note, this module is mainly intended for internal use and the API may
change in the future

"""

import binascii
import iso8601
from clx.xms import api
from clx.xms.exceptions import UnexpectedResponseException

def _date_time(json, date_string):
    """Deserializes the given string into a `DateTime`.

    Assumes the string is in ISO-8601 format.

    @param string $json original JSON message
    @param string $str  the string holding the date time
    @return DateTime a date time
    @throws UnexpectedResponseException if given invalid time string
    """
    try:
        return iso8601.parse_date(date_string)
    except iso8601.ParseError as ex:
        raise UnexpectedResponseException(ex.args + (json,))

def _batch_response_helper(json, fields, batch):
    """Helper that populates the given batch result.

    The batch is populated from a dictionary representation of the
    JSON document.

    :param json: original JSON string
    :param fields: the JSON fields
    :param batch: the target object
    :return: None

    """

    batch.batch_id = fields['id']
    batch.recipients = fields['to']
    batch.sender = fields['from']
    batch.canceled = fields['canceled']

    if 'delivery_report' in fields:
        batch.delivery_report = fields['delivery_report']

    if 'send_at' in fields:
        batch.send_at = _date_time(json, fields['send_at'])

    if 'expire_at' in fields:
        batch.expire_at = _date_time(json, fields['expire_at'])

    if 'created_at' in fields:
        batch.created_at = _date_time(json, fields['created_at'])

    if 'modified_at' in fields:
        batch.modified_at = _date_time(json, fields['modified_at'])

    if 'callback_url' in fields:
        batch.callback_url = fields['callback_url']

def _convert_parameters(params):
    """Converts an object describing parameter mappings to associative
    arrays.

    We want an associative array but since `json_decode` produces an
    object whose fields correspond to the substitutions we need to do
    a bit of conversion.

    :param params: the parameter mapping object
    :return: the parameter mappings
    """

    return params

def _batch_response_from_fields(json, fields):
    """Helper that creates and populates a batch result object.

    The result is populated from a dictionary representation of the
    JSON document.

    :param json: the JSON formatted string
    :param fields: the `json_decode` containing the result
    :return: the parsed result
    :raises UnexpectedResponseException: if the JSON contained an
        unexpected message type

    """

    if fields['type'] == 'mt_text':
        result = api.MtBatchTextSmsResult()
        result.body = fields['body']

        if 'parameters' in fields:
            result.parameters = _convert_parameters(fields['parameters'])
    elif fields['type'] == 'mt_binary':
        result = api.MtBatchBinarySmsResult()
        result.udh = binascii.unhexlify(fields['udh'])
        result.body = binascii.a2b_base64(fields['body'])
    else:
        raise UnexpectedResponseException(
            "Received unexpected batch type " + fields['type'],
            json
        )

    # Read the common fields.
    _batch_response_helper(json, fields, result)

    return result

def batch_result(response):
    """Reads a request response containing a batch result.

    If the ``type`` field has the value ``mt_text`` then an
    :py:class:`MtBatchSmsTextCreate` object is returned, if the value
    is ``mt_binary`` then an :py:class:`MtBatchTextSmsCreate` object is
    returned, otherwise an exception is thrown.

    :param response: the response object to interpret
    :return: the parsed result
    :rtype: MtBatchTextSmsResult or MtBatchBinarySmsResult
    :raises UnexpectedResponseException: if the JSON contained
        an unexpected message type

    """

    json = response.text
    fields = response.json()
    return _batch_response_from_fields(json, fields)

def batch_delivery_report(response):
    """Reads a JSON blob describing a batch delivery report.

    :param response: An XMS response carrying a JSON body
    :vartype response: Response

    :return: the parsed batch delivery report
    :rtype: BatchDeliveryReport

    :raises UnexpectedResponseException: if the JSON contained an
    unexpected message type
    """

    json = response.text
    fields = response.json()

    if 'type' not in fields or fields['type'] != 'delivery_report_sms':
        raise UnexpectedResponseException("Expected delivery report", json)

    def report_status(status):
        """Helper used to populate statuses property."""

        result = api.BatchDeliveryReportStatus()
        result.code = status['code']
        result.status = status['status']
        result.count = status['count']
        if 'recipients' in status:
            result.recipients = status['recipients']
        return result

    result = api.BatchDeliveryReport()
    result.batch_id = fields['batch_id']
    result.total_message_count = fields['total_message_count']
    result.statuses = [report_status(s) for s in fields['statuses']]

    return result

def batch_recipient_delivery_report(response):
    """Reads a batch recipient delivery report from the given JSON text.

    :param response: an XMS response
    :vartype response: Response

    :returns: a delivery report
    :rtype: BatchRecipientDeliveryReport

    :raises UnexpectedResponseException: if the JSON contained an
      unexpected message type
    """

    json = response.text
    fields = response.json()

    expected_type = 'recipient_delivery_report_sms'
    if 'type' not in fields or fields['type'] != expected_type:
        raise UnexpectedResponseException(
            "Expected recipient delivery report", json)

    result = api.BatchRecipientDeliveryReport()

    result.batch_id = fields['batch_id']
    result.recipient = fields['recipient']
    result.code = fields['code']
    result.status = fields['status']
    result.status_at = _date_time(json, fields['at'])

    if 'status_message' in fields:
        result.statusMessage = fields['status_message']

    if 'operator' in fields:
        result.operator = fields['operator']

    if 'operator_status_at' in fields:
        result.operatorStatusAt = _date_time(
            json, fields['operator_status_at'])

    return result
