import time
from typing import Optional

from pulumi.dynamic import CreateResult, Resource, ResourceProvider
from pulumi.output import Input
from pulumi.resource import ResourceOptions


class Delay(Resource):
    """
    This is a Pulumi resource which adds an artifical delay to the deployment.  This is
    useful when there are resources are not immediately available upon creation, but are
    depended upon by another resource.  For example, when creating a Pinpoint event
    stream, the role policy is required by the stream but takes time to propogate:

    ```python
    pinpoint_stream_role_policy = iam.RolePolicy("MyPinpointStreamPolicy", ...)

    pinpoint_stream_role_delay = Delay("EventStreamRoleDelay",
        delay_time=10,
        opts=ResourceOptions(depends_on=[pinpoint_stream_role_policy])
    )

    pinpoint_stream = pinpoint.EventStream("MyPinpointEventStream", ...
        opts=ResourceOptions(depends_on=[ pinpoint_stream_role_delay ])
    )
    ```

    """

    def __init__(
        self,
        resource_name: str,
        delay_time: Input[int],
        opts: Optional[ResourceOptions] = None,
    ):
        super().__init__(
            DelayProvider(resource_name),
            resource_name,
            {"delay_time": delay_time},
            opts,
        )


class DelayProvider(ResourceProvider):
    def __init__(self, resource_name):
        self.resource_name = resource_name

    def create(self, inputs):
        time.sleep(inputs["delay_time"])
        return CreateResult(self.resource_name, inputs)
