# Google Colab-friendly List Playground
# Paste this into a Colab cell and run it.

from IPython.display import display, clear_output, HTML
import ipywidgets as widgets


def parse_list(text):
    """Convert comma-separated text into a Python list of strings."""
    items = [item.strip() for item in text.split(",")]
    return [item for item in items if item]


def format_list(lst):
    return "[" + ", ".join(repr(item) for item in lst) + "]"


def safe_int(text, default):
    try:
        return int(text)
    except Exception:
        return default


class ListPlayground:
    def __init__(self):
        self.list_text = widgets.Textarea(
            value="apple, banana, cherry, date",
            description="List:",
            layout=widgets.Layout(width="100%", height="90px"),
        )

        self.operation = widgets.Dropdown(
            options=[
                ("append", "append"),
                ("pop", "pop"),
                ("remove", "remove"),
                ("indexing", "index"),
                ("slicing", "slice"),
            ],
            value="append",
            description="Op:",
            layout=widgets.Layout(width="250px"),
        )

        self.value_box = widgets.Text(
            value="kiwi",
            description="Value:",
            layout=widgets.Layout(width="250px"),
        )

        self.index_box = widgets.Text(
            value="1",
            description="Index:",
            layout=widgets.Layout(width="250px"),
        )

        self.start_box = widgets.Text(
            value="1",
            description="Start:",
            layout=widgets.Layout(width="250px"),
        )

        self.end_box = widgets.Text(
            value="3",
            description="End:",
            layout=widgets.Layout(width="250px"),
        )

        self.load_button = widgets.Button(description="Load List", button_style="")
        self.run_button = widgets.Button(description="Run Operation", button_style="success")
        self.reset_button = widgets.Button(description="Reset", button_style="warning")

        self.hint = widgets.HTML()
        self.output = widgets.Output()
        self.history = []
        self.current_list = parse_list(self.list_text.value)

        self.load_button.on_click(self.on_load)
        self.run_button.on_click(self.on_run)
        self.reset_button.on_click(self.on_reset)
        self.operation.observe(self.on_operation_change, names="value")

        self.controls_row = widgets.HBox([self.operation, self.value_box, self.index_box, self.start_box, self.end_box])
        self.buttons_row = widgets.HBox([self.load_button, self.run_button, self.reset_button])

        self.container = widgets.VBox([
            widgets.HTML("<h2>List Operations Playground</h2>"),
            widgets.HTML("<p>Try append, pop, remove, indexing, and slicing. Select one and watch the list change.</p>"),
            self.list_text,
            self.controls_row,
            self.hint,
            self.buttons_row,
            self.output,
        ])

        self.update_hint()
        self.render()

    def update_hint(self):
        op = self.operation.value
        hints = {
            "append": "<b>append</b>: add one item to the end of the list.",
            "pop": "<b>pop</b>: remove and return an item by index, or the last item.",
            "remove": "<b>remove</b>: remove the first matching value.",
            "index": "<b>indexing</b>: read an item at a position without changing the list.",
            "slice": "<b>slicing</b>: view part of the list without changing the list.",
        }
        self.hint.value = f"<div style='padding:8px 0;color:#444'>{hints[op]}</div>"

    def refresh_controls(self):
        op = self.operation.value
        self.value_box.layout.display = "block" if op in ("append", "remove") else "none"
        self.index_box.layout.display = "block" if op in ("pop", "index") else "none"
        self.start_box.layout.display = "block" if op == "slice" else "none"
        self.end_box.layout.display = "block" if op == "slice" else "none"

    def render(self):
        with self.output:
            clear_output()
            display(HTML(f"<p><b>Current list:</b> {format_list(self.current_list)}</p>"))
            if self.history:
                display(HTML("<p><b>Recent changes</b></p>"))
                for item in self.history[:5]:
                    display(HTML(
                        f"<div style='margin:8px 0;padding:8px;border:1px solid #ddd;border-radius:8px;'>"
                        f"<b>{item['op']}</b><br>"
                        f"{item['note']}<br>"
                        f"<small>Before: {format_list(item['before'])}</small><br>"
                        f"<small>After: {format_list(item['after'])}</small>"
                        f"</div>"
                    ))

    def on_operation_change(self, change):
        self.update_hint()
        self.refresh_controls()

    def on_load(self, _):
        self.current_list = parse_list(self.list_text.value)
        self.history = []
        with self.output:
            clear_output()
            display(HTML(f"<p>Loaded {len(self.current_list)} item(s): {format_list(self.current_list)}</p>"))

    def on_reset(self, _):
        self.current_list = parse_list(self.list_text.value)
        self.history = []
        with self.output:
            clear_output()
            display(HTML(f"<p>Reset to {format_list(self.current_list)}</p>"))

    def on_run(self, _):
        before = list(self.current_list)
        after = list(self.current_list)
        op = self.operation.value
        note = ""
        message = ""

        if op == "append":
            value = self.value_box.value
            after.append(value)
            note = f"append({value!r}) adds the value to the end."
            message = f"Appended {value!r}."

        elif op == "pop":
            if not after:
                note = "pop() on an empty list does nothing here."
                message = "The list is empty, so pop cannot remove anything."
            else:
                idx = self.index_box.value.strip()
                idx = len(after) - 1 if idx == "" else safe_int(idx, len(after) - 1)
                if idx < 0 or idx >= len(after):
                    note = f"Index {idx} is out of range."
                    message = f"Index {idx} is out of range for a list of length {len(after)}."
                else:
                    removed = after.pop(idx)
                    note = f"pop({idx}) removes and returns {removed!r}."
                    message = f"Popped {removed!r} at index {idx}."

        elif op == "remove":
            value = self.value_box.value
            if value in after:
                after.remove(value)
                note = f"remove({value!r}) deletes the first matching item."
                message = f"Removed first {value!r}."
            else:
                note = f"{value!r} was not found."
                message = f"Could not find {value!r} in the list."

        elif op == "index":
            idx = safe_int(self.index_box.value, 0)
            if idx < 0 or idx >= len(after):
                note = f"Index {idx} is out of range."
                message = f"Index {idx} is out of range for a list of length {len(after)}."
            else:
                note = f"list[{idx}] reads an item without changing the list."
                message = f"list[{idx}] is {after[idx]!r}."

        elif op == "slice":
            start = safe_int(self.start_box.value, 0)
            end = safe_int(self.end_box.value, len(after))
            sliced = after[start:end]
            note = f"list[{start}:{end}] returns a new list with items from {start} up to {end}."
            message = f"Slice result: {format_list(sliced)}."

        self.current_list = after
        self.history.insert(0, {
            "op": op,
            "before": before,
            "after": after,
            "note": note,
        })
        self.history = self.history[:5]

        with self.output:
            clear_output()
            display(HTML(f"<p><b>Result:</b> {message}</p>"))
            display(HTML(f"<p><b>Current list:</b> {format_list(self.current_list)}</p>"))
            if self.history:
                display(HTML("<p><b>Recent changes</b></p>"))
                for item in self.history:
                    display(HTML(
                        f"<div style='margin:8px 0;padding:8px;border:1px solid #ddd;border-radius:8px;'>"
                        f"<b>{item['op']}</b><br>"
                        f"{item['note']}<br>"
                        f"<small>Before: {format_list(item['before'])}</small><br>"
                        f"<small>After: {format_list(item['after'])}</small>"
                        f"</div>"
                    ))


# Create and display the playground
playground = ListPlayground()
display(playground.container)
