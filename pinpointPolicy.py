from pulumi.output import Output


def get_pinpoint_stream_role_trust_policy_document():
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "pinpoint.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }


def get_pinpoint_stream_role_policy_document(
    region: str, account_id: str, delivery_stream_name: Output[str]
):
    return delivery_stream_name.apply(
        lambda name: {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "firehose:PutRecordBatch",
                        "firehose:DescribeDeliveryStream",
                    ],
                    "Resource": [
                        f"arn:aws:firehose:{region}:{account_id}:deliverystream/{name}"
                    ],
                }
            ],
        }
    )
