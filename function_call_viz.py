# Google Colab code-flow highlighter
# Paste this into a Colab cell and run it.

from IPython.display import display, clear_output, HTML
import ipywidgets as widgets
import time

# The code we want to visualize (shown on screen the whole time)
CODE_LINES = [
    "def showWeather():",
    "    weather = int(input(\"What is the temperature? \") )",
    "    if weather > 80:",
    "        print(\"It seems hot!\")",
    "    else:",
    "        print(\"Nice weather!\")",
    "",
    "def main():",
    "    print(\"Welcome to the weather checker!\")",
    "    showWeather()",
    "    print(\"Thanks for using the weather checker!\")",
    "",
    "main()",
]


def code_view(active_line=None, executed=None, title="Program code"):
    """Render the code with one active line highlighted and an arrow shown."""
    executed = executed or set()
    rows = []
    for i, line in enumerate(CODE_LINES, start=1):
        is_active = (i == active_line)
        is_done = (i in executed and not is_active)
        arrow = "➜" if is_active else " "
        bg = "#fde68a" if is_active else ("#dcfce7" if is_done else "transparent")
        border = "1px solid #f59e0b" if is_active else ("1px solid #86efac" if is_done else "1px solid transparent")
        color = "#111827" if is_active or is_done else "#6b7280"
        rows.append(
            f"""
            <div style='display:grid;grid-template-columns:30px 40px 1fr;align-items:stretch;gap:8px;margin:2px 0;'>
              <div style='text-align:right;color:#94a3b8;font-family:monospace;padding-top:2px;'>{i}</div>
              <div style='font-family:monospace;color:#ef4444;font-weight:700;'>{arrow}</div>
              <div style='font-family:monospace;white-space:pre;background:{bg};border:{border};border-radius:8px;padding:4px 8px;color:{color};'>
                {line if line else '&nbsp;'}
              </div>
            </div>
            """
        )

    return f"""
    <div style='border:1px solid #cbd5e1;border-radius:14px;padding:14px;background:#f8fafc;'>
      <div style='font-weight:700;margin-bottom:10px;color:#0f172a;'>{title}</div>
      {''.join(rows)}
    </div>
    """


class CodeFlowVisualizer:
    def __init__(self):
        self.temp = widgets.IntSlider(
            value=75,
            min=0,
            max=120,
            step=1,
            description="Temp:",
            continuous_update=False,
            layout=widgets.Layout(width="360px"),
        )

        self.run_btn = widgets.Button(description="Run", button_style="success")
        self.reset_btn = widgets.Button(description="Reset")
        self.out = widgets.Output()

        self.run_btn.on_click(self.run_program)
        self.reset_btn.on_click(self.reset_program)

        self.container = widgets.VBox([
            widgets.HTML("<h2>Weather Checker Code Flow</h2>"),
            widgets.HTML("<p>Click Run to see the arrow move through the code. The active line is highlighted.</p>"),
            self.temp,
            widgets.HBox([self.run_btn, self.reset_btn]),
            self.out,
        ])

        self.render_start()

    def render_start(self):
        with self.out:
            clear_output()
            display(HTML(code_view(active_line=13, executed={13}, title="Ready to run")))
            display(HTML("<p style='color:#475569;margin-top:10px;'>Press <b>Run</b> to animate the program.</p>"))

    def show_frame(self, active_line, executed, message=""):
        with self.out:
            clear_output(wait=True)
            display(HTML(code_view(active_line=active_line, executed=executed, title="Running")))
            if message:
                display(HTML(f"<p style='margin-top:10px;font-family:monospace;background:#111827;color:#f8fafc;padding:10px;border-radius:10px;'>{message}</p>"))

    def reset_program(self, _):
        self.render_start()

    def run_program(self, _):
        weather = self.temp.value
        executed = set()

        frames = [
            (8,  {8},  "main() starts"),
            (9,  {8, 9},  "print('Welcome to the weather checker!')"),
            (10, {8, 9, 10},  "showWeather() is called"),
            (1,  {8, 9, 10, 1},  "showWeather(): function begins"),
            (2,  {8, 9, 10, 1, 2},  f'weather = {weather}'),
            (3,  {8, 9, 10, 1, 2, 3},  f'if weather > 80 -> {weather > 80}'),
        ]

        if weather > 80:
            frames.append((4, {8, 9, 10, 1, 2, 3, 4}, "print('It seems hot!')"))
        else:
            frames.extend([
                (5, {8, 9, 10, 1, 2, 3, 5}, "else branch selected"),
                (6, {8, 9, 10, 1, 2, 3, 5, 6}, "print('Nice weather!')"),
            ])

        frames.extend([
            (11, {8, 9, 10, 1, 2, 3, 4 if weather > 80 else 6, 11}, "showWeather() ends"),
            (12, {8, 9, 10, 1, 2, 3, 4 if weather > 80 else 6, 11, 12}, "print('Thanks for using the weather checker!')"),
            (13, {8, 9, 10, 1, 2, 3, 4 if weather > 80 else 6, 11, 12, 13}, "Program finished"),
        ])

        for active_line, executed, message in frames:
            self.show_frame(active_line, executed, message)
            time.sleep(1.0)

        with self.out:
            display(HTML("<p style='color:#065f46;font-weight:700;'>Done.</p>"))


viz = CodeFlowVisualizer()
display(viz.container)
