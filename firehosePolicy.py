import pulumi


def getFirehoseRoleTrustPolicyDocument(accountId):
    """Returns a trust (AssumeRole) policy allowing the firehose service for a given account"""

    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"Service": "firehose.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {"StringEquals": {"sts:ExternalId": f"{accountId}"}},
            }
        ],
    }


def applyFirehoseRolePolicyDocumentOutputs(bucketArn, deliveryStreamName, func):
    """ Applies the Pulumi outputs `bucketArn` and `deliveryStringName` to the
        given function.

        bucketArn -- The destination bucket ARN as a Pulumi Output
        deliveryStreamName -- The name of the Firehose delivery stream as a Pulumi Output
        func -- A lambda function with inputs (bucketArn: str, deliveryStringName: str)
    """
    return pulumi.Output.all(bucketArn, deliveryStreamName).apply(
        lambda outputs: func(outputs[0], outputs[1])
    )


def getFirehoseRolePolicyDocument(
    region, accountId, bucketArnOutput, deliveryStreamNameOutput
):
    """ Returns a role permitting Firehose to read Dynamo tables and write to S3

        region -- The AWS region as a string
        accountID -- The AWS account ID as a string
        bucketArnOutput -- The destination bucket ARN as a Pulumi Output
        deliveryStreamNameOutput -- The name of the Firehose delivery stream as a Pulumi Output
    """
    return applyFirehoseRolePolicyDocumentOutputs(
        bucketArnOutput,
        deliveryStreamNameOutput,
        lambda bucketArn, deliveryStreamName: {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Action": [
                        "glue:GetTable",
                        "glue:GetTableVersion",
                        "glue:GetTableVersions",
                    ],
                    "Resource": "*",
                },
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Action": [
                        "s3:AbortMultipartUpload",
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:PutObject",
                    ],
                    "Resource": [bucketArn, f"{bucketArn}/*"],
                },
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Action": ["logs:PutLogEvents"],
                    "Resource": [
                        f"arn:aws:logs:{region}:{accountId}:log-group:/aws/kinesisfirehose/{deliveryStreamName}:log-stream:*"
                    ],
                },
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Action": [
                        "kinesis:DescribeStream",
                        "kinesis:GetShardIterator",
                        "kinesis:GetRecords",
                    ],
                    "Resource": f"arn:aws:kinesis:{region}:{accountId}:stream/{deliveryStreamName}",
                },
            ],
        },
    )
