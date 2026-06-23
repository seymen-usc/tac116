from IPython.display import display, HTML, clear_output
import ipywidgets as widgets
import time

temp = widgets.IntSlider(
    value=75,
    min=0,
    max=120,
    description="Temp"
)

run_btn = widgets.Button(
    description="Run Program",
    button_style="success"
)

out = widgets.Output()

def show_step(lines):
    clear_output(wait=True)

    html = "<pre style='font-size:16px;'>"
    html += "\n".join(lines)
    html += "</pre>"

    display(temp)
    display(run_btn)
    display(out)

    with out:
        clear_output(wait=True)
        display(HTML(html))

def run_program(b):

    weather = temp.value

    steps = [
        [
            "➜ main()",
            "",
            "  print('Welcome to the weather checker!')",
            "  showWeather()",
            "  print('Thanks for using the weather checker!')"
        ],

        [
            "main()",
            "",
            "➜ print('Welcome to the weather checker!')"
        ],

        [
            "main()",
            "",
            "➜ showWeather()"
        ],

        [
            "showWeather()",
            "",
            f"➜ weather = {weather}"
        ]
    ]

    if weather > 80:
        steps.append([
            "showWeather()",
            "",
            "➜ if weather > 80: TRUE",
            "",
            "➜ print('It seems hot!')"
        ])
    else:
        steps.append([
            "showWeather()",
            "",
            "➜ if weather > 80: FALSE",
            "",
            "➜ print('Nice weather!')"
        ])

    steps.extend([
        [
            "main()",
            "",
            "➜ print('Thanks for using the weather checker!')"
        ],
        [
            "✅ Program Finished"
        ]
    ])

    for step in steps:
        show_step(step)
        time.sleep(1.2)

run_btn.on_click(run_program)

display(temp)
display(run_btn)
display(out)
