from typing import List, Tuple

import pulumi
from pulumi.output import Output
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

EVENT_VARIABLE_NAME = "analytics_event"
DATA_VARIABLE_NAME = "analytics_data"


class GtmAnalytics(pulumi.ComponentResource):
    """
    The Google Tag Manager subcomponent of `nuage:aws:Analytics`.  This component
    creates a GTM container and workspace, as well as tags which report analytics to
    both Google Analytics and AWS Amplify.

    Note that the Amplify tag will record GTM events by calling a function named
    `Analytics` which MUST be present on the `window`.
    """

    container_id: Output[str]
    """
    The ID of the Google Tag Manager container
    """

    tag: Output[str]
    """
    The Google Tag Manager tag which is placed in an HTML `<head>`
    """

    tag_no_script: Output[str]
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

    event_variable_id: Output[str]
    """
    The ID of the data layer variable for passing analytic event names
    """

    data_variable_id: Output[str]
    """
    The ID of the data layer variable for passing analytic event data
    """

    def __init__(self, name, opts=None):
        """
        :param gtm_variables: A list of data layer variables to create in GTM.  A GA
                event tag will be created for each of these variables, and the variables
                will also be passed into Amplify on each event.
        """
        super().__init__("nuage:aws:GtmAnalytics", name, None, opts)

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

        event_variable = DataLayerVariable(
            f"{name}EventVariable",
            variable_name=EVENT_VARIABLE_NAME,
            workspace_path=workspace.path,
        )

        data_variable = DataLayerVariable(
            f"{name}DataVariable",
            variable_name=DATA_VARIABLE_NAME,
            workspace_path=workspace.path,
        )

        event_trigger = CustomEventTrigger(
            f"{name}EventTrigger",
            trigger_name=f"{name}EventTrigger",
            workspace_path=workspace.path,
        )

        amplify_tag = CustomHtmlTag(
            f"{name}AmplifyTag",
            args=CustomHtmlTagArgs(
                workspace_path=workspace.path,
                tag_name=f"{name}AmplifyTag",
                html=self.create_amplify_tag(),
                firing_trigger_id=[event_trigger.trigger_id],
            ),
        )

        outputs = {
            "container_id": container.container_id,
            "tag": container.gtm_tag,
            "tag_no_script": container.gtm_tag_noscript,
            "amplify_tag_id": amplify_tag.tag_id,
            "event_name": event_trigger.trigger_name,
            "event_variable_id": event_variable.variable_id,
            "data_variable_id": data_variable.variable_id,
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

    def create_amplify_tag(self, variables: List[Tuple[str, str]] = []):
        return (
            """
<script>
    window.Analytics.record({
        name: {{"""
            + EVENT_VARIABLE_NAME
            + """}},
        attributes: {
            hostname: {{Page Hostname}},
            page_path:{{Page Path}},
            page_url: {{Page URL}},
            referrer: {{Referrer}},
            """
            + DATA_VARIABLE_NAME
            + ": {{"
            + DATA_VARIABLE_NAME
            + """}},
        }
    }).catch(function(e) { console.error("Amplify Tag Error:" , e) })
</script>
"""
        )