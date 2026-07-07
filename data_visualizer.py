"""
data_visualizer.py
Quick tree visualizer for nested dict/list/scalar structures.

Usage:
    from data_visualizer import visualize

    data = {
        "user": "Ana",
        "scores": [10, 20, {"bonus": 5}],
        "tags": ["a", ["nested", "list"]],
    }
    visualize(data)

Design:
- dict  -> shown with 🔑 key labels, braces {}
- list  -> shown with #index labels, brackets []
- scalars -> shown with their type + value
- Recurses to any depth, indenting with tree branch characters.
"""

from typing import Any


# ANSI colors (safe to ignore if terminal doesn't support them)
class _C:
    DICT = "\033[94m"   # blue
    LIST = "\033[92m"   # green
    KEY = "\033[93m"    # yellow
    IDX = "\033[96m"    # cyan
    VAL = "\033[0m"     # reset/default
    TYPE = "\033[90m"   # gray
    END = "\033[0m"


def _type_tag(value: Any) -> str:
    return f"{_C.TYPE}({type(value).__name__}){_C.END}"


def _render(value: Any, prefix: str = "", is_last: bool = True, label: str = "") -> list:
    lines = []
    connector = "└── " if is_last else "├── "
    extension = "    " if is_last else "│   "

    if isinstance(value, dict):
        header = f"{prefix}{connector}{label}{_C.DICT}{{dict}}{_C.END}"
        lines.append(header)
        items = list(value.items())
        for i, (k, v) in enumerate(items):
            last = i == len(items) - 1
            key_label = f"{_C.KEY}key '{k}'{_C.END}: "
            lines.extend(_render(v, prefix + extension, last, key_label))

    elif isinstance(value, list):
        header = f"{prefix}{connector}{label}{_C.LIST}[list]{_C.END}"
        lines.append(header)
        for i, v in enumerate(value):
            last = i == len(value) - 1
            idx_label = f"{_C.IDX}#{i}{_C.END}: "
            lines.extend(_render(v, prefix + extension, last, idx_label))

    else:
        val_repr = repr(value)
        lines.append(f"{prefix}{connector}{label}{val_repr} {_type_tag(value)}")

    return lines


def visualize(data: Any, title: str = "root", use_color: bool = True) -> None:
    """Print a tree visualization of nested dict/list/scalar data."""
    global _C
    if not use_color:
        for attr in ("DICT", "LIST", "KEY", "IDX", "VAL", "TYPE", "END"):
            setattr(_C, attr, "")

    root_label = f"{_C.KEY}{title}{_C.END}: "
    lines = _render(data, prefix="", is_last=True, label=root_label)
    print("\n".join(lines))


def to_string(data: Any, title: str = "root", use_color: bool = False) -> str:
    """Same as visualize(), but returns the tree as a string instead of printing."""
    global _C
    if not use_color:
        for attr in ("DICT", "LIST", "KEY", "IDX", "VAL", "TYPE", "END"):
            setattr(_C, attr, "")
    root_label = f"{title}: "
    return "\n".join(_render(data, prefix="", is_last=True, label=root_label))


if __name__ == "__main__":
    sample = {
        "user": "Ana",
        "active": True,
        "scores": [10, 20, {"bonus": 5, "notes": ["great", "improved"]}],
        "tags": ["a", ["nested", "list", {"deep": 1}]],
        "meta": {"created": "2026-07-07", "flags": []},
    }
    visualize(sample, title="data")
