from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pulumi
import pytest
from pulumi import automation

from pulumi_extra import override_resource_defaults
from tests._helpers import Order

pytestmark = [
    pytest.mark.order(Order.AfterRegistryInit),
    pytest.mark.integration,
]


def pulumi_program() -> None:
    import pulumi_docker as docker

    busybox = docker.RemoteImage(
        "busybox",
        opts=pulumi.ResourceOptions(
            transforms=[
                override_resource_defaults(
                    "*",
                    defaults={
                        "platform": "linux/amd64",
                    },
                ),
            ],
        ),
        name="busybox",
    )

    for attr in ("name", "platform"):
        pulumi.export(attr, getattr(busybox, attr))


@pytest.fixture
def pulumi_stack(tmpdir: Path) -> Iterator[automation.Stack]:
    stack = automation.create_or_select_stack(
        stack_name="test",
        project_name="test",
        program=pulumi_program,
        opts=automation.LocalWorkspaceOptions(
            env_vars={
                "PULUMI_BACKEND_URL": f"file://{tmpdir}",
                "PULUMI_CONFIG_PASSPHRASE": "test",
            },
        ),
    )
    stack.up(on_output=print)
    yield stack
    stack.destroy(on_output=print, remove=True)


# TODO(lasuillard): Test runtime breaks due to async loop conflicts; need per-test (at least thread level) isolation.
class Test__override_resource:
    def test(self, pulumi_stack: automation.Stack) -> None:
        # Arrange
        # ...

        # Act
        outputs = pulumi_stack.outputs()

        # Assert
        def _resolve_output_values(outputs: automation.OutputMap) -> dict[str, Any]:
            return {k: v.value for k, v in outputs.items()}

        assert _resolve_output_values(outputs) == {
            "name": "busybox",
            "platform": "linux/amd64",  # Original default value is ""
        }
