import pulumi
from Analytics import Analytics

analytics = Analytics("MyAnalytics")

pulumi.export("bucket_name", analytics.bucket_name)
pulumi.export("delivery_stream_name", analytics.delivery_stream_name)
pulumi.export("delivery_stream_arn", analytics.destination_stream_arn)
pulumi.export("pinpoint_application_name", analytics.pinpoint_application_name)
pulumi.export("pinpoint_application_id", analytics.pinpoint_application_id)
