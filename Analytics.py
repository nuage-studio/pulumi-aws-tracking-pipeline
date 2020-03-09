import json

import pulumi
from DelayResource import Delay
from firehosePolicy import (
    get_firehose_role_policy_document,
    get_firehose_role_trust_policy_document,
)
from pinpointPolicy import (
    get_pinpoint_stream_role_policy_document,
    get_pinpoint_stream_role_trust_policy_document,
)
from pulumi.output import Output
from pulumi.resource import ResourceOptions
from pulumi_aws import config, iam, kinesis, pinpoint, s3
from pulumi_aws.get_caller_identity import get_caller_identity


class Analytics(pulumi.ComponentResource):
    """
    The `nuage:aws:Analytics` creates Pinpoint application which pushes analytic events
    into an S3 bucket via a Kinesis Firehose.
    """

    bucket_name: Output[str]
    """
    The name of the S3 bucket into which analytics events will appear.
    """

    delivery_stream_name: Output[str]
    """
    The name of the Kinesis Firehose stream which streams events from Pinpoint to S3.
    """

    destination_stream_arn: Output[str]
    """
    The ARN of the Kinesis Firehose stream which streams events from Pinpoint to S3.
    """

    pinpoint_application_name: Output[str]
    """
    The Application name of the Pinpoint application for managing analytics.
    """

    pinpoint_application_id: Output[str]
    """
    The Application ID of the Pinpoint application for managing analytics.
    """

    def __init__(self, name, opts=None):
        super().__init__("nuage:aws:Analytics", name, None, opts)

        account_id = get_caller_identity().account_id
        region = config.region

        bucket = s3.Bucket(f"{name}Bucket")

        firehose_role = iam.Role(
            f"{name}FirehoseRole",
            assume_role_policy=get_firehose_role_trust_policy_document(account_id),
        )

        delivery_stream = kinesis.FirehoseDeliveryStream(
            f"{name}DeliveryStream",
            destination="extended_s3",
            extended_s3_configuration={
                "bucketArn": bucket.arn,
                "role_arn": firehose_role.arn,
                "compressionFormat": "GZIP",
            },
            opts=ResourceOptions(depends_on=[bucket, firehose_role]),
        )

        firehose_role_policy = iam.RolePolicy(
            f"{name}DeliveryStreamPolicy",
            role=firehose_role.name,
            policy=get_firehose_role_policy_document(
                region, account_id, bucket.arn, delivery_stream.name
            ).apply(json.dumps),
        )

        pinpoint_app = pinpoint.App(f"{name}PinpointApp")

        pinpoint_stream_role = iam.Role(
            f"{name}PinpointStreamRole",
            assume_role_policy=get_pinpoint_stream_role_trust_policy_document(),
        )

        pinpoint_stream_role_policy = iam.RolePolicy(
            f"{name}PinpointStreamPolicy",
            role=pinpoint_stream_role.name,
            policy=get_pinpoint_stream_role_policy_document(
                region, account_id, delivery_stream.name, pinpoint_app.application_id
            ).apply(json.dumps),
            opts=ResourceOptions(depends_on=[pinpoint_stream_role, delivery_stream]),
        )

        # IAM roles can take time to propogate so we have to add an artificial delay
        pinpoint_stream_role_delay = Delay(
            "EventStreamRoleDelay",
            10,
            opts=ResourceOptions(depends_on=[pinpoint_stream_role_policy]),
        )

        pinpoint_stream = pinpoint.EventStream(
            f"{name}PinpointEventStream",
            application_id=pinpoint_app.application_id,
            destination_stream_arn=delivery_stream.arn,
            role_arn=pinpoint_stream_role.arn,
            opts=ResourceOptions(
                depends_on=[delivery_stream, pinpoint_app, pinpoint_stream_role_delay,]
            ),
        )

        self.set_outputs(
            {
                "bucket_name": bucket.id,
                "delivery_stream_name": delivery_stream.name,
                "destination_stream_arn": delivery_stream.arn,
                "pinpoint_application_name": pinpoint_app.name,
                "pinpoint_application_id": pinpoint_app.application_id,
            }
        )

    def set_outputs(self, outputs: dict):
        """
        Adds the Pulumi outputs as attributes on the current object so they can be
        used as outputs by the caller, as well as registering them.
        """
        for output_name in outputs.keys():
            setattr(self, output_name, outputs[output_name])

        self.register_outputs(outputs)
