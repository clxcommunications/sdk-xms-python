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

      One or more MSISDNs indicating the batch recipients.

      type: *list(str)*

    .. attribute:: sender

      The batch sender, typically a short code or long number.

      type: *str*

    .. attribute:: delivery_report

      The type of delivery report to use for this batch.

      type: *str*

    .. attribute:: send_at

      The time at which this batch should be sent.

      type: *datetime*

    .. attribute:: expire_at

      The time at which this batch should expire.

      type: *datetime*

    .. attribute:: callback_url

      The URL to which callbacks should be sent.

      type: *str*

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

      type: *list[str]*

    """

    def __init__(self):
        MtBatchSms.__init__(self)
        self.tags = set()


class MtBatchTextSmsCreate(MtBatchSmsCreate):
    """Class whose fields describe a text batch.

    .. attribute:: body

      The message body or template.

      type: *str*

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

      type: *dict[str, dict[str, str]]*

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

      type: *str*

    .. attribute:: udh

      The User Data Header of this binary message.

      type: *str*

    """

    def __init__(self):
        MtBatchSmsCreate.__init__(self)
        self.body = None
        self.udh = None


class MtBatchSmsResult(MtBatchSms):
    """Contains the common fields of text and binary batches.

    .. attribute:: batch_id

      The unique batch identifier.

      type: *str*

    .. attribute:: created_at

      Time when this batch was created.

      type: *datetime*

    .. attribute:: modified_at

      Time when this batch was last modified.

      type: *datetime*

    .. attribute:: canceled

      Whether this batch has been canceled.

      type: *bool*

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

      type: *str*

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

      type: *str*

    .. attribute:: udh

      The User Data Header of this binary message.

      type: *str*

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

      type: *str*

    .. attribute:: total_message_count

      The total number of messages sent as part of this batch.

      type: *int*

    .. attribute:: statuses

      The batch status buckets. This array describes the aggregated
      status for the batch where each array element contains
      information about messages having a certain delivery status and
      delivery code.

      type: *list[BatchDeliveryReportStatus]*

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

      type: *int*

    .. attribute:: status

      The delivery status for this recipient bucket.

      type: *str*

    .. attribute:: count

      The number of recipients belonging to this bucket.

      type: *int*

    .. attribute:: recipients

      The recipients having this status.

      Note, this is non-empty only if a `full` delivery report has been
      requested.

      type: *list[str]*

    """

    def __init__(self):
        self.code = None
        self.status = None
        self.count = None
        self.recipients = None


class BatchRecipientDeliveryReport(object):

    """A delivery report for an individual batch recipient.

    .. attribute:: batch_id

      The batch identifier.

      type: *string*

    .. attribute:: recipient

      The recipient address.

      type: *string*

    .. attribute:: code

      The delivery code.

      type: *int*

    .. attribute:: status

      The delivery status.

      type: *int*

    .. attribute:: status_message

      The delivery status message. The status message is not always
      available and the attribute is set to *None* in those cases.

      type: *string* or *None*

    .. attribute:: operator

      The recipient's mobile operator. If the operator is not known,
      then this is set to *None*.

      type: *string* or *None*

    .. attribute:: status_at

      The time at delivery.

      type: *datetime*

    .. attribute:: operator_status_at

      The time of delivery as reported by operator.

      type: *datetime* or *None*

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

    :param code: the error code
    :vartype code: str
    :param text: the human readable error text
    :vartype text: str

    .. attribute:: code

      A code that can be used to programmatically recognize the error.

      type: *str*

    .. attribute: text

      Human readable description of the error.

      type: *str*

    """

    def __init__(self, code, text):
        self.code = code
        self.text = text
