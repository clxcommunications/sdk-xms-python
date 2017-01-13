# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
# pylint: disable=invalid-name

from datetime import datetime
import json
from clx.xms import api, exceptions, deserialize
from nose.tools import *
from iso8601 import UTC

class MockResponse(object):
    def __init__(self, text):
        self.text = text

    def json(self):
        return json.loads(self.text)

@raises(exceptions.UnexpectedResponseException)
def test_read_invalid_json():
    class BadMockResponse(MockResponse):
        def __init__(self):
            MockResponse.__init__(self, '{this is invalid JSON}')

        def json(self):
            raise ValueError('Bad JSON')

    deserialize.batch_result(BadMockResponse())

def test_read_batch_response_text():
    response = MockResponse(
        """{
            "body": "${foo}${bar}",
            "canceled": true,
            "parameters": {
                "foo": {
                    "123456789": "Joe",
                    "987654321": "Mary",
                    "default": "you"
                },
                "bar": {}
            },
            "created_at": "2016-12-01T11:03:13.192Z",
            "delivery_report": "none",
            "send_at": "2016-12-02T11:03:13.192Z",
            "expire_at": "2016-12-05T11:03:13.192Z",
            "from": "12345",
            "id": "3SD49KIOW8lL1Z5E",
            "modified_at": "2016-12-01T11:03:13Z",
            "to": [
                "987654321",
                "555555555"
            ],
            "callback_url": "https://example.com/callbacker",
            "type": "mt_text"
        }""")

    result = deserialize.batch_result(response)

    assert_is_instance(result, api.MtBatchTextSmsResult)
    assert_equal('${foo}${bar}', result.body)
    assert_true(result.canceled)
    assert_equal(
        datetime(2016, 12, 1, 11, 3, 13, 192000, UTC), result.created_at
    )
    assert_equal('none', result.delivery_report)
    assert_equal(
        datetime(2016, 12, 2, 11, 3, 13, 192000, UTC), result.send_at
    )
    assert_equal(
        datetime(2016, 12, 5, 11, 3, 13, 192000, UTC), result.expire_at
    )
    assert_equal('12345', result.sender)
    assert_equal('3SD49KIOW8lL1Z5E', result.batch_id)
    assert_equal(
        datetime(2016, 12, 1, 11, 3, 13, 0, UTC), result.modified_at
    )
    assert_equal(
        'https://example.com/callbacker', result.callback_url
    )
    assert_equal(
        {'987654321', '555555555'}, result.recipients
    )
    assert_equal(
        {
            'foo': {
                'default': 'you',
                '987654321': 'Mary',
                '123456789': 'Joe'
            },
            'bar': {}
        },
        result.parameters
    )

@raises(exceptions.UnexpectedResponseException)
def test_read_batch_response_unknown():
    response = MockResponse(
        """{
            "some_field": "some_value",
            "type": "mt_what"
        }""")

    deserialize.batch_result(response)

def test_read_batches_page():
    response = MockResponse(
        """
        {
            "batches": [
                {
                    "body": "AAECAw==",
                    "canceled": false,
                    "created_at": "2016-12-14T08:15:29.969Z",
                    "delivery_report": "none",
                    "expire_at": "2016-12-17T08:15:29.969Z",
                    "from": "12345",
                    "id": "5Z8QsIRsk86f-jHB",
                    "modified_at": "2016-12-14T08:15:29.969Z",
                    "tags": [
                        "rah"
                    ],
                    "to": [
                        "987654321",
                        "123456789"
                    ],
                    "type": "mt_binary",
                    "udh": "fffefd"
                },
                {
                    "body": "Hello, world!",
                    "canceled": false,
                    "created_at": "2016-12-09T12:54:28.247Z",
                    "delivery_report": "none",
                    "expire_at": "2016-12-12T12:54:28.247Z",
                    "from": "12345",
                    "id": "4nQCc1T6Dg-R-zHX",
                    "modified_at": "2016-12-09T12:54:28.247Z",
                    "tags": [
                        "rah"
                    ],
                    "to": [
                        "987654321"
                    ],
                    "type": "mt_text"
                },
                {
                    "body": "Hello",
                    "canceled": false,
                    "created_at": "2016-12-06T11:14:37.438Z",
                    "delivery_report": "none",
                    "expire_at": "2016-12-09T11:14:37.438Z",
                    "from": "12345",
                    "id": "4G4OmwztSJbVL2bl",
                    "modified_at": "2016-12-06T11:14:37.438Z",
                    "tags": [
                        "rah1",
                        "rah2"
                    ],
                    "to": [
                        "987654321",
                        "555555555"
                    ],
                    "type": "mt_text"
                }
            ],
            "count": 7,
            "page": 0,
            "page_size": 3
        }
        """)

    result = deserialize.batches_page(response)

    assert_equal(3, result.size)
    assert_equal(0, result.page)
    assert_equal(7, result.total_size)
    assert_equal(3, len(result.content))

    assert_is_instance(result.content[0], api.MtBatchBinarySmsResult)
    assert_is_instance(result.content[1], api.MtBatchTextSmsResult)
    assert_is_instance(result.content[2], api.MtBatchTextSmsResult)

    assert_equal('5Z8QsIRsk86f-jHB', result.content[0].batch_id)
    assert_equal('4nQCc1T6Dg-R-zHX', result.content[1].batch_id)
    assert_equal('4G4OmwztSJbVL2bl', result.content[2].batch_id)

def test_read_delivery_report_summary():
    response = MockResponse(
        """
        {
            "batch_id": "3SD49KIOW8lL1Z5E",
            "statuses": [
                {
                    "code": 0,
                    "count": 2,
                    "status": "Delivered"
                },
                {
                    "code": 11,
                    "count": 1,
                    "status": "Failed"
                }
            ],
            "total_message_count": 2,
            "type": "delivery_report_sms"
        }
        """)

    result = deserialize.batch_delivery_report(response)

    assert_equal('3SD49KIOW8lL1Z5E', result.batch_id)
    assert_equal(2, result.total_message_count)
    assert_equal(2, len(result.statuses))

    assert_equal(0, result.statuses[0].code)
    assert_equal(11, result.statuses[1].code)

    assert_equal('Delivered', result.statuses[0].status)
    assert_equal('Failed', result.statuses[1].status)

    assert_equal(2, result.statuses[0].count)
    assert_equal(1, result.statuses[1].count)

    assert_equal(set(), result.statuses[0].recipients)
    assert_equal(set(), result.statuses[1].recipients)

def test_read_delivery_report_full():
    response = MockResponse(
        """{
          "type" : "delivery_report_sms",
          "batch_id" : "4G4OmwztSJbVL2bl",
          "total_message_count" : 2,
          "statuses" : [ {
            "code" : 0,
            "status" : "Delivered",
            "count" : 1,
            "recipients" : [ "555555555" ]
          }, {
            "code" : 11,
            "status" : "Failed",
            "count" : 1,
            "recipients" : [ "987654321" ]
          } ]
        }""")

    result = deserialize.batch_delivery_report(response)

    assert_equal('4G4OmwztSJbVL2bl', result.batch_id)
    assert_equal(2, result.total_message_count)
    assert_equal(2, len(result.statuses))

    assert_equal(0, result.statuses[0].code)
    assert_equal(11, result.statuses[1].code)

    assert_equal('Delivered', result.statuses[0].status)
    assert_equal('Failed', result.statuses[1].status)

    assert_equal(1, result.statuses[0].count)
    assert_equal(1, result.statuses[1].count)

    assert_equal({'555555555'}, result.statuses[0].recipients)
    assert_equal({'987654321'}, result.statuses[1].recipients)

@raises(exceptions.UnexpectedResponseException)
def test_read_delivery_report_unknown_type():
    response = MockResponse('{ "hello" : "value" }')
    deserialize.batch_delivery_report(response)

def test_read_recipient_delivery_report():
    response = MockResponse('{"recipient":"123456789","code":11,"status":"Failed","at":"2016-12-05T16:24:23.318Z","type":"recipient_delivery_report_sms","batch_id":"3-mbA7z9wDKY76ag","operator_status_at":"2016-12-05T16:24:00.000Z","status_message":"mystatusmessage","operator":"31101"}')

    result = deserialize.batch_recipient_delivery_report(response)

    assert_equal('3-mbA7z9wDKY76ag', result.batch_id)
    assert_equal(
        datetime(2016, 12, 5, 16, 24, 0, 0, UTC), result.operator_status_at
    )
    assert_equal(
        datetime(2016, 12, 5, 16, 24, 23, 318000, UTC), result.status_at
    )
    assert_equal(api.DeliveryStatus.FAILED, result.status)
    assert_equal(11, result.code)
    assert_equal('123456789', result.recipient)
    assert_equal('mystatusmessage', result.status_message)
    assert_equal('31101', result.operator)

@raises(exceptions.UnexpectedResponseException)
def test_read_recipient_delivery_report_unknown_type():
    response = MockResponse('{ "hello" : "value" }')
    deserialize.batch_recipient_delivery_report(response)

def test_read_group_result():
    response = MockResponse(
        """{
            "auto_update": {
                "to": "12345",
                "add": {
                    "first_word": "hello",
                    "second_word": "world"
                },
                "remove": {
                    "first_word": "goodbye",
                    "second_word": "world"
                }
            },
            "child_groups": [],
            "created_at": "2016-12-08T12:38:19.962Z",
            "id": "4cldmgEdAcBfcHW3",
            "modified_at": "2016-12-10T12:38:19.162Z",
            "name": "rah-test",
            "size": 1
        }""")

    result = deserialize.group_result(response)

    assert_equal('12345', result.auto_update.recipient)
    assert_equal(('hello', 'world'), result.auto_update.add_word_pair)
    assert_equal(('goodbye', 'world'), result.auto_update.remove_word_pair)
    assert_equal(0, len(result.child_groups))
    assert_equal(
        datetime(2016, 12, 8, 12, 38, 19, 962000, UTC), result.created_at
    )
    assert_equal('4cldmgEdAcBfcHW3', result.group_id)
    assert_equal(
        datetime(2016, 12, 10, 12, 38, 19, 162000, UTC), result.modified_at
    )
    assert_equal('rah-test', result.name)
    assert_equal(1, result.size)

def test_read_groups_page():
    response = MockResponse(
        """
        {
          "count": 8,
          "page": 2,
          "groups": [
            {
              "id": "4cldmgEdAcBfcHW3",
              "name": "rah-test",
              "size": 1,
              "created_at": "2016-12-08T12:38:19.962Z",
              "modified_at": "2016-12-08T12:38:19.962Z",
              "child_groups": [],
              "auto_update": {
                "to": "12345"
              }
            }
          ],
          "page_size": 1
        }
        """)

    result = deserialize.groups_page(response)

    assert_equal(1, result.size)
    assert_equal(2, result.page)
    assert_equal(8, result.total_size)
    assert_equal(1, len(result.content))
    assert_is_instance(result.content[0], api.GroupResult)
    assert_equal('4cldmgEdAcBfcHW3', result.content[0].group_id)

def test_read_group_members():
    response = MockResponse('["123456789", "987654321"]')

    result = deserialize.group_members(response)

    assert_equal({'123456789', '987654321'}, result)

def test_read_tags():
    response = MockResponse('{ "tags": ["tag1", "таг2"] }')

    result = deserialize.tags(response)

    assert_equal({'tag1', u'таг2'}, result)

def test_read_error():
    response = MockResponse(
        """
        {
            "code": "yes_this_is_code",
            "text": "This is a text"
        }
        """)

    result = deserialize.error(response)

    assert_equal('yes_this_is_code', result.code)
    assert_equal('This is a text', result.text)

def test_dry_run_with_per_recipients():
    response = MockResponse(
        """
        {"number_of_recipients":2,"number_of_messages":2,"per_recipient":[{"recipient":"987654321","body":"Hello","number_of_parts":1,"encoding":"text"},{"recipient":"555555555","body":"Hello","number_of_parts":1,"encoding":"text"}]}
        """)

    result = deserialize.batch_dry_run_result(response)

    assert_equal(2, result.number_of_recipients)
    assert_equal(2, result.number_of_messages)
    assert_equal('Hello', result.per_recipient[0].body)
    assert_equal(
        api.DryRunPerRecipient.ENCODING_TEXT, result.per_recipient[0].encoding
    )
    assert_equal('555555555', result.per_recipient[1].recipient)
    assert_equal(1, result.per_recipient[1].number_of_parts)

def test_dry_run_without_per_recipients():
    response = MockResponse('{"number_of_recipients":2,"number_of_messages":2}')

    result = deserialize.batch_dry_run_result(response)

    assert_equal(2, result.number_of_recipients)
    assert_equal(2, result.number_of_messages)

def test_mo_binary_sms():
    response = MockResponse(
        """
        {
          "type": "mo_binary",
          "to": "54321",
          "from": "123456789",
          "id": "b88b4cee-168f-4721-bbf9-cd748dd93b60",
          "sent_at": "2016-12-03T16:24:23.318Z",
          "received_at": "2016-12-05T16:24:23.318Z",
          "body": "AwE=",
          "udh": "00010203",
          "operator": "48271"
        }
        """)

    result = deserialize.mo_sms(response)

    assert_is_instance(result, api.MoBinarySms)
    assert_equal('54321', result.recipient)
    assert_equal('123456789', result.sender)
    assert_equal('b88b4cee-168f-4721-bbf9-cd748dd93b60', result.message_id)
    assert_equal(b'\x03\x01', result.body)
    assert_equal(b'\x00\x01\x02\x03', result.udh)
    assert_equal(
        datetime(2016, 12, 3, 16, 24, 23, 318000, UTC), result.sent_at
    )
    assert_equal(
        datetime(2016, 12, 5, 16, 24, 23, 318000, UTC), result.received_at
    )
    assert_equal('48271', result.operator)

def test_mo_text_sms():
    response = MockResponse(
        """
        {
          "type": "mo_text",
          "to": "12345",
          "from": "987654321",
          "id": "b88b4cee-168f-4721-bbf9-cd748dd93b60",
          "sent_at": "2016-12-03T16:24:23.318Z",
          "received_at": "2016-12-05T16:24:23.318Z",
          "body": "Hello, world!",
          "keyword": "kivord",
          "operator": "31110"
        }
        """)

    result = deserialize.mo_sms(response)

    assert_is_instance(result, api.MoTextSms)
    assert_equal('12345', result.recipient)
    assert_equal('987654321', result.sender)
    assert_equal(
        'b88b4cee-168f-4721-bbf9-cd748dd93b60', result.message_id
    )
    assert_equal('Hello, world!', result.body)
    assert_equal("kivord", result.keyword)
    assert_equal(
        datetime(2016, 12, 3, 16, 24, 23, 318000, UTC), result.sent_at
    )
    assert_equal(
        datetime(2016, 12, 5, 16, 24, 23, 318000, UTC), result.received_at
    )

def test_mo_text_sms_minimal():
    response = MockResponse(
        """
        {
          "type": "mo_text",
          "to": "12345",
          "from": "987654321",
          "id": "b88b4cee-168f-4721-bbf9-cd748dd93b60",
          "received_at": "2016-12-05T16:24:23.318Z",
          "body": "Hello, world!"
        }
        """)

    result = deserialize.mo_sms(response)

    assert_is_instance(result, api.MoTextSms)
    assert_equal('12345', result.recipient)
    assert_equal('987654321', result.sender)
    assert_equal(
        'b88b4cee-168f-4721-bbf9-cd748dd93b60', result.message_id
    )
    assert_equal('Hello, world!', result.body)
    assert_equal(
        datetime(2016, 12, 5, 16, 24, 23, 318000, UTC),
        result.received_at
    )

@raises(exceptions.UnexpectedResponseException)
def test_mo_text_sms_invalid_date_time():
    response = MockResponse(
        """
        {
          "type": "mo_text",
          "to": "12345",
          "from": "987654321",
          "id": "b88b4cee-168f-4721-bbf9-cd748dd93b60",
          "received_at": "2016-12-05T16:24:23318Z",
          "body": "Hello, world!"
        }
        """)

    deserialize.mo_sms(response)

@raises(exceptions.UnexpectedResponseException)
def test_mo_unknown_sms():
    response = MockResponse('{"type": "whatever"}')
    deserialize.mo_sms(response)

def test_read_inbounds_page():
    response = MockResponse(
        """
        {
          "count": 9,
          "page": 3,
          "inbounds": [
            {
              "type": "mo_text",
              "to": "12345",
              "from": "987654321",
              "id": "b88b4cee",
              "received_at": "2016-12-05T16:24:23.318Z",
              "body": "Hello, world!"
            },
            {
              "type": "mo_binary",
              "to": "54321",
              "from": "123456789",
              "id": "cd748dd93b60",
              "sent_at": "2016-12-03T16:24:23.318Z",
              "received_at": "2016-12-05T16:24:23.318Z",
              "body": "AwE=",
              "udh": "00010203"
            }
          ],
          "page_size": 2
        }
        """)

    result = deserialize.inbounds_page(response)

    assert_equal(2, result.size)
    assert_equal(3, result.page)
    assert_equal(9, result.total_size)
    assert_equal(2, len(result.content))
    assert_is_instance(result.content[0], api.MoTextSms)
    assert_equal('b88b4cee', result.content[0].message_id)
    assert_is_instance(result.content[1], api.MoBinarySms)
    assert_equal('cd748dd93b60', result.content[1].message_id)
