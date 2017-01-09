# -*- coding: utf-8 -*-

"""JSON serializes for XMS API object classes.

Note, this module is mainly intended for internal use and the API may
change in the future

"""

import binascii

def _write_datetime(value):
    """Helper that validates a date time object."""

    if value.utcoffset() is None:
        raise ValueError("expected datetime with time zone")

    return value.isoformat()

def _create_batch_helper(batch):
    """Helper that prepares the fields of a batch for JSON serialization.

    :param batch: the batch to serialize
    :vartype batch: MtBatchSmsCreate
    :return: dictionary for JSON serialization
    """

    fields = {
        'from': batch.sender,
        'to': batch.recipients
    }

    if batch.delivery_report:
        fields['delivery_report'] = batch.delivery_report

    if batch.send_at:
        fields['send_at'] = _write_datetime(batch.send_at)

    if batch.expire_at:
        fields['expire_at'] = _write_datetime(batch.expire_at)

    if batch.tags:
        fields['tags'] = batch.tags

    if batch.callback_url:
        fields['callback_url'] = batch.callback_url

    return fields

def text_batch(batch):
    """Serializes the given text batch into JSON.

    :param batch: the batch to serialize
    :vartype batch: MtBatchTextSmsCreate
    :return: dictionary suitable for JSON serialization
    """

    fields = _create_batch_helper(batch)

    fields['type'] = 'mt_text'
    fields['body'] = batch.body

    if batch.parameters:
        fields['parameters'] = batch.parameters

    return fields

def binary_batch(batch):
    """Serializes the given binary batch into JSON.

    :param batch: the batch to serialize
    :vartype batch: MtBatchBinarySmsCreate
    :return: dictionary suitable for JSON serialization
    """

    fields = _create_batch_helper(batch)

    fields['type'] = 'mt_binary'
    fields['body'] = binascii.b2a_base64(batch.body)
    fields['udh'] = binascii.hexlify(batch.udh)

    return fields

def _group_auto_update_helper(auto_update):
    """Helper that prepares the given group auto update for JSON
    serialization.

    :param auto_update: the auto update to serialize
    :vartype auto_update: GroupAutoUpdate
    :return: dictionary suitable for JSON serialization

    """

    fields = {
        'to': auto_update.recipient
    }

    if auto_update.add_word_pair[0]:
        fields['add']['first_word'] = auto_update.add_word_pair[0]

    if auto_update.add_word_pair[1]:
        fields['add']['second_word'] = auto_update.add_word_pair[1]

    if auto_update.remove_word_pair[0]:
        fields['remove']['first_word'] = auto_update.remove_word_pair[0]

    if auto_update.remove_word_pair[1]:
        fields['remove']['second_word'] = auto_update.remove_word_pair[1]

    return fields

def group_create(group):
    """Serializes the given group create object to JSON.

    :param group: the group to serialize
    :vartype group: GroupCreate
    :return: dictionary suitable for JSON serialization

    """

    fields = {}

    if group.name:
        fields['name'] = group.name

    if group.members:
        fields['members'] = group.members

    if group.child_groups:
        fields['child_groups'] = group.child_groups

    if group.auto_update:
        fields['auto_update'] = _group_auto_update_helper(group.auto_update)

    if group.tags:
        fields['tags'] = group.tags

    return fields