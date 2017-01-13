# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes

"""The classes in this module represent objects sent and received from
the XMS REST API.

"""

from __future__ import absolute_import, division, print_function

class ReportType(object):
    """A collection of known delivery report types.

    These values are known to be valid in
    :py:attr:`MtSmsBatch.delivery_report`.

    """

    NONE = 'none'
    SUMMARY = 'summary'
    FULL = 'full'
    PER_RECIPIENT = 'per_recipient'


class DeliveryStatus(object):
    """A collection of known delivery statuses.

    Note, new statuses may be introduced to the XMS API.
    """

    QUEUED = "Queued"
    """Message is queued within REST API system and will be dispatched
    according to the rate of the account."""

    DISPATCHED = "Dispatched"
    """Message has been dispatched and accepted for delivery by the SMSC."""

    ABORTED = "Aborted"
    """Message was aborted before reaching SMSC."""

    REJECTED = "Rejected"
    """Message was rejected by SMSC."""

    DELIVERED = "Delivered"
    """Message has been delivered."""

    FAILED = "Failed"
    """Message failed to be delivered."""

    EXPIRED = "Expired"
    """Message expired before delivery."""

    UNKNOWN = "Unknown"
    """It is not known if message was delivered or not."""


class DeliveryReportType(object):
    """The types of delivery reports that can be retrieved."""

    SUMMARY = "summary"
    """Indicates a summary batch delivery report.

    The summary delivery report does not include the per-recipient
    result but rather aggregated statistics about the deliveries.

    """

    FULL = "full"
    """Indicates a full batch delivery report.

    This includes per-recipient delivery results. For batches with
    many destinations such reports may be very large.

    """


class Reset(object):
    """A class whose instances indicate that a value should be reset.

    This is used when updating previously created XMS objects. Note,
    it is typically not necessary to created new objects of this type,
    instead use the constant :const:`.RESET`.

    """

    def __init__(self):
        pass

RESET = Reset()
"""Object used to indicate that a XMS field should be reset to its
default value."""

class MtBatchSms(object):
    """Base class for all SMS batch classes.

    Holds fields that are common to both the create and response
    classes.

    .. attribute:: recipients

      One or more MSISDNs indicating the batch recipients.

      :type: set[str]

    .. attribute:: sender

      The batch sender, typically a short code or long number.

      :type: str

    .. attribute:: delivery_report

      The type of delivery report to use for this batch.

      :type: str

    .. attribute:: send_at

      The time at which this batch should be sent.

      :type: datetime

    .. attribute:: expire_at

      The time at which this batch should expire.

      :type: datetime

    .. attribute:: callback_url

      The URL to which callbacks should be sent.

      :type: str

    """

    def __init__(self):
        self.recipients = set()
        self.sender = None
        self.delivery_report = None
        self.send_at = None
        self.expire_at = None
        self.callback_url = None


class MtBatchSmsCreate(MtBatchSms):
    """Describes parameters available during batch creation.

    We can create two kinds of batches, textual and binary, described
    in the child classes :py:class:`MtBatchTextSmsCreate` and
    :py:class:`MtBatchTextSmsCreate`, respectively.

    .. attribute:: tags

      The initial set of tags to give the batch.

      :type: set[str]

    """

    def __init__(self):
        MtBatchSms.__init__(self)
        self.tags = set()


class MtBatchTextSmsCreate(MtBatchSmsCreate):
    """Class whose fields describe a text batch.

    .. attribute:: body

      The message body or template.

      :type: str

    .. attribute:: parameters

      The template parameters.

      This property is only relevant is the :py:attr:`body` property
      is a template. This is expected to be an associative array
      mapping parameter keys to associative arrays themselves mapping
      recipient numbers to substitution strings.

      More concretely we may have for the parameterized message
      "Hello, ${name}!" have::

        batch.parameters = {
            'name': {
                '123456789': 'Mary',
                '987654321': 'Joe',
                'default': 'valued customer'
            }
        }

      And the recipient with MSISDN "123456789" would then receive the
      message "Hello, Mary!".

      Note the use of "default" to indicate the substitution for
      recipients not explicitly given. For example, the recipient
      "555555555" would receive the message "Hello, valued customer!".

      :type: dict[str, dict[str, str]]

    """

    def __init__(self):
        MtBatchSmsCreate.__init__(self)
        self.body = None
        self.parameters = {}


class MtBatchBinarySmsCreate(MtBatchSmsCreate):
    """Describes a binary batch.

    This class holds all parameters that can be used when creating a
    binary SMS batch.

    .. attribute:: body

      The body of this binary message.

      :type: bytes

    .. attribute:: udh

      The User Data Header of this binary message.

      :type: bytes

    """

    def __init__(self):
        MtBatchSmsCreate.__init__(self)
        self.body = None
        self.udh = None


class MtBatchSmsUpdate(object):
    """Describes updates that can be performed on text and binary SMS
    batches.

    .. attribute:: recipient_insertions

      The message destinations to add to the batch. This should have
      zero or more MSISDNs.

      :type: set[str]

    .. attribute:: recipient_removals

      The message destinations to remove from the batch. This should
      have zero or more MSISDNs.

      :type: set[str]

    .. attribute:: sender

      The message originator as a long number or short code. If
      ``None`` then the current value is kept, if :const:`.RESET` then
      the value is reset to its XMS default, and if set to a string
      the sender is updated.

      :type: str or None or Reset

    .. attribute:: delivery_report

      Description of how to update the batch delivery report value. If
      ``None`` then the current value is kept, if :const:`.RESET` then
      the value is reset to its XMS default, and if set to a string
      the delivery report value is updated.

      See :class:`ReportType` for valid report types.

      :type: str or None or Reset

    .. attribute:: send_at

      Description of how to update the batch send at value. If
      ``None`` then the current value is kept, if :const:`.RESET` then
      the value is reset to its XMS default, and if set to a date time
      the send at value is updated.

      :type: datetime or None or Reset

    .. attribute:: expire_at

      Description of how to update the batch expire at value. If
      ``None`` then the current value is kept, if :const:`.RESET` then
      the value is reset to its XMS default, and if set to a date time
      the expire at value is updated.

      :type: datetime or None or Reset

    .. attribute:: callback_url

      Description of how to update the batch callback URL. If ``None``
      then the current value is kept, if :const:`.RESET` then the
      value is reset to its XMS default, and if set to a string the
      callback URL value is updated.

      :type: str or None or Reset

    """

    def __init__(self):
        self.recipient_insertions = set()
        self.recipient_removals = set()
        self.sender = None
        self.delivery_report = None
        self.send_at = None
        self.expire_at = None
        self.callback_url = None


class MtBatchTextSmsUpdate(MtBatchSmsUpdate):
    """Class that the update operations that can be performed on a text
    batch.

    .. attribute:: body

      The updated batch message body. If ``None`` then the current
      batch message is kept.

      :type: str or None

    .. attribute:: parameters

      Description of how to update the batch parameters. If ``None``
      then the current value is kept, if :const:`.RESET` then the
      value is reset to its XMS default, and if set to a dictionary
      the parameters value is updated.

      :type: dict or None or Reset

    """

    def __init__(self):
        MtBatchSmsUpdate.__init__(self)
        self.body = None
        self.parameters = None


class MtBatchBinarySmsUpdate(MtBatchSmsUpdate):
    """Describes updates to a binary SMS batch.

    .. attribute:: body

      The updated binary batch body. If ``None`` then the existing
      body is left as-is.

      :type: bytes or None

    .. attribute:: udh

      The updated binary User Data Header. If ``None`` then the
      existing UDH is left as-is.

      :type: bytes or None

    """

    def __init__(self):
        MtBatchSmsUpdate.__init__(self)
        self.body = None
        self.udh = None


class MtBatchSmsResult(MtBatchSms):
    """Contains the common fields of text and binary batches.

    .. attribute:: batch_id

      The unique batch identifier.

      :type: str

    .. attribute:: created_at

      Time when this batch was created.

      :type: datetime

    .. attribute:: modified_at

      Time when this batch was last modified.

      :type: datetime

    .. attribute:: canceled

      Whether this batch has been canceled.

      :type: bool

    """

    def __init__(self):
        MtBatchSms.__init__(self)
        self.batch_id = None
        self.created_at = None
        self.modified_at = None
        self.canceled = None


class MtBatchTextSmsResult(MtBatchSmsResult):
    """A textual batch as returned by the XMS endpoint.

    This differs from the batch creation definition by the addition
    of, for example, the batch identifier and the creation time.

    .. attribute:: body

      The message body or template. See
      :py:attr:`MtBatchTextSmsCreate.parameters`.

      :type: str

    .. attribute:: parameters

      The template parameters.

      type *dict[str, dict[str, str]]*

    """

    def __init__(self):
        MtBatchSmsResult.__init__(self)
        self.body = None
        self.parameters = None


class MtBatchBinarySmsResult(MtBatchSmsResult):
    """A binary SMS batch as returned by XMS.

    .. attribute:: body

      The body of this binary message.

      :type: bytes

    .. attribute:: udh

      The User Data Header of this binary message.

      :type: bytes

    """

    def __init__(self):
        MtBatchSmsResult.__init__(self)
        self.body = None
        self.udh = None


class BatchDeliveryReport(object):
    """Batch delivery report.

    A batch delivery report is divided into a number of *buckets* and
    each such bucket contain statistics about batch messages having a
    specific delivery status. The :py:attr:`statuses` property
    contains the various buckets.

    .. attribute:: batch_id

      Identifier of the batch that this report covers.

      :type: str

    .. attribute:: total_message_count

      The total number of messages sent as part of this batch.

      :type: int

    .. attribute:: statuses

      The batch status buckets. This array describes the aggregated
      status for the batch where each array element contains
      information about messages having a certain delivery status and
      delivery code.

      :type: list[BatchDeliveryReportStatus]

    """

    def __init__(self):
        self.batch_id = None
        self.total_message_count = None
        self.statuses = []


class BatchDeliveryReportStatus(object):
    """Aggregated statistics for a given batch.

    This represents the delivery statistics for a given statistics
    *bucket*. See :py:class:`BatchDeliveryReport`.

    .. attribute:: code

      The delivery status code for this recipient bucket.

      :type: int

    .. attribute:: status

      The delivery status for this recipient bucket.

      :type: str

    .. attribute:: count

      The number of recipients belonging to this bucket.

      :type: int

    .. attribute:: recipients

      The recipients having this status.

      Note, this is non-empty only if a `full` delivery report has been
      requested.

      :type: set[str]

    """

    def __init__(self):
        self.code = None
        self.status = None
        self.count = None
        self.recipients = set()


class BatchRecipientDeliveryReport(object):

    """A delivery report for an individual batch recipient.

    .. attribute:: batch_id

      The batch identifier.

      :type: string

    .. attribute:: recipient

      The recipient address.

      :type: string

    .. attribute:: code

      The delivery code.

      :type: int

    .. attribute:: status

      The delivery status.

      :type: int

    .. attribute:: status_message

      The delivery status message. The status message is not always
      available and the attribute is set to *None* in those cases.

      :type: string or None

    .. attribute:: operator

      The recipient's mobile operator. If the operator is not known,
      then this is set to *None*.

      :type: string or None

    .. attribute:: status_at

      The time at delivery.

      :type: datetime

    .. attribute:: operator_status_at

      The time of delivery as reported by operator.

      :type: datetime or None

    """

    def __init__(self):
        self.batch_id = None
        self.recipient = None
        self.code = None
        self.status = None
        self.status_message = None
        self.operator = None
        self.status_at = None
        self.operator_status_at = None

class Error(object):
    """Describes error responses given by XMS.

    :param str code: the error code
    :param str text: the human readable error text

    .. attribute:: code

      A code that can be used to programmatically recognize the error.

      :type: str

    .. attribute:: text

      Human readable description of the error.

      :type: str

    """

    def __init__(self, code, text):
        self.code = code
        self.text = text

class MtBatchDryRunResult(object):
    """A batch dry run report.

    .. attribute:: number_of_recipients

      The number of recipients that would receive the batch message.

      :type: int

    .. attribute:: number_of_message

      The number of messages that will be sent.

      :type: int

    .. attribute:: per_recipient

      The per-recipient dry-run result.

      :type: list[DryRunPerRecipient]

    """

    def __init__(self):
        self.number_of_recipients = None
        self.number_of_messages = None
        self.per_recipient = []

class DryRunPerRecipient(object):
    """Per-recipient dry-run result.

    Object of this class only occur within dry-run results. See
    :class:`MtBatchDryRunResult`.

    .. attribute:: recipient

      The recipient.

      :type: str

    .. attribute:: number_of_parts

      Number of message parts needed for the recipient.

      :type: int

    .. attribute:: body

      Message body sent to this recipient.

      :type: str

    .. attribute:: encoding

      Indicates the text encoding used for this recipient.

      This is one of "text" or "unicode". See :const:`ENCODING_TEXT`
      and :const:`ENCODING_UNICODE`.

      :type: str

    """

    ENCODING_TEXT = "text"
    """Constant indicating non-unicode encoding."""

    ENCODING_UNICODE = "unicode"
    """Constant indicating unicode encoding."""

    def __init__(self):
        self.recipient = None
        self.number_of_parts = None
        self.body = None
        self.encoding = None


class GroupAutoUpdate(object):
    """A description of automatic group updates.

    An automatic update is triggered by a mobile originated message to
    a given number containing special keywords.

    When the given recipient receives a mobile originated SMS
    containing keywords (first and/or second) matching the given
    ``add`` arguments then the sender MSISDN is added to the group.
    Similarly, if the MO is matching the given ``remove`` keyword
    arguments then the MSISDN is removed from the group.

    For example::

      GroupAutoUpdate(
        recipient='12345',
        add_first_word='add',
        remove_first_word='remove')

    would trigger based solely on the first keyword of the MO message.
    On the other hand::

      GroupAutoUpdate(
        recipient='12345',
        add_first_word='alert',
        add_second_word='add',
        remove_first_word='alert',
        remove_second_word='remove')

    would trigger only when both the first and second keyword are
    given in the MO message.

    :param str recipient: recipient that triggers this rule

    :param add_first_word: first ``add`` keyword, default is `None`.
    :type add_first_word: str or None

    :param add_second_word: second ``add`` keyword, default is `None`.
    :type add_second_word: str or None

    :param remove_first_word: first ``remove`` keyword, default is `None`.
    :type remove_first_word: str or None

    :param remove_second_word: second ``remove`` keywords, default is `None`.
    :type remove_second_word: str or None

    .. attribute:: recipient

      The recipient of the mobile originated message. A short code or
      long number.

      :type: str

    .. attribute:: add_word_pair

      A two-element tuple holding the first and second keyword that
      causes the MO sender to be added to the group.

      :type: tuple[str or None, str or None]

    .. attribute:: remove_word_pair

      A two-element tuple holding the first and second keyword that
      causes the MO sender to be removed from the group.

      :type: tuple[str or None, str or None]

    """

    def __init__(self,
                 recipient,
                 add_first_word=None,
                 add_second_word=None,
                 remove_first_word=None,
                 remove_second_word=None):
        self.recipient = recipient
        self.add_word_pair = (add_first_word, add_second_word)
        self.remove_word_pair = (remove_first_word, remove_second_word)


class GroupCreate(object):
    """A description of the fields necessary to create a group.

    .. attribute:: name

      The group name.

      :type: str

    .. attribute:: members

      A set of MSISDNs that belong to this group.

      :type: set[str]

    .. attribute:: child_groups

      A set of groups that in turn belong to this group.

      :type: set[str]

    .. attribute:: auto_update

      Describes how this group should be auto updated.

      If no auto updating should be performed for the group then this
      value is ``None``.

      :type: GroupAutoUpdate or None

    .. attribute:: tags

      The tags associated to this group.

      :type: set[str]

    """

    def __init__(self):
        self.name = None
        self.members = set()
        self.child_groups = set()
        self.auto_update = None
        self.tags = set()


class GroupResult(object):
    """This class holds the result of a group fetch operation.

    This may be used either standalone or as an element of a paged
    result.

    .. attribute:: group_id

      The unique group identifier.

      :type: str

    .. attribute:: name

      The group name.

      :type: str

    .. attribute:: size

      The number of members of this group.

      :type: int

    .. attribute:: child_groups

      A set of groups that in turn belong to this group.

      :type: set[str]

    .. attribute:: auto_update

      Describes how this group should be auto updated.

      If no auto updating should be performed for the group then this
      value is ``None``.

      :type: GroupAutoUpdate or None

    .. attribute:: created_at

      The time at which this group was created.

      :type: datetime

    .. attribute:: modified_at

      The time when this group was last modified.

      :type: datetime

    """

    def __init__(self):
        self.group_id = None
        self.name = None
        self.size = None
        self.child_groups = set()
        self.auto_update = None
        self.created_at = None
        self.modified_at = None


class GroupUpdate(object):
    """Describes updates that can be performed on a group.

    .. attribute:: name

      Updates the group name.

      If ``None`` then the current value is kept, if :const:`.RESET`
      then the value is reset to its XMS default, and if set to a
      string the name is updated.

      :type: None or str or Reset

    .. attribute:: member_insertions

      The MSISDNs that should be added to this group.

      :type: set[str]

    .. attribute:: member_removals

      The MSISDNs that should be removed from this group.

      :type: set[str]

    .. attribute:: child_group_insertions

      The child groups that should be added to this group.

      :type: set[str]

    .. attribute:: child_group_removals

      The child groups that should be removed from this group.

      :type: set[str]

    .. attribute:: add_from_group

      Identifier of a group whose members should be added to this
      group.

      :type: str

    .. attribute:: remove_from_group

      Identifier of a group whose members should be removed from this
      group.

      :type: str

    .. attribute:: auto_update

      Describes how this group should be auto updated.

      If ``None`` then the current value is kept, if :const:`.RESET`
      then the value is reset to its XMS default, and if set to a
      ``GroupAutoUpdate`` object the value is updated.

      :type: None or GroupAutoUpdate or Reset

    """

    def __init__(self):
        self.name = None
        self.member_insertions = set()
        self.member_removals = set()
        self.child_group_insertions = set()
        self.child_group_removals = set()
        self.add_from_group = None
        self.remove_from_group = None
        self.auto_update = None


class MoSms(object):
    """Base class for SMS mobile originated messages.

    Holds fields that are common to both the textual and binary MO
    classes.

    .. attribute:: message_id

      The message identifier.

      :type: str

    .. attribute:: recipient

      The message recipient. This is a short code or long number.

      :type: str

    .. attribute:: sender

      The message sender. This is an MSISDN.

      :type: str

    .. attribute:: operator

      The MCCMNC of the originating operator, if available.

      :type: str or None

    .. attribute:: sent_at

      The time when this message was sent, if available.

      :type: datetime or None

    .. attribute:: received_at

      The time when the messaging system received this message.

      :type: datetime

    """

    def __init__(self):
        self.message_id = None
        self.recipient = None
        self.sender = None
        self.operator = None
        self.sent_at = None
        self.received_at = None


class MoTextSms(MoSms):
    """An SMS mobile originated message with textual content.

    .. attribute:: body

      The message body.

      :type: str

    .. attribute:: keyword

      The message keyword, if available.

      :type: str or None

    """

    def __init__(self):
        MoSms.__init__(self)
        self.body = None
        self.keyword = None

class MoBinarySms(MoSms):
    """An SMS mobile originated message with binary content.

    .. attribute:: body

      The binary message body.

      :type: bytes

    .. attribute:: udh

      The user data header.

      :type: bytes

    """

    def __init__(self):
        MoSms.__init__(self)
        self.body = None
        self.udh = None


class Page(object):
    """A page of elements.

    The element type depends on the type of page that has been
    retrieved. Typically it is one of :class:`MtSmsBatchResponse` or
    :class:`GroupResponse`.

    .. attribute:: page

      The page number, starting from zero.

      :type: int

    .. attribute:: page

      The number of elements on this page.

      :type: int

    .. attribute:: total_size

      The total number of elements across all fetched pages.

      :type: int

    .. attribute:: content

      The page elements.

      :type: list[obj]

    """

    def __init__(self):
        self.page = None
        self.size = None
        self.total_size = None
        self.content = None

    def __iter__(self):
        """Returns an iterator over the content of this page.

        For example, if the page is the result of a batch listing then
        this iterator will yield batch results.

        :returns: the page iterator
        :rtype: iterator

        """

        return iter(self.content)


class Pages(object):
    """A paged result.

    It is possible to, for example, fetch individual pages or iterate
    over all pages.

    :param worker: worker function that fetches pages

    """

    def __init__(self, worker):
        self._worker = worker

    def get(self, page):
        """Downloads a specific page.

        :param int page: number of the page to fetch
        :return: a page
        :rtype: Page

        """

        return self._worker(page)

    def __iter__(self):
        """Iterator across all pages."""

        return PagesIterator(self)


class PagesIterator(object):
    """An iterator over a paged result.

    The key is the page number and the value corresponds to the
    content of the pages.

    :param Pages pages: the pages that we are iterating over

    """

    def __init__(self, pages):
        self._pages = pages
        self._cur_page = None
        self._position = 0

    def next(self):
        return self.__next__()

    def __next__(self):
        """Steps this iterator to the next page."""

        if not self._cur_page or self._cur_page.page != self._position:
            self._cur_page = self._pages.get(self._position)

        self._position += 1

        # If we fetched an empty page then the iteration is over.
        if self._cur_page.size <= 0:
            raise StopIteration
        else:
            return self._cur_page
