# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
# pylint: disable=invalid-name

from datetime import datetime
from clx.xms import api, exceptions, serialize
from nose.tools import *
from iso8601 import UTC

def test_date_without_timezone():
    batch = api.MtBatchTextSmsCreate()
    batch.sender = '12345'
    batch.recipients = ['123456789']
    batch.body = 'hello'
    batch.send_at = datetime(2016, 12, 1, 11, 3, 13, 192000)

    try:
        serialize.text_batch(batch)
    except ValueError as ex:
        assert_equal('Expected datetime with time zone', str(ex))

def test_batch_create_text():
    batch = api.MtBatchTextSmsCreate()
    batch.sender = '12345'
    batch.recipients = ['987654321', '123456789']
    batch.body = 'Hello, ${name}!'
    batch.parameters['name'] = {
        '987654321': 'Mary',
        '123456789': 'Joe',
        'default': 'you'
    }
    batch.delivery_report = api.ReportType.NONE
    batch.send_at = datetime(2016, 12, 1, 11, 3, 13, 192000, UTC)
    batch.expire_at = datetime(2016, 12, 4, 11, 3, 13, 192000, UTC)
    batch.callback_url = 'http://localhost/callback'

    actual = serialize.text_batch(batch)

    expected = {
        'body': 'Hello, ${name}!',
        'delivery_report': 'none',
        'send_at': '2016-12-01T11:03:13.192000+00:00',
        'expire_at': '2016-12-04T11:03:13.192000+00:00',
        'from': '12345',
        'to': [
            '987654321',
            '123456789'
        ],
        'parameters': {
            'name': {
                '987654321': 'Mary',
                '123456789': 'Joe',
                'default': 'you'
            }
        },
        'callback_url': 'http://localhost/callback',
        'type': 'mt_text'
    }

    assert_equal(expected, actual)

def test_batch_create_binary():
    batch = api.MtBatchBinarySmsCreate()
    batch.sender = '12345'
    batch.recipients = ['987654321', '123456789']
    batch.body = b'\x00\x01\x02\x03'
    batch.udh = b'\xff\xfe\xfd'
    batch.delivery_report = api.ReportType.SUMMARY
    batch.expire_at = datetime(2016, 12, 17, 8, 15, 29, 969000, UTC)
    batch.tags = ['tag1', 'таг2']

    actual = serialize.binary_batch(batch)

    expected = {
        'body': 'AAECAw==\n',
        'delivery_report': 'summary',
        'expire_at': '2016-12-17T08:15:29.969000+00:00',
        'from': '12345',
        'tags': ['tag1', 'таг2'],
        'to': [
            '987654321',
            '123456789'
        ],
        'type': 'mt_binary',
        'udh': 'fffefd'
    }

    assert_equal(expected, actual)

def test_batch_update_text_set_all():
    batch = api.MtBatchTextSmsUpdate()
    batch.sender = '12345'
    batch.recipient_insertions = ['987654321', '123456789']
    batch.recipient_removals = ['555555555']
    batch.body = 'Hello, ${name}!'
    batch.parameters = {
        'name': {
            '987654321': 'Mary',
            '123456789': 'Joe',
            'default': 'you'
        }
    }
    batch.delivery_report = api.ReportType.NONE
    batch.send_at = datetime(2016, 12, 1, 11, 3, 13, 192000, UTC)
    batch.expire_at = datetime(2016, 12, 4, 11, 3, 13, 192000, UTC)
    batch.callback_url = 'http://localhost/callback'

    actual = serialize.text_batch_update(batch)

    expected = {
        'type': 'mt_text',
        'body': 'Hello, ${name}!',
        'delivery_report': 'none',
        'send_at': '2016-12-01T11:03:13.192000+00:00',
        'expire_at': '2016-12-04T11:03:13.192000+00:00',
        'from': '12345',
        'to_add': [
            '987654321',
            '123456789'
        ],
        'to_remove': [
            '555555555'
        ],
        'parameters': {
            'name': {
                '987654321': 'Mary',
                '123456789': 'Joe',
                'default': 'you'
            }
        },
        'callback_url': 'http://localhost/callback'
    }

    assert_equal(expected, actual)

def test_batch_update_text_minimal():
    batch = api.MtBatchTextSmsUpdate()

    actual = serialize.text_batch_update(batch)
    expected = {'type': 'mt_text'}

    assert_equal(expected, actual)

def test_batch_update_text_resets():
    batch = api.MtBatchTextSmsUpdate()
    batch.delivery_report = api.RESET
    batch.send_at = api.RESET
    batch.expire_at = api.RESET
    batch.callback_url = api.RESET
    batch.parameters = api.RESET

    actual = serialize.text_batch_update(batch)

    expected = {
        'type': 'mt_text',
        'delivery_report': None,
        'send_at': None,
        'expire_at': None,
        'callback_url': None,
        'parameters': None
    }

    assert_equal(expected, actual)

def test_batch_update_binary_set_all():
    batch = api.MtBatchBinarySmsUpdate()
    batch.sender = '12345'
    batch.recipient_insertions = ['987654321', '123456789']
    batch.recipient_removals = ['555555555']
    batch.body = b'\x00\x01\x02\x03'
    batch.udh = b'\xff\xfe\xfd'
    batch.delivery_report = api.ReportType.PER_RECIPIENT
    batch.send_at = datetime(2016, 12, 1, 11, 3, 13, 192000, UTC)
    batch.expire_at = datetime(2016, 12, 4, 11, 3, 13, 192000, UTC)
    batch.callback_url = 'http://localhost/callback'

    actual = serialize.binary_batch_update(batch)

    expected = {
        'type': 'mt_binary',
        'body': 'AAECAw==\n',
        'udh': 'fffefd',
        'delivery_report': 'per_recipient',
        'send_at': '2016-12-01T11:03:13.192000+00:00',
        'expire_at': '2016-12-04T11:03:13.192000+00:00',
        'from': '12345',
        'to_add': [
            '987654321',
            '123456789'
        ],
        'to_remove': [
            '555555555'
        ],
        'callback_url': 'http://localhost/callback'
    }

    assert_equal(expected, actual)

def test_batch_update_binary_minimal():
    batch = api.MtBatchBinarySmsUpdate()

    actual = serialize.binary_batch_update(batch)
    expected = {'type': 'mt_binary'}

    assert_equal(expected, actual)

def test_batch_update_binary_resets():
    batch = api.MtBatchBinarySmsUpdate()
    batch.delivery_report = api.RESET
    batch.send_at = api.RESET
    batch.expire_at = api.RESET
    batch.callback_url = api.RESET

    actual = serialize.binary_batch_update(batch)

    expected = {
        'type': 'mt_binary',
        'delivery_report': None,
        'send_at': None,
        'expire_at': None,
        'callback_url': None
    }

    assert_equal(expected, actual)

def test_group_create():
    group = api.GroupCreate()
    group.name = 'test name'
    group.members = ['123456789', '987654321']
    group.child_groups = ['group1', 'group2']
    group.auto_update = api.GroupAutoUpdate(
        recipient='12345',
        add_first_word='ADD',
        add_second_word='plz',
        remove_first_word='REMOVE',
        remove_second_word='ME')
    group.tags = ['tag1', 'tag2']

    actual = serialize.group_create(group)

    expected = {
        'auto_update': {
            'to': '12345',
            'add': {
                'first_word': 'ADD',
                'second_word': 'plz'
            },
            'remove': {
                'first_word': 'REMOVE',
                'second_word': 'ME'
            }
        },
        'members': ['123456789', '987654321'],
        'child_groups': ['group1', 'group2'],
        'name': 'test name',
        'tags': ['tag1', 'tag2']
    }

    assert_equal(expected, actual)

def test_group_update_everything():
    group_update = api.GroupUpdate()
    group_update.name = 'new name'
    group_update.member_insertions = ['123456789']
    group_update.member_removals = ['987654321', '4242424242']
    group_update.child_group_insertions = ['groupId1', 'groupId2']
    group_update.child_group_removals = ['groupId3']
    group_update.add_from_group = 'group1'
    group_update.remove_from_group = 'group2'
    group_update.auto_update = api.GroupAutoUpdate(
        recipient='1111',
        add_first_word='kw0',
        add_second_word='kw1',
        remove_first_word='kw2',
        remove_second_word='kw3')

    actual = serialize.group_update(group_update)

    expected = {
        'name': 'new name',
        'add': ['123456789'],
        'remove': ['987654321', '4242424242'],
        'child_groups_add': ['groupId1', 'groupId2'],
        'child_groups_remove': ['groupId3'],
        'add_from_group': 'group1',
        'remove_from_group': 'group2',
        'auto_update': {
            'to': '1111',
            'add': {'first_word': 'kw0', 'second_word': 'kw1'},
            'remove': {'first_word': 'kw2', 'second_word': 'kw3'}
        }
    }

    assert_equal(expected, actual)

def test_group_update_minimal():
    group_update = api.GroupUpdate()

    actual = serialize.group_update(group_update)
    expected = {}

    assert_equal(expected, actual)

def test_group_update_resets():
    group_update = api.GroupUpdate()
    group_update.name = api.RESET
    group_update.auto_update = api.RESET

    actual = serialize.group_update(group_update)

    expected = {
        'name': None,
        'auto_update': None
    }

    assert_equal(expected, actual)

def test_tags():
    actual = serialize.tags(['tag1', 'tag2'])
    expected = {'tags': ['tag1', 'tag2']}

    assert_equal(expected, actual)

def test_tags_update():
    actual = serialize.tags_update(['tag_1', 'tag_2'], ['tag'])
    expected = {'add': ['tag_1', 'tag_2'], 'remove': ['tag']}

    assert_equal(expected, actual)
