import json

import pulumi
from Analytics import Analytics
from identityPoolPolicy import (
    get_unauthenticated_role_policy_document,
    get_unauthenticated_role_trust_policy_document,
)
from pulumi.resource import ResourceOptions
from pulumi_aws import cognito, config, iam
from pulumi_aws.get_caller_identity import get_caller_identity

"""
This is an example Pulumi program which creates a Nuage Analytics pipeline component,
as well as a Cognito Identity Pool which allows anonymous authentication.  This
stack can be used to power the example website in the `example` folder.
"""

analytics = Analytics("MyAnalytics")

identity_pool = cognito.IdentityPool(
    "MyAnalyticsIdentityPool",
    allow_unauthenticated_identities=True,
    identity_pool_name="MyAnalyticsIdentityPool",
)

unauthenticated_role = iam.Role(
    "MyAnalyticsUnauthRole",
    assume_role_policy=get_unauthenticated_role_trust_policy_document(identity_pool.id),
)

unauthenticated_role_policy = iam.RolePolicy(
    f"MyAnalyticsUnauthRolePolicy",
    role=unauthenticated_role,
    policy=get_unauthenticated_role_policy_document(
        config.region,
        get_caller_identity().account_id,
        analytics.pinpoint_application_id,
    ).apply(json.dumps),
    opts=ResourceOptions(depends_on=[analytics, unauthenticated_role]),
)

cognito.IdentityPoolRoleAttachment(
    "MyAnalyticsIDPoolRoleAttach",
    identity_pool_id=identity_pool.id,
    roles={"unauthenticated": unauthenticated_role.arn},
)

pulumi.export("bucket_name", analytics.bucket_name)
pulumi.export("delivery_stream_name", analytics.delivery_stream_name)
pulumi.export("delivery_stream_arn", analytics.destination_stream_arn)
pulumi.export("pinpoint_application_name", analytics.pinpoint_application_name)
pulumi.export("pinpoint_application_id", analytics.pinpoint_application_id)
pulumi.export("identity_pool_id", identity_pool.id)
