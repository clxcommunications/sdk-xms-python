# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes

"""Collection of value classes
"""

class ReportType(object):
    """A collection of known delivery report types.

    These values are known to be valid in
    :py:attr:`MtSmsBatch.delivery_report`.

    """

    NONE = 'none'
    SUMMARY = 'summary'
    FULL = 'full'
    PER_RECIPIENT = 'per_recipient'


class MtBatchSms(object):
    """Base class for all SMS batch classes.

    Holds fields that are common to both the create and response
    classes.

    .. attribute:: recipients

    type: *list(str)*

    One or more MSISDNs indicating the batch recipients.

    .. attribute:: sender

    type: *str*

    The batch sender, typically a short code or long number.

    .. attribute:: delivery_report

    type: *str*

    The type of delivery report to use for this batch.

    .. attribute:: send_at

    type: *datetime*

    The time at which this batch should be sent.

    .. attribute:: expire_at

    type: *datetime*

    The time at which this batch should expire.

    .. attribute:: callback_url

    type: *str*

    The URL to which callbacks should be sent.
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

    type: *list[str]*

    The initial set of tags to give the batch.
    """

    def __init__(self):
        MtBatchSms.__init__(self)
        self.tags = set()


class MtBatchTextSmsCreate(MtBatchSmsCreate):
    """Class whose fields describe a text batch.

    .. attribute:: body

    type: *str*

    The message body or template.

    .. attribute:: parameters

    type: *dict[str, dict[str, str]]*

    The template parameters.

    This property is only relevant is the :py:attr:`body` property is
    a template. This is expected to be an associative array mapping
    parameter keys to associative arrays themselves mapping recipient
    numbers to substitution strings.

    More concretely we may have for the parameterized message "Hello,
    ${name}!" have::

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

    type: *str*

    The body of this binary message.

    .. attribute:: udh

    type: *str*

    The User Data Header of this binary message.
    """

    def __init__(self):
        MtBatchSmsCreate.__init__(self)
        self.body = None
        self.udh = None


class MtBatchSmsResult(MtBatchSms):
    """Contains the common fields of text and binary batches.

    .. attribute:: batch_id

    type: *str*

    The unique batch identifier.

    .. attribute:: created_at

    type: *datetime*

    Time when this batch was created.

    .. attribute:: modified_at

    type: *datetime*

    Time when this batch was last modified.

    .. attribute:: canceled

    type: *bool*

    Whether this batch has been canceled.
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

    type: *str*

    The message body or template. See
    :py:attr:`MtBatchTextSmsCreate.parameters`.

    .. attribute:: parameters

    type *dict[str, dict[str, str]]*

    The template parameters.

    """

    def __init__(self):
        MtBatchSmsResult.__init__(self)
        self.body = None
        self.parameters = None


class MtBatchBinarySmsResult(MtBatchSmsResult):
    """A binary SMS batch as returned by XMS.

    .. attribute:: body

    type: *str*

    The body of this binary message.

    .. attribute:: udh

    type: *str*

    The User Data Header of this binary message.
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

    type: *str*

    Identifier of the batch that this report covers.

    .. attribute:: total_message_count

    type: *int*

    The total number of messages sent as part of this batch.

    .. attribute:: statuses

    type: *list[BatchDeliveryReportStatus]*

    The batch status buckets. This array describes the aggregated
    status for the batch where each array element contains information
    about messages having a certain delivery status and delivery code.

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

    type: *int*

    The delivery status code for this recipient bucket.

    .. attribute:: status

    type: *str*

    The delivery status for this recipient bucket.

    .. attribute:: count

    type: *int*

    The number of recipients belonging to this bucket.

    .. attribute:: recipients

    The recipients having this status.

    Note, this is non-empty only if a `full` delivery report has been
    requested.

    """

    def __init__(self):
        self.code = None
        self.status = None
        self.count = None
        self.recipients = None


class BatchRecipientDeliveryReport(object):

    """A delivery report for an individual batch recipient.

    .. attribute:: batch_id

    type: *string*

    The batch identifier.

    .. attribute:: recipient

    type: *string*

    The recipient address.

    .. attribute:: code

    type: *int*

    The delivery code.

    .. attribute:: status

    type: *int*

    The delivery status.

    .. attribute:: status_message

    type: *string* or *None*

    The delivery status message. The status message is not always
    available and the attribute is set to *None* in those cases.

    .. attribute:: operator

    type: *string* or *None*

    The recipient's mobile operator. If the operator is not known,
    then this is set to *None*.

    .. attribute:: status_at

    type: *datetime*

    The time at delivery.

    .. attribute:: operator_status_at

    type: *datetime* or *None*

    The time of delivery as reported by operator.
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
