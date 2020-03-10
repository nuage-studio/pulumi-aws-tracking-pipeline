from pulumi.output import Output


def get_unauthenticated_role_trust_policy_document(identity_pool_id: Output[str]):
    return identity_pool_id.apply(
        lambda id: {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Federated": "cognito-identity.amazonaws.com"},
                    "Action": "sts:AssumeRoleWithWebIdentity",
                    "Condition": {
                        "StringEquals": {"cognito-identity.amazonaws.com:aud": id},
                        "ForAnyValue:StringLike": {
                            "cognito-identity.amazonaws.com:amr": "unauthenticated"
                        },
                    },
                }
            ],
        }
    )


def get_unauthenticated_role_policy_document(
    region: str, account_id: str, pinpoint_application_id: Output[str],
):
    return pinpoint_application_id.apply(
        lambda id: {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["mobiletargeting:PutEvents"],
                    "Resource": [
                        f"arn:aws:mobiletargeting:{region}:{account_id}:apps/{id}/*"
                    ],
                },
                {
                    "Effect": "Allow",
                    "Action": ["mobiletargeting:UpdateEndpoint"],
                    "Resource": [
                        f"arn:aws:mobiletargeting:{region}:{account_id}:apps/{id}/*"
                    ],
                },
                {
                    "Effect": "Allow",
                    "Action": ["mobileanalytics:PutEvents"],
                    "Resource": ["*"],
                },
            ],
        }
    )
