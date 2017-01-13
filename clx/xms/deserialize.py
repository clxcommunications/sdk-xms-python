# -*- coding: utf-8 -*-

"""JSON deserializer for API classes.

Note, this module is mainly intended for internal use and the API may
change in the future

"""

from __future__ import absolute_import, division, print_function

import binascii
import iso8601
from clx.xms import api
from clx.xms.exceptions import UnexpectedResponseException

def _date_time(json, date_string):
    """Deserializes the given string into a `DateTime`.

    Assumes the string is in ISO-8601 format.

    :param str json original: JSON message
    :param str date_string: the string holding the date time
    :return: a date time
    :rtype: datetime
    :raises UnexpectedResponseException: if given invalid time string
    """
    try:
        return iso8601.parse_date(date_string)
    except iso8601.ParseError as ex:
        raise UnexpectedResponseException(str(ex), json)

def _batch_response_helper(json, fields, batch):
    """Helper that populates the given batch result.

    The batch is populated from a dictionary representation of the
    JSON document.

    :param str json: original JSON string
    :param dict fields: the JSON fields
    :param MtBatchSmsResult batch: the target object
    :return: None

    """

    batch.batch_id = fields['id']
    batch.recipients = set(fields['to'])
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

    :param str json: the JSON formatted string
    :param dict fields: the `json_decode` containing the result
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

def _check_response(response):
    """Reads the JSON object from the given response.

    :returns: The raw JSON string and the parsed JSON dictionary
    :rtype: tuple[str, dict]
    :raises UnexpectedResponseException: if response did not contain valid JSON

    """

    json = response.text
    try:
        return (json, response.json())
    except ValueError as ex:
        raise UnexpectedResponseException(str(ex), json)

def batch_result(response):
    """Reads a request response containing a batch result.

    If the ``type`` field has the value ``mt_text`` then an
    :class:`MtBatchSmsTextCreate` object is returned, if the value is
    ``mt_binary`` then an :class:`MtBatchTextSmsCreate` object is
    returned, otherwise an exception is thrown.

    :param Response response: the response object to interpret
    :return: the parsed result
    :rtype: MtBatchTextSmsResult or MtBatchBinarySmsResult
    :raises UnexpectedResponseException: if the JSON contained
        an unexpected message type

    """

    json, fields = _check_response(response)
    return _batch_response_from_fields(json, fields)

def batches_page(response):
    """Reads a JSON blob describing a page of batches.

    :param Response response: the response object to interpret
    :return: the parsed page
    :rtype: Page
    :raises UnexpectedResponseException: if the JSON contained an
        unexpected message type

    """

    json, fields = _check_response(response)

    result = api.Page()
    result.page = fields['page']
    result.size = fields['page_size']
    result.total_size = fields['count']
    result.content = [
        _batch_response_from_fields(json, s) for s in fields['batches']
    ]

    return result

def batch_dry_run_result(response):
    """Reads a JSON formatted string describing a dry-run result.

    :param Response response: the response object to interpret
    :return: the parsed result
    :rtype: MtBatchDryRunResult

    """

    def recipient(recipient_fields):
        """Helper used to populate ``per_recipient`` property."""

        recipient = api.DryRunPerRecipient()
        recipient.recipient = recipient_fields['recipient']
        recipient.number_of_parts = recipient_fields['number_of_parts']
        recipient.body = recipient_fields['body']
        recipient.encoding = recipient_fields['encoding']
        return recipient

    fields = response.json()

    result = api.MtBatchDryRunResult()
    result.number_of_recipients = fields['number_of_recipients']
    result.number_of_messages = fields['number_of_messages']

    if 'per_recipient' in fields:
        result.per_recipient = [recipient(r) for r in fields['per_recipient']]

    return result

def batch_delivery_report(response):
    """Reads a JSON blob describing a batch delivery report.

    :param Response response: An XMS response carrying a JSON body
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
            result.recipients = set(status['recipients'])
        return result

    result = api.BatchDeliveryReport()
    result.batch_id = fields['batch_id']
    result.total_message_count = fields['total_message_count']
    result.statuses = [report_status(s) for s in fields['statuses']]

    return result

def batch_recipient_delivery_report(response):
    """Reads a batch recipient delivery report from the given JSON text.

    :param Response response: an XMS response
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
        result.status_message = fields['status_message']

    if 'operator' in fields:
        result.operator = fields['operator']

    if 'operator_status_at' in fields:
        result.operator_status_at = _date_time(
            json, fields['operator_status_at'])

    return result

def error(response):
    """Reads a JSON blob containing an error response.

    :param Response response: an XMS response
    :returns: the decoded error
    :rtype: Error

    """

    fields = response.json()
    return api.Error(fields['code'], fields['text'])

def _auto_update_from_fields(fields):
    """Helper that creates a group auto update object from the given
    fields.

    :param fields: the fields representing the JSON blob
    :return: the created group auto update
    :rtype: GroupAutoUpdate

    """

    add_map = fields.get('add', {})
    remove_map = fields.get('remove', {})

    return api.GroupAutoUpdate(
        fields['to'],
        add_first_word=add_map.get('first_word', None),
        add_second_word=add_map.get('second_word', None),
        remove_first_word=remove_map.get('first_word', None),
        remove_second_word=remove_map.get('second_word', None))

def _group_result_from_fields(json, fields):
    """Helper that creates a group response object from the given fields.

    :param json: original JSON string
    :param fields: the JSON fields
    :return: the created group response
    :rtype: GroupResult

    """

    result = api.GroupResult()
    result.child_groups = set(fields['child_groups'])
    result.group_id = fields['id']
    result.size = fields['size']
    result.created_at = _date_time(json, fields['created_at'])
    result.modified_at = _date_time(json, fields['modified_at'])

    if 'name' in fields:
        result.name = fields['name']

    if 'auto_update' in fields:
        result.auto_update = _auto_update_from_fields(fields['auto_update'])

    return result

def group_result(response):
    """Parses a group response from the given JSON text.

    :param Response response: an XMS response
    :returns: the deserialized group response
    :rtype: GroupResult

    """

    json = response.text
    fields = response.json()
    return _group_result_from_fields(json, fields)

def groups_page(response):
    """Parses a page of groups from the given JSON text.

    :param Response response: an XMS response
    :returns: the created page of groups
    :rtype: Page

    """

    json, fields = _check_response(response)

    result = api.Page()
    result.page = fields['page']
    result.size = fields['page_size']
    result.total_size = fields['count']
    result.content = [
        _group_result_from_fields(json, s) for s in fields['groups']
    ]

    return result

def group_members(response):
    """Reads a JSON blob containing a set of group members.

    :param Response response: an XMS response
    :returns: a set of MSISDNs
    :rtype: set[str]

    """

    _, fields = _check_response(response)
    return set(fields)

def tags(response):
    """Reads a JSON blob containing a list of tags.

    :param Response response: an XMS response
    :returns: a set of tags
    :rtype: set[str]

    """

    _, fields = _check_response(response)
    return set(fields['tags'])

def _mo_sms_from_fields(json, fields):
    """Helper that reads an MO from the given fields.

    :param str json: original JSON formatted text
    :param dict fields: the JSON fields
    :return: the parsed inbound message
    :rtype: MoSms
    :raise UnexpectedResponseException: if the JSON contained an
        unexpected message type

    """

    if fields['type'] == 'mo_text':
        result = api.MoTextSms()
        result.body = fields['body']

        if 'keyword' in fields:
            result.keyword = fields['keyword']
    elif fields['type'] == 'mo_binary':
        result = api.MoBinarySms()
        result.udh = binascii.unhexlify(fields['udh'])
        result.body = binascii.a2b_base64(fields['body'])
    else:
        raise UnexpectedResponseException(
            'Received unexpected inbound type ' + fields['type'],
            json)

    result.message_id = fields['id']
    result.sender = fields['from']
    result.recipient = fields['to']

    if 'operator' in fields:
        result.operator = fields['operator']

    if 'sent_at' in fields:
        result.sent_at = _date_time(json, fields['sent_at'])

    if 'received_at' in fields:
        result.received_at = _date_time(json, fields['received_at'])

    return result

def mo_sms(response):
    """Reads an XMS response containing an MO message.

    :param Response response: an XMS response
    :returns: the MO message found in the response
    :rtype: MoSms
    :raises UnexpectedResponseException: if the JSON contained an
        unexpected message type

    """

    json, fields = _check_response(response)
    return _mo_sms_from_fields(json, fields)

def inbounds_page(response):
    """Reads a JSON blob describing a page of MO messages.

    :param Response response: an XMS response
    :returns: the parsed page
    :rtype: Page
    :raises UnexpectedResponseException: if the JSON contained an
        unexpected message type

    """

    json, fields = _check_response(response)

    result = api.Page()
    result.page = fields['page']
    result.size = fields['page_size']
    result.total_size = fields['count']
    result.content = [_mo_sms_from_fields(json, s) for s in fields['inbounds']]

    return result
