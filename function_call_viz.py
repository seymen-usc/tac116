from IPython.display import display, HTML, clear_output
import ipywidgets as widgets

# Input widget
temp_input = widgets.IntText(
    value=75,
    description='Temp:'
)

run_button = widgets.Button(
    description="Run Program",
    button_style="success"
)

output = widgets.Output()

def run_program(button):
    with output:
        clear_output()

        weather = temp_input.value

        steps = []

        # Step 1
        steps.append("➡️ main() starts")

        # Step 2
        steps.append("📢 print('Welcome to the weather checker!')")

        # Step 3
        steps.append("➡️ showWeather() called")

        # Step 4
        steps.append(f"🌡️ weather = {weather}")

        # Decision
        if weather > 80:
            steps.append(" weather > 80 ? → TRUE")
            steps.append(" print('It seems hot!')")
        else:
            steps.append(" weather > 80 ? → FALSE")
            steps.append(" print('Nice weather!')")

        # Final
        steps.append(" print('Thanks for using the weather checker!')")
        steps.append(" Program Ends")

        html = "<h3>Program Flow</h3>"

        for step in steps:
            html += (
                "<div style='padding:10px;"
                "margin:5px;"
                "border:1px solid #ccc;"
                "border-radius:8px;'>"
                f"{step}</div>"
            )

        display(HTML(html))

run_button.on_click(run_program)

display(temp_input)
display(run_button)
display(output)
