from __future__ import annotations

__all__ = ("Empty", "EmptyType")

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


class Empty:
    """A sentinel class used as placeholder."""


EmptyType: TypeAlias = Type[Empty]
