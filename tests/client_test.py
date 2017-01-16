# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
# pylint: disable=invalid-name

from datetime import date
from unittest import TestCase
from clx.xms import api, client, exceptions
from nose.tools import *
import requests_mock
from requests import ConnectionError
from requests.exceptions import MissingSchema

class DummyMtBatchCreate(api.MtBatchSmsCreate):
    """A little fake batch SMS create subclass."""

@raises(ConnectionError)
def test_unanswered_request():
    c = client.Client('foo', 'bar', "http://localhost:26541/xms")
    c.fetch_batch('BATCHID')

@raises(MissingSchema)
def test_invalid_url():
    c = client.Client('foo', 'bar', "/this is an invalid URL")
    c.fetch_batch('BATCHID')

def test_client_properties():
    c = client.Client('foo', 'bar', 'http://customurl/', 53.0)
    assert_equal('foo', c.service_plan_id)
    assert_equal('bar', c.token)
    assert_equal('http://customurl/', c.endpoint)
    assert_equal(53.0, c.timeout)

@requests_mock.Mocker()
class ClientTest(TestCase):
    BASE_URL = 'http://baz:1234/xms'

    def setUp(self):
        self._client = client.Client('foo', 'bar', self.BASE_URL)

    def tearDown(self):
        self._client = None

    def test_handles400_bad_request(self, m):
        m.get(
            self.BASE_URL + '/v1/foo/batches/batchid',
            status_code=400,
            json={'code': 'yes_this_is_code', 'text': 'the text'})

        try:
            self._client.fetch_batch('batchid')
            self.fail('expected exception')
        except exceptions.ErrorResponseException as ex:
            assert_equal('yes_this_is_code', ex.error_code)
            assert_equal('the text', str(ex))

    def test_handles403_forbidden(self, m):
        m.get(
            self.BASE_URL + '/v1/foo/batches/batchid',
            status_code=403,
            text='{"code":"yes_this_is_code","text":"the text"}')

        try:
            self._client.fetch_batch('batchid')
            self.fail('expected exception')
        except exceptions.ErrorResponseException as ex:
            assert_equal('yes_this_is_code', ex.error_code)
            assert_equal('the text', str(ex))

    def test_handles404_not_found(self, m):
        url = self.BASE_URL + '/v1/foo/batches/batchid'
        m.get(url, status_code=404, json={})

        try:
            self._client.fetch_batch('batchid')
            self.fail('expected exception')
        except exceptions.NotFoundException as ex:
            assert_equal('No resource found at "' + url +'"', str(ex))
            assert_equal(url, ex.url)

    def test_handles401_unauthorized(self, m):
        m.get(
            self.BASE_URL + '/v1/foo/batches/batchid',
            status_code=401,
            json={})

        try:
            self._client.fetch_batch('batchid')
            self.fail('expected exception')
        except exceptions.UnauthorizedException as ex:
            assert_equal('foo', ex.service_plan_id)
            assert_equal('bar', ex.token)

    def test_handles500_internal_server_error(self, m):
        m.get(
            self.BASE_URL + '/v1/foo/batches/batchid',
            status_code=500,
            json={})

        try:
            self._client.fetch_batch('batchid')
            self.fail('expected exception')
        except exceptions.UnexpectedResponseException as ex:
            assert_equal('{}', ex.http_body)

    def test_create_text_batch(self, m):
        response_body = """
        {
          "type" : "mt_text",
          "body" : "hello",
          "id" : "5Z8QsIRsk86f-jHB",
          "to" : [ "987654321", "123456789" ],
          "from" : "12345",
          "expire_at" : "2016-12-17T08:15:29.969Z",
          "created_at" : "2016-12-14T08:15:29.969Z",
          "modified_at" : "2016-12-14T08:15:29.969Z",
          "canceled" : false
        }
        """

        m.post(
            self.BASE_URL + '/v1/foo/batches',
            status_code=201,
            headers={'content-type': 'application/json'},
            text=response_body)

        batch = api.MtBatchTextSmsCreate()
        batch.body = 'hello'
        batch.recipients = ['987654321', '123456789']
        batch.sender = '12345'

        result = self._client.create_batch(batch)

        assert_is_instance(result, api.MtBatchTextSmsResult)
        assert_equal('5Z8QsIRsk86f-jHB', result.batch_id)

        expected_request_body = {
            'type': 'mt_text',
            'body': 'hello',
            'from': '12345',
            'to': ['987654321', '123456789']
        }

        assert_equal(expected_request_body, m.request_history[0].json())

    def test_create_binary_batch(self, m):
        response_body = {
            'type': 'mt_binary',
            'udh': 'fffefd',
            'body': 'AAECAw==',
            'id': '5Z8QsIRsk86f-jHB',
            'to': ['987654321', '123456789'],
            'from': '12345',
            'expire_at': '2016-12-17T08:15:29.969Z',
            'created_at': '2016-12-14T08:15:29.969Z',
            'modified_at': '2016-12-14T08:15:29.969Z',
            'canceled': False
        }

        m.post(
            self.BASE_URL + '/v1/foo/batches',
            status_code=201,
            headers={'content-type': 'application/json'},
            json=response_body)

        batch = api.MtBatchBinarySmsCreate()
        batch.body = b'\x00\x01\x02\x03'
        batch.udh = b'\xff\xfe\xfd'
        batch.recipients = ['987654321', '123456789']
        batch.sender = '12345'

        result = self._client.create_batch(batch)

        assert_is_instance(result, api.MtBatchBinarySmsResult)
        assert_equal('5Z8QsIRsk86f-jHB', result.batch_id)

        expected_request_body = {
            'type': 'mt_binary',
            'udh': 'fffefd',
            'body': 'AAECAw==\n',
            'to': ['987654321', '123456789'],
            'from': '12345'
        }

        assert_equal(expected_request_body, m.request_history[0].json())

    def test_dry_run_binary_batch(self, m):
        response_body = {
            'number_of_recipients': 2,
            'number_of_messages': 2
        }

        m.post(
            self.BASE_URL + '/v1/foo/batches/dry_run',
            status_code=201,
            headers={'content-type': 'application/json'},
            json=response_body)

        batch = api.MtBatchBinarySmsCreate()
        batch.body = b'\x00\x01\x02\x03'
        batch.udh = b'\xff\xfe\xfd'
        batch.recipients = ['987654321']
        batch.sender = '12345'

        result = self._client.create_batch_dry_run(batch)

        assert_equal(2, result.number_of_recipients)

        expected_request_body = {
            'type': 'mt_binary',
            'udh': 'fffefd',
            'body': 'AAECAw==\n',
            'to': ['987654321'],
            'from': '12345'
        }

        assert_equal(expected_request_body, m.request_history[0].json())

    def test_dry_run_text_batch(self, m):
        response_body = {
            'number_of_recipients': 2,
            'number_of_messages': 2,
            'per_recipient': [
                {
                    'recipient': '987654321',
                    'body': 'Hello',
                    'number_of_parts': 1,
                    'encoding': 'text'
                },
                {
                    'recipient':'555555555',
                    'body': 'Hello',
                    'number_of_parts': 1,
                    'encoding': 'text'
                }
            ]
        }

        m.post(
            self.BASE_URL + '/v1/foo/batches/dry_run' +
            '?per_recipient=true&' +
            'number_of_recipients=20',
            status_code=201,
            headers={'content-type': 'application/json'},
            json=response_body)

        batch = api.MtBatchTextSmsCreate()
        batch.body = 'Hello'
        batch.recipients = ['987654321', '555555555']
        batch.sender = '12345'

        result = self._client.create_batch_dry_run(batch, 20)

        assert_equal(2, result.number_of_recipients)

        expected_request_body = {
            'type': 'mt_text',
            'body': 'Hello',
            'to': ['987654321', '555555555'],
            'from': '12345'
        }

        assert_equal(expected_request_body, m.request_history[0].json())

    @raises(AttributeError)
    def test_dry_run_batch_wrong_type(self, _):
        self._client.create_batch_dry_run(DummyMtBatchCreate(), 20)

    def test_replace_text_batch(self, m):
        response_body = {
            "type": "mt_text",
            "body": "hello",
            "id": "5Z8QsIRsk86f-jHB",
            "to": ["987654321", "123456789"],
            "from": "12345",
            "expire_at": "2016-12-17T08:15:29.969Z",
            "created_at": "2016-12-14T08:15:29.969Z",
            "modified_at": "2016-12-14T08:15:29.969Z",
            "canceled": False
        }

        m.put(
            self.BASE_URL + '/v1/foo/batches/BatchID',
            status_code=201,
            headers={'content-type': 'application/json'},
            json=response_body)

        batch = api.MtBatchTextSmsCreate()
        batch.body = 'hello'
        batch.recipients = ['987654321', '123456789']
        batch.sender = '12345'

        result = self._client.replace_batch('BatchID', batch)

        assert_equal('5Z8QsIRsk86f-jHB', result.batch_id)

        expected_request_body = {
            "type": "mt_text",
            "body": "hello",
            "from": "12345",
            "to": ["987654321", "123456789"]
        }

        assert_equal(expected_request_body, m.request_history[0].json())

    def test_replace_binary_batch(self, m):
        response_body = {
            "type": "mt_binary",
            "udh": "fffefd",
            "body": "AAECAw==\n",
            "id": "5Z8QsIRsk86f-jHB",
            "to": ["987654321", "123456789"],
            "from": "12345",
            "expire_at": "2016-12-17T08:15:29.969Z",
            "created_at": "2016-12-14T08:15:29.969Z",
            "modified_at": "2016-12-14T08:15:29.969Z",
            "canceled": False
        }

        m.put(
            self.BASE_URL + '/v1/foo/batches/5Z8QsIRsk86f-jHB',
            status_code=201,
            headers={'content-type': 'application/json'},
            json=response_body)

        batch = api.MtBatchBinarySmsCreate()
        batch.body = b'\x00\x01\x02\x03'
        batch.udh = b'\xff\xfe\xfd'
        batch.recipients = ['987654321', '123456789']
        batch.sender = '12345'

        result = self._client.replace_batch('5Z8QsIRsk86f-jHB', batch)

        assert_equal('5Z8QsIRsk86f-jHB', result.batch_id)

        expected_request_body = {
            "type": "mt_binary",
            "udh": "fffefd",
            "body": "AAECAw==\n",
            "to": ["987654321", "123456789"],
            "from": "12345"
        }

        assert_equal(expected_request_body, m.request_history[0].json())

    def test_update_text_batch(self, m):
        response_body = {
            "body": "Hello, world!",
            "canceled": False,
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
        }

        m.post(
            self.BASE_URL + '/v1/foo/batches/4nQCc1T6Dg-R-zHX',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body)

        batch = api.MtBatchTextSmsUpdate()
        batch.send_at = api.RESET
        batch.body = 'hello'

        result = self._client.update_batch('4nQCc1T6Dg-R-zHX', batch)

        assert_equal('4nQCc1T6Dg-R-zHX', result.batch_id)

        expected_request_body = {
            "type": "mt_text",
            "body": "hello",
            "send_at": None
        }

        assert_equal(expected_request_body, m.request_history[0].json())

    def test_update_binary_batch(self, m):
        response_body = {
            "udh": "fffefd",
            "body": "AAECAw==\n",
            "canceled": False,
            "created_at": "2016-12-09T12:54:28.247Z",
            "delivery_report": "none",
            "expire_at": "2016-12-12T12:54:28.247Z",
            "from": "12345",
            "id": "4nQCc1T6Dg-R-zHY",
            "modified_at": "2016-12-09T12:54:28.247Z",
            "tags": [
                "rah"
            ],
            "to": [
                "987654321"
            ],
            "type": "mt_binary"
        }

        m.post(
            self.BASE_URL + '/v1/foo/batches/4nQCc1T6Dg-R-zHY',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body)

        batch = api.MtBatchBinarySmsUpdate()
        batch.callback_url = api.RESET
        batch.body = b'\x55\x44\x66'

        result = self._client.update_batch('4nQCc1T6Dg-R-zHY', batch)

        assert_equal('4nQCc1T6Dg-R-zHY', result.batch_id)

        expected_request_body = {
            "type": "mt_binary",
            "body": "VURm\n",
            "callback_url": None
        }

        assert_equal(expected_request_body, m.request_history[0].json())

    def test_fetch_text_batch(self, m):
        response_body = {
            "type": "mt_text",
            "body": "Hello, world!",
            "id": "!-@#$%^&*",
            "to": ["987654321", "123456789"],
            "from": "12345",
            "expire_at": "2016-12-17T08:15:29.969Z",
            "created_at": "2016-12-14T08:15:29.969Z",
            "modified_at": "2016-12-14T08:15:29.969Z",
            "canceled": False
        }

        m.get(
            self.BASE_URL + '/v1/foo/batches/%21-%40%23%24%25%5E%26%2A',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body)

        result = self._client.fetch_batch('!-@#$%^&*')

        assert_is_instance(result, api.MtBatchTextSmsResult)
        assert_equal('!-@#$%^&*', result.batch_id)

    @raises(ValueError)
    def test_fetch_batch_empty_id(self, _):
        self._client.fetch_batch('')

    def test_fetch_binary_batch(self, m):
        response_body = {
            "type": "mt_binary",
            "udh": "fffefd",
            "body": "AAECAw==\n",
            "id": "5Z8QsIRsk86f-jHB",
            "to": ["987654321", "123456789"],
            "from": "12345",
            "expire_at": "2016-12-17T08:15:29.969Z",
            "created_at": "2016-12-14T08:15:29.969Z",
            "modified_at": "2016-12-14T08:15:29.969Z",
            "canceled": False
        }

        m.get(
            self.BASE_URL + '/v1/foo/batches/5Z8QsIRsk86f-jHB',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body)

        result = self._client.fetch_batch('5Z8QsIRsk86f-jHB')

        assert_is_instance(result, api.MtBatchBinarySmsResult)
        assert_equal('5Z8QsIRsk86f-jHB', result.batch_id)

    def test_fetch_batches(self, m):
        response_body1 = {
            "batches": [
                {
                    "body": "AAECAw==\n",
                    "canceled": False,
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
                    "canceled": False,
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
                    "canceled": False,
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

        response_body2 = {
            "batches": [],
            "count": 7,
            "page": 1,
            "page_size": 0
        }

        m.get(
            self.BASE_URL +
            '/v1/foo/batches?page=0&page_size=10' +
            '&from=12345%2C98765&tags=tag1%2Ctag2' +
            '&start_date=2016-12-01&end_date=2016-12-02',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body1)

        m.get(
            self.BASE_URL +
            '/v1/foo/batches?page=1&page_size=10' +
            '&from=12345%2C98765&tags=tag1%2Ctag2' +
            '&start_date=2016-12-01&end_date=2016-12-02',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body2)

        pages = self._client.fetch_batches(
            page_size=10,
            senders=['12345', '98765'],
            tags=['tag1', 'tag2'],
            start_date=date(2016, 12, 1),
            end_date=date(2016, 12, 2))

        page = pages.get(0)
        assert_is_instance(page, api.Page)
        assert_equal(3, page.size)
        assert_equal(7, page.total_size)
        assert_equal('4G4OmwztSJbVL2bl', page.content[2].batch_id)

        page = pages.get(1)
        assert_is_instance(page, api.Page)
        assert_equal(0, page.size)
        assert_equal(7, page.total_size)
        assert_equal([], page.content)

    def test_cancel_batch(self, m):
        m.delete(
            self.BASE_URL + '/v1/foo/batches/BatchId',
            status_code=200)

        self._client.cancel_batch('BatchId')

        assert_true(m.called, 'No HTTP request performed')

    def test_fetch_batch_tags(self, m):
        m.get(
            self.BASE_URL + '/v1/foo/batches/BATCHID/tags',
            status_code=200,
            headers={'content-type': 'application/json'},
            json={"tags":["tag1", "tag2"]})

        tags = self._client.fetch_batch_tags('BATCHID')

        assert_equal({'tag1', 'tag2'}, tags)

    def test_replace_batch_tags(self, m):
        m.put(
            self.BASE_URL + '/v1/foo/batches/batchid/tags',
            status_code=200,
            headers={'content-type': 'application/json'},
            json={"tags": ["tag"]})

        tags = self._client.replace_batch_tags('batchid', ['tag'])

        assert_equal({'tag'}, tags)

    def test_fetch_delivery_report(self, m):
        response_body = {
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

        m.get(
            self.BASE_URL +
            '/v1/foo/batches/3SD49KIOW8lL1Z5E/delivery_report' +
            '?type=full' +
            '&status=Delivered%2CFailed' +
            '&code=0%2C11%2C400',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body)

        result = self._client.fetch_delivery_report(
            '3SD49KIOW8lL1Z5E',
            api.DeliveryReportType.FULL,
            ['Delivered', 'Failed'],
            [0, 11, 400]
        )

        assert_equal('3SD49KIOW8lL1Z5E', result.batch_id)

    def test_fetch_recipient_delivery_report(self, m):
        response_body = {
            "recipient": "123456789",
            "code": 11,
            "status": "Failed",
            "at": "2016-12-05T16:24:23.318Z",
            "type": "recipient_delivery_report_sms",
            "batch_id": "3-mbA7z9wDKY76ag",
            "operator_status_at": "2016-12-05T16:24:00.000Z"
        }

        m.get(
            self.BASE_URL +
            '/v1/foo/batches/3-mbA7z9wDKY76ag' +
            '/delivery_report/123456789',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body)

        result = self._client.fetch_recipient_delivery_report(
            '3-mbA7z9wDKY76ag', '123456789'
        )

        assert_equal('3-mbA7z9wDKY76ag', result.batch_id)

    def test_create_group(self, m):
        response_body = {
            "auto_update": {
                "to": "12345",
                "add": {
                    "first_word": "hello"
                },
                "remove": {
                    "first_word": "goodbye"
                }
            },
            "child_groups": [],
            "created_at": "2016-12-08T12:38:19.962Z",
            "id": "4cldmgEdAcBfcHW3",
            "modified_at": "2016-12-08T12:38:19.962Z",
            "name": "rah-test",
            "size": 1
        }

        group = api.GroupCreate()
        group.members = ['123456789', '987654321']
        group.name = 'my group'

        m.post(
            self.BASE_URL + '/v1/foo/groups',
            status_code=201,
            headers={'content-type': 'application/json'},
            json=response_body)

        result = self._client.create_group(group)

        assert_equal('4cldmgEdAcBfcHW3', result.group_id)

        expected_request_body = {
            "name": "my group",
            "members": ["123456789", "987654321"]
        }

        assert_equal(expected_request_body, m.request_history[0].json())

    def test_create_then_fetch_group(self, m):
        response_body1 = {
            "child_groups": [],
            "created_at": "2016-12-08T12:38:19.962Z",
            "id": "4cldmgEdAcBfcHW3",
            "modified_at": "2016-12-08T12:38:19.962Z",
            "name": "rah-test",
            "size": 1
        }

        response_body2 = {
            "child_groups": [],
            "created_at": "2016-12-08T12:38:19.962Z",
            "id": "helloworld",
            "modified_at": "2016-12-08T12:38:19.962Z",
            "name": "rah-test",
            "size": 1
        }

        group = api.GroupCreate()
        group.members = ['123456789', '987654321']

        m.post(
            self.BASE_URL + '/v1/foo/groups',
            status_code=201,
            headers={'content-type': 'application/json'},
            json=response_body1)

        m.get(
            self.BASE_URL + '/v1/foo/groups/helloworld',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body2)

        result = self._client.create_group(group)

        assert_equal('4cldmgEdAcBfcHW3', result.group_id)
        assert_in('Content-Type', m.request_history[0].headers)
        assert_equal(
            {"members":["123456789", "987654321"]},
            m.request_history[0].json())

        result = self._client.fetch_group('helloworld')
        assert_equal('helloworld', result.group_id)
        assert_not_in('Content-Type', m.request_history[1].headers)

    def test_create_then_delete_group(self, m):
        response_body1 = {
            "child_groups": [],
            "created_at": "2016-12-08T12:38:19.962Z",
            "id": "4cldmgEdAcBfcHW3",
            "modified_at": "2016-12-08T12:38:19.962Z",
            "name": "rah-test",
            "size": 1
        }

        group = api.GroupCreate()
        group.members = ['123456789', '987654321']

        m.post(
            self.BASE_URL + '/v1/foo/groups',
            status_code=201,
            headers={'content-type': 'application/json'},
            json=response_body1)

        m.delete(self.BASE_URL + '/v1/foo/groups/helloworld', status_code=200)

        result = self._client.create_group(group)
        assert_equal('4cldmgEdAcBfcHW3', result.group_id)
        assert_in('Content-Type', m.request_history[0].headers)
        assert_equal(
            {"members":["123456789", "987654321"]},
            m.request_history[0].json())

        self._client.delete_group('helloworld')
        assert_not_in('Content-Type', m.request_history[1].headers)

    def test_replace_group(self, m):
        response_body = {
            "child_groups": [],
            "created_at": "2016-12-08T12:38:19.962Z",
            "id": "4cldmgEdAcBfcHW3",
            "modified_at": "2016-12-10T12:38:19.162Z",
            "size": 1004
        }

        m.put(
            self.BASE_URL + '/v1/foo/groups/4cldmgEdAcBfcHW3',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body)

        group = api.GroupCreate()
        group.members = ['555555555']

        result = self._client.replace_group('4cldmgEdAcBfcHW3', group)

        assert_equal('4cldmgEdAcBfcHW3', result.group_id)
        assert_equal(1004, result.size)

    def test_update_group(self, m):
        response_body = {
            "child_groups": [],
            "created_at": "2016-12-08T12:38:19.962Z",
            "id": "4cldmgEdAcBfcHW3",
            "modified_at": "2016-12-10T12:38:19.162Z",
            "size": 1004
        }

        m.post(
            self.BASE_URL + '/v1/foo/groups/4cldmgEdAcBfcHW3',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body)

        group = api.GroupUpdate()

        result = self._client.update_group('4cldmgEdAcBfcHW3', group)

        assert_equal('4cldmgEdAcBfcHW3', result.group_id)
        assert_equal(1004, result.size)

    def test_delete_group(self, m):
        m.delete(
            self.BASE_URL + '/v1/foo/groups/GroupId',
            status_code=200)

        self._client.delete_group('GroupId')

        assert_true(m.called, 'No HTTP request performed')

    def test_fetch_group(self, m):
        response_body = {
            "auto_update": {
                "to": "12345",
                "add": {},
                "remove": {
                }
            },
            "child_groups": [],
            "created_at": "2016-12-08T12:38:19.962Z",
            "id": "4cldmgEdAcBfcHW3",
            "modified_at": "2016-12-10T12:38:19.162Z",
            "name": "rah-test",
            "size": 1
        }

        m.get(
            self.BASE_URL + '/v1/foo/groups/4cldmgEdAcBfcHW3',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body)

        group = self._client.fetch_group('4cldmgEdAcBfcHW3')

        assert_equal('4cldmgEdAcBfcHW3', group.group_id)

    @raises(ValueError)
    def test_fetch_group_empty_id(self, _):
        self._client.fetch_group('')

    def test_fetch_groups(self, m):
        response_body1 = {
            "count": 8,
            "page": 0,
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

        response_body2 = {
            "groups": [],
            "count": 8,
            "page": 1,
            "page_size": 0
        }

        m.get(
            self.BASE_URL +
            '/v1/foo/groups?page=0&page_size=10&tags=tag1%2Ctag2',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body1)

        m.get(
            self.BASE_URL +
            '/v1/foo/groups?page=1&page_size=10&tags=tag1%2Ctag2',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body2)

        pages = self._client.fetch_groups(page_size=10, tags=['tag1', 'tag2'])

        page = pages.get(0)
        assert_is_instance(page, api.Page)
        assert_equal(1, page.size)
        assert_equal(8, page.total_size)
        assert_equal('4cldmgEdAcBfcHW3', page.content[0].group_id)

        page = pages.get(1)
        assert_is_instance(page, api.Page)
        assert_equal(0, page.size)
        assert_equal(8, page.total_size)
        assert_equal([], page.content)

    def test_fetch_group_members(self, m):
        expected = ['123456789', '987654321', '555555555']

        m.get(
            self.BASE_URL + '/v1/foo/groups/123/members',
            headers={'content-type': 'application/json'},
            json=expected)

        actual = self._client.fetch_group_members('123')

        assert_equal(set(expected), actual)

    def test_fetch_group_tags(self, m):
        m.get(
            self.BASE_URL + '/v1/foo/groups/groupid/tags',
            status_code=200,
            headers={'content-type': 'application/json'},
            json={"tags":["tag1", "tag2"]})

        tags = self._client.fetch_group_tags('groupid')

        assert_equal({'tag1', 'tag2'}, tags)

    def test_replace_group_tags(self, m):
        m.put(
            self.BASE_URL + '/v1/foo/groups/GroupId/tags',
            status_code=200,
            headers={'content-type': 'application/json'},
            json={"tags": []})

        tags = self._client.replace_group_tags('GroupId', [])

        assert_equal(set(), tags)
        assert_equal({"tags":[]}, m.request_history[0].json())

    def test_update_batch_tags(self, m):
        m.post(
            self.BASE_URL + '/v1/foo/batches/batchid/tags',
            status_code=200,
            headers={'content-type': 'application/json'},
            json={"tags": ["tag"]})

        tags = self._client.update_batch_tags('batchid', ['at'], ['rt'])

        assert_equal({'tag'}, tags)

        assert_equal(
            {"add":["at"], "remove":["rt"]},
            m.request_history[0].json())

    def test_update_group_tags(self, m):
        m.post(
            self.BASE_URL + '/v1/foo/groups/GroupId/tags',
            status_code=200,
            headers={'content-type': 'application/json'},
            json={"tags": ["a", "b"]})

        tags = self._client.update_group_tags('GroupId', [], ['foo'])

        assert_equal({'a', 'b'}, tags)
        assert_equal(
            {"add": [], "remove": ["foo"]},
            m.request_history[0].json())

    def test_fetch_inbound(self, m):
        response_body = {
            "type": "mo_text",
            "to": "12345",
            "from": "987654321",
            "id": "10101010101",
            "sent_at": "2016-12-03T16:24:23.318Z",
            "received_at": "2016-12-05T16:24:23.318Z",
            "body": "Hello, world!",
            "keyword": "kivord",
            "operator": "31110"
        }

        m.get(
            self.BASE_URL + '/v1/foo/inbounds/10101010101',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body)

        mo = self._client.fetch_inbound('10101010101')

        assert_equal('987654321', mo.sender)

    @raises(ValueError)
    def test_fetch_inbound_empty_id(self, _):
        self._client.fetch_inbound('')

    def test_fetch_inbounds(self, m):
        response_body1 = {
            "count": 4,
            "page": 0,
            "inbounds": [
                {
                    "type": "mo_text",
                    "to": "12345",
                    "from": "987654321",
                    "id": "10101010101",
                    "received_at": "2016-12-05T16:24:23.318Z",
                    "body": "Hello, world!",
                    "keyword": "kivord",
                    "operator": "31110"
                }, {
                    "type": "mo_binary",
                    "to": "54321",
                    "from": "123456789",
                    "id": "20202020202",
                    "received_at": "2016-12-05T16:24:23.318Z",
                    "body": "AwE=",
                    "udh": "00010203"
                }, {
                    "type": "mo_text",
                    "to": "12345",
                    "from": "987654321",
                    "id": "30303030303",
                    "sent_at": "2016-12-03T16:24:23.318Z",
                    "received_at": "2016-12-05T16:24:23.318Z",
                    "body": "Hello, world!",
                    "keyword": "kivord",
                    "operator": "31110"
                }
            ],
            "page_size": 3
        }

        response_body2 = {
            "inbounds": [],
            "count": 4,
            "page": 1,
            "page_size": 0
        }

        m.get(
            self.BASE_URL +
            '/v1/foo/inbounds' +
            '?page=0&page_size=12&to=23456%2C8654' +
            '&start_date=2016-12-11&end_date=2016-12-12',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body1)

        m.get(
            self.BASE_URL +
            '/v1/foo/inbounds' +
            '?page=1&page_size=12&to=23456%2C8654' +
            '&start_date=2016-12-11&end_date=2016-12-12',
            status_code=200,
            headers={'content-type': 'application/json'},
            json=response_body2)

        pages = self._client.fetch_inbounds(
            page_size=12,
            recipients=['23456', '8654'],
            start_date=date(2016, 12, 11),
            end_date=date(2016, 12, 12))

        page = pages.get(0)
        assert_is_instance(page, api.Page)
        assert_equal(0, page.page)
        assert_equal(3, page.size)
        assert_equal(4, page.total_size)
        assert_equal('10101010101', page.content[0].message_id)
        assert_equal('20202020202', page.content[1].message_id)
        assert_equal('30303030303', page.content[2].message_id)

        page = pages.get(1)
        assert_is_instance(page, api.Page)
        assert_equal(1, page.page)
        assert_equal(0, page.size)
        assert_equal(4, page.total_size)
        assert_equal([], page.content)
