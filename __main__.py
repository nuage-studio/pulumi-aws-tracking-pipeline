import pulumi
from Analytics import Analytics

analytics = Analytics("MyAnalytics")

pulumi.export("bucket_name", analytics.bucket_name)
