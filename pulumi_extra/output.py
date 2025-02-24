"""Utils for outputs."""

from __future__ import annotations

from typing import TYPE_CHECKING, overload

import pulumi
from jinja2 import StrictUndefined, Template

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path
    from typing import Any


@overload
def render_template(
    template_file: Path,
    *,
    context: Mapping[str, Any],
) -> str: ...


@overload
def render_template(
    template_file: Path,
    *,
    inputs: Mapping[str, pulumi.Input[Any]],
) -> pulumi.Output[str]: ...


def render_template(
    template_file: Path,
    *,
    context: Mapping[str, Any] | None = None,
    inputs: Mapping[str, pulumi.Input[Any]] | None = None,
) -> str | pulumi.Output[str]:
    """Render a template file with the given context."""
    template = Template(
        template_file.read_text(),
        undefined=StrictUndefined,
    )

    if context is not None and inputs is None:
        return template.render(context)

    if context is None and inputs is not None:
        return pulumi.Output.all(inputs).apply(lambda args: template.render(args[0]))

    msg = "Either context or input must be provided." + str(context) + ", " + str(inputs)
    raise ValueError(msg)
