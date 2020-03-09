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


def apply_pinpoint_stream_role_policy_document_outputs(
    delivery_stream_name, pinpoint_application_id, func
):
    """ Applies the Pulumi outputs `delivery_stream_name` and `pinpoint_application_id`
        to the given function.

        delivery_stream_name
        pinpoint_application_id
        func -- A lambda function with inputs (delivery_stream_name: str,
                pinpoint_application_id: str)
    """
    return Output.all(delivery_stream_name, pinpoint_application_id).apply(
        lambda outputs: func(outputs[0], outputs[1])
    )


def get_pinpoint_stream_role_policy_document(
    region: str,
    account_id: str,
    delivery_stream_name: Output[str],
    pinpoint_application_id: Output[str],
):

    return apply_pinpoint_stream_role_policy_document_outputs(
        delivery_stream_name,
        pinpoint_application_id,
        lambda name, appId: {
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
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "mobiletargeting:UpdateEndpoint",
                        "mobiletargeting:PutEvents",
                    ],
                    "Resource": [
                        f"arn:aws:mobiletargeting:*:{account_id}:apps/{appId}",
                        f"arn:aws:mobiletargeting:*:{account_id}:apps/{appId}/*",
                        f"arn:aws:mobiletargeting:*:{account_id}:apps/{appId}*",
                    ],
                },
                {
                    "Effect": "Allow",
                    "Action": ["mobileanalytics:PutEvents"],
                    "Resource": ["*"],
                },
            ],
        },
    )
