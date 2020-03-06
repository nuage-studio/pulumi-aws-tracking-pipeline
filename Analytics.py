import json

import pulumi
from firehosePolicy import (
    getFirehoseRolePolicyDocument,
    getFirehoseRoleTrustPolicyDocument,
)
from pulumi.output import Output
from pulumi.resource import ResourceOptions
from pulumi_aws import config, iam, kinesis, s3
from pulumi_aws.get_caller_identity import get_caller_identity


class Analytics(pulumi.ComponentResource):

    bucket_name: Output[str]
    """
    The name of the S3 bucket into which analytics events will appear.
    """

    delivery_stream_name: Output[str]
    """
    The name of the Kinesis Firehose stream which streams events from Pinpoint to S3.
    """

    def __init__(self, name, opts=None):
        super().__init__("nuage:aws:Analytics2", name, None, opts)

        accountId = get_caller_identity().account_id
        region = config.region

        bucket = s3.Bucket(f"{name}Bucket")

        firehoseRole = iam.Role(
            f"{name}FirehoseRole",
            assume_role_policy=getFirehoseRoleTrustPolicyDocument(accountId),
        )

        deliveryStream = kinesis.FirehoseDeliveryStream(
            f"{name}DeliveryStream",
            destination="extended_s3",
            extended_s3_configuration={
                "bucketArn": bucket.arn,
                "role_arn": firehoseRole.arn,
                "compressionFormat": "GZIP",
            },
            opts=ResourceOptions(depends_on=[bucket]),
        )

        firehoseRolePolicy = iam.RolePolicy(
            f"{name}DeliveryStreamPolicy",
            role=firehoseRole.name,
            policy=getFirehoseRolePolicyDocument(
                region, accountId, bucket.arn, deliveryStream.name
            ).apply(json.dumps),
        )

        self.set_outputs(
            {"bucket_name": bucket.id, "delivery_stream_name": deliveryStream.name}
        )

    def set_outputs(self, outputs: dict):
        """
        Adds the Pulumi outputs as attributes on the current object so they can be
        used as outputs by the caller, as well as registering them.
        """
        for output_name in outputs.keys():
            setattr(self, output_name, outputs[output_name])

        self.register_outputs(outputs)
