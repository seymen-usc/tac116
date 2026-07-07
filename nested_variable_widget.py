    """
    nested_variable_widget.py
    
    Reusable nested data visualizer for Python variables.
    
    Features:
    - Displays dictionaries and lists/tuples/sets as an expandable tree.
    - Shows labels for dict keys and indexes for list/tuple items.
    - Handles nested combinations like dict inside list, list inside dict, etc.
    - Can be imported into another .py file and called with one function.
    
    Example:
        from nested_variable_widget import visualize
    
        data = {
            "name": "Alex",
            "scores": [10, 20, {"bonus": 5}],
            "profile": {"age": 19, "tags": ["student", "coder"]},
        }
    
        visualize(data)
    """
def main():
    from __future__ import annotations
    
    from dataclasses import dataclass
    from typing import Any, Iterable, Optional
    import tkinter as tk
    from tkinter import ttk
    
    
    @dataclass(frozen=True)
    class NodeInfo:
        label: str
        type_name: str
        preview: str
    
    
    def _type_name(value: Any) -> str:
        if isinstance(value, dict):
            return "dict"
        if isinstance(value, list):
            return "list"
        if isinstance(value, tuple):
            return "tuple"
        if isinstance(value, set):
            return "set"
        return type(value).__name__
    
    
    def _preview(value: Any, limit: int = 80) -> str:
        if isinstance(value, str):
            text = repr(value)
        else:
            text = repr(value)
        if len(text) > limit:
            return text[: limit - 1] + "…"
        return text
    
    
    def _iter_children(value: Any) -> Iterable[tuple[str, Any]]:
        """
        Yield (label, child_value) pairs for supported container types.
        Dict keys become labels. Sequence items become [index] labels.
        """
        if isinstance(value, dict):
            for key, child in value.items():
                yield f"{key}", child
        elif isinstance(value, (list, tuple)):
            for i, child in enumerate(value):
                yield f"[{i}]", child
        elif isinstance(value, set):
            # Stable presentation: sort by repr when possible.
            try:
                items = sorted(value, key=lambda x: repr(x))
            except Exception:
                items = list(value)
            for i, child in enumerate(items):
                yield f"{{{i}}}", child
    
    
    def _build_node_info(label: str, value: Any) -> NodeInfo:
        return NodeInfo(label=label, type_name=_type_name(value), preview=_preview(value))
    
    
    def _insert_tree(tree: ttk.Treeview, parent: str, label: str, value: Any) -> None:
        info = _build_node_info(label, value)
        node_id = tree.insert(parent, "end", text=info.label, values=(info.type_name, info.preview))
    
        if isinstance(value, (dict, list, tuple, set)):
            for child_label, child_value in _iter_children(value):
                _insert_tree(tree, node_id, child_label, child_value)
    
    
    def _text_tree(value: Any, label: str = "root", indent: int = 0) -> str:
        pad = "    " * indent
        tname = _type_name(value)
        preview = _preview(value)
        lines = [f"{pad}{label} ({tname}): {preview}"]
    
        if isinstance(value, (dict, list, tuple, set)):
            for child_label, child_value in _iter_children(value):
                lines.append(_text_tree(child_value, child_label, indent + 1))
        return "\n".join(lines)
    
    
    def visualize(value: Any, title: str = "Nested Variable Viewer") -> None:
        """
        Open a simple tree-style widget that visualizes nested dict/list structures.
    
        Parameters
        ----------
        value:
            Any Python object. Nested dict/list/tuple/set structures are expanded.
        title:
            Window title.
    
        Notes
        -----
        - Dict children are shown by key labels.
        - List/tuple children are shown by numeric indexes like [0], [1], ...
        - Scalar values show their type and repr preview.
        """
        try:
            root = tk.Tk()
        except tk.TclError:
            # No display available; fall back to a console tree.
            print(_text_tree(value))
            return
    
        root.title(title)
        root.geometry("900x600")
    
        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="both", expand=True)
    
        header = ttk.Label(
            frame,
            text="Nested Variable Visualization",
            font=("TkDefaultFont", 14, "bold"),
        )
        header.pack(anchor="w", pady=(0, 10))
    
        columns = ("Type", "Value")
        tree = ttk.Treeview(frame, columns=columns, show="tree headings")
        tree.heading("#0", text="Label / Index")
        tree.heading("Type", text="Type")
        tree.heading("Value", text="Value")
    
        tree.column("#0", width=240, stretch=True)
        tree.column("Type", width=120, stretch=False)
        tree.column("Value", width=500, stretch=True)
    
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    
        tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
    
        # Root node
        root_id = tree.insert("", "end", text="root", values=(_type_name(value), _preview(value)))
        if isinstance(value, (dict, list, tuple, set)):
            for child_label, child_value in _iter_children(value):
                _insert_tree(tree, root_id, child_label, child_value)
            tree.item(root_id, open=True)
    
        # Expand the first level for convenience.
        for child in tree.get_children(root_id):
            tree.item(child, open=True)
    
        root.mainloop()
    
    
    def preview(value: Any) -> str:
        """
        Return a console-friendly tree preview of the nested structure.
        Useful for debugging or environments where GUI windows are unavailable.
        """
        return _text_tree(value)
    
    
    __all__ = ["visualize", "preview"]
