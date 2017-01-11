# -*- coding: utf-8 -*-

"""JSON serializes for XMS API object classes.

Note, this module is mainly intended for internal use and the API may
change in the future

"""

import binascii
from clx.xms.api import RESET

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

def _batch_update_helper(batch):
    """Helper that prepares the given batch for serialization.

    :param batch: the batch to serialize
    :vartype batch: MtBatchSmsUpdate
    :return: dictionary suitable for JSON serialization
    :rtype: dict

    """

    fields = {}

    if batch.recipient_insertions:
        fields['to_add'] = batch.recipient_insertions

    if batch.recipient_removals:
        fields['to_remove'] = batch.recipient_removals

    if batch.sender:
        fields['from'] = batch.sender

    if batch.delivery_report == RESET:
        fields['delivery_report'] = None
    elif batch.delivery_report:
        fields['delivery_report'] = batch.delivery_report

    if batch.send_at == RESET:
        fields['send_at'] = None
    elif batch.send_at:
        fields['send_at'] = _write_datetime(batch.send_at)

    if batch.expire_at == RESET:
        fields['expire_at'] = None
    elif batch.expire_at:
        fields['expire_at'] = _write_datetime(batch.expire_at)

    if batch.callback_url == RESET:
        fields['callback_url'] = None
    elif batch.callback_url:
        fields['callback_url'] = batch.callback_url

    return fields

def text_batch_update(batch):
    """Serializes the given text batch update into JSON.

    :param batch: the batch update to serialize
    :vartype batch: MtBatchTextSmsUpdate
    :return: dictionary suitable for JSON serialization
    :rtype: dict

    """

    fields = _batch_update_helper(batch)

    fields['type'] = 'mt_text'

    if batch.body:
        fields['body'] = batch.body

    if batch.parameters == RESET:
        fields['parameters'] = None
    elif batch.parameters:
        fields['parameters'] = batch.parameters

    return fields

def binary_batch_update(batch):
    """Serializes the given binary batch update into JSON.

    :param batch: the batch update to serialize
    :vartype batch: MtBatchBinarySmsUpdate
    :return: dictionary suitable for JSON serialization
    :rtype: dict

    """

    fields = _batch_update_helper(batch)

    fields['type'] = 'mt_binary'

    if batch.body:
        fields['body'] = binascii.b2a_base64(batch.body)

    if batch.udh:
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
        fields.setdefault('add', {})['first_word'] = \
            auto_update.add_word_pair[0]

    if auto_update.add_word_pair[1]:
        fields.setdefault('add', {})['second_word'] = \
            auto_update.add_word_pair[1]

    if auto_update.remove_word_pair[0]:
        fields.setdefault('remove', {})['first_word'] = \
            auto_update.remove_word_pair[0]

    if auto_update.remove_word_pair[1]:
        fields.setdefault('remove', {})['second_word'] = \
            auto_update.remove_word_pair[1]

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

def group_update(obj):
    """Serializes the given group update object to JSON.

    :param obj: the group update to serialize
    :vartype obj: GroupUpdate
    :return: a dictionary suitable for JSON serialization
    :rtype: dict

    """

    fields = {}

    if obj.name == RESET:
        fields['name'] = None
    elif obj.name:
        fields['name'] = obj.name

    if obj.member_insertions:
        fields['add'] = obj.member_insertions

    if obj.member_removals:
        fields['remove'] = obj.member_removals

    if obj.child_group_insertions:
        fields['child_groups_add'] = obj.child_group_insertions

    if obj.child_group_removals:
        fields['child_groups_remove'] = obj.child_group_removals

    if obj.add_from_group:
        fields['add_from_group'] = obj.add_from_group

    if obj.remove_from_group:
        fields['remove_from_group'] = obj.remove_from_group

    if obj.auto_update == RESET:
        fields['auto_update'] = None
    elif obj.auto_update:
        fields['auto_update'] = _group_auto_update_helper(obj.auto_update)

    return fields

def tags(tag_coll):
    """Serializes the given tags to a JSON string.

    :param ts: a list of tags
    :vartype ts: list[string]
    :return: a dictionary suitable for JSON serialization
    :rtype: dict

    """

    return {'tags': tag_coll}

def tags_update(tags_to_add, tags_to_remove):
    """Serializes the given tag updates to a JSON string.

    :param tags_to_add: list of tags
    :vartype tags_to_add: list[str]
    :param tags_to_remove: list of tags
    :vartype tags_to_remove: list[str]
    :return: a dictionary suitable for JSON serialization
    :rtype: dict

    """

    return {'add': tags_to_add, 'remove': tags_to_remove}
