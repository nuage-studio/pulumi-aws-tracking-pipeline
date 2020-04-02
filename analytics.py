import json
from typing import List, Tuple

import pulumi
from delay_resource import Delay
from firehose_policy import (
    get_firehose_role_policy_document,
    get_firehose_role_trust_policy_document,
)
from pinpoint_policy import (
    get_pinpoint_stream_role_policy_document,
    get_pinpoint_stream_role_trust_policy_document,
)
from pulumi.output import Output
from pulumi.resource import ResourceOptions
from pulumi_aws import config, iam, kinesis, pinpoint, s3
from pulumi_aws.get_caller_identity import get_caller_identity
from pulumi_google_tag_manager.dynamic_providers.gtm import (
    Container,
    ContainerArgs,
    CustomEventTrigger,
    CustomHtmlTag,
    CustomHtmlTagArgs,
    DataLayerVariable,
    Workspace,
    WorkspaceArgs,
)


class Analytics(pulumi.ComponentResource):
    """
    The `nuage:aws:Analytics` creates Pinpoint application which pushes analytic events
    into an S3 bucket via a Kinesis Firehose.  It can also optionally create a
    Google Tag Manager container with a custom tag for calling Amplify.
    The custom tag will record GTM events by calling a function named `Analytics` which
    MUST be present on the `window`.
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

    gtm_container_id: Output[str]
    """
    The ID of the Google Tag Manager container
    """

    gtm_tag: Output[str]
    """
    The Google Tag Manager tag which is placed in an HTML `<head>`
    """

    gtm_tag_no_script: Output[str]
    """
    The Google Tag Manager tag which is placed inside the HTML `<body>`
    """

    amplify_tag_id: Output[str]
    """
    The ID of the Custom HTML tag in GTM which passes analytics to Amplify
    """

    event_name: Output[str]
    """
    The name of the GTM event trigger which will cause the Amplify tag to fire
    """

    def __init__(
        self, name, should_create_gtm_tag=True, gtm_variables: List[str] = [], opts=None
    ):
        """
        :param should_create_gtm_tag: Whether or not a GTM environment should be created
                with a tag for calling Amplify.
        :param gtm_variables: A list of data layer variables to create in GTM.  These
                variables will also be passed into Amplify on each event.
        """
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

        outputs = {
            "bucket_name": bucket.id,
            "delivery_stream_name": delivery_stream.name,
            "destination_stream_arn": delivery_stream.arn,
            "pinpoint_application_name": pinpoint_app.name,
            "pinpoint_application_id": pinpoint_app.application_id,
            "gtm_container_id": None,
            "gtm_tag": None,
            "gtm_tag_no_script": None,
            "amplify_tag_id": None,
        }

        if should_create_gtm_tag:
            (gtm_container, _, event_trigger, amplify_tag) = self.create_gtm_tag(
                name, gtm_variables
            )

            outputs = {
                **outputs,
                "gtm_container_id": gtm_container.container_id,
                "gtm_tag": gtm_container.gtm_tag,
                "gtm_tag_no_script": gtm_container.gtm_tag_noscript,
                "amplify_tag_id": amplify_tag.tag_id,
                "event_name": event_trigger.trigger_name,
            }

        self.set_outputs(outputs)

    def set_outputs(self, outputs: dict):
        """
        Adds the Pulumi outputs as attributes on the current object so they can be
        used as outputs by the caller, as well as registering them.
        """
        for output_name in outputs.keys():
            setattr(self, output_name, outputs[output_name])

        self.register_outputs(outputs)

    def create_gtm_tag(self, name, gtm_variables=[]):

        gtm_account_id = pulumi.Config().require("gtm_account_id")

        container = Container(
            f"{name}Container",
            args=ContainerArgs(
                account_id=gtm_account_id, container_name=f"{name}Container",
            ),
        )
        workspace = Workspace(
            f"{name}Workspace",
            args=WorkspaceArgs(
                container_path=container.path, workspace_name=f"{name}Workspace"
            ),
        )

        for gtm_variable in gtm_variables:
            variable = DataLayerVariable(
                f"{name}_{gtm_variable}",
                variable_name=gtm_variable,
                workspace_path=workspace.path,
            )

        custom_event = CustomEventTrigger(
            f"{name}EventTrigger",
            trigger_name=f"{name}EventTrigger",
            workspace_path=workspace.path,
        )

        custom_tag = CustomHtmlTag(
            f"{name}AmplifyTag",
            args=CustomHtmlTagArgs(
                workspace_path=workspace.path,
                tag_name=f"{name}AmplifyTag",
                html=self.create_amplify_tag([(name, name) for name in gtm_variables]),
                firing_trigger_id=[custom_event.trigger_id],
            ),
        )

        return (container, workspace, custom_event, custom_tag)

    def create_amplify_tag(self, variables: List[Tuple[str, str]] = []):

        var_strings = [t[0] + ": {{" + t[1] + "}}," for t in variables]

        return (
            """
<script>
    window.Analytics.record({
        name: {{Event}},
        attributes: {
            hostname: {{Page Hostname}},
            page_path:{{Page Path}},
            page_url: {{Page URL}},
            referrer: {{Referrer}},
            """
            + "\n".join(var_strings)
            + """
        }
    }).catch(function(e) { console.error("Amplify Tag Error:" , e) })
</script>
"""
        )
