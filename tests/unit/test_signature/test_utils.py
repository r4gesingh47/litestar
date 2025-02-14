from __future__ import annotations

from typing import Any, List, Optional

import attrs
import pytest
from pydantic import BaseModel

from litestar._signature.utils import _any_attrs_annotation
from litestar.utils.signature import ParsedSignature


@attrs.define
class Foo:
    bar: str


class Bar(BaseModel):
    foo: str


@pytest.mark.parametrize("annotation", [Foo, List[Foo], Optional[Foo]])
def test_any_attrs_annotation(annotation: Any) -> None:
    def fn(foo: annotation) -> None:
        ...

    assert _any_attrs_annotation(ParsedSignature.from_fn(fn, {"annotation": annotation})) is True
