import ipywidgets as widgets
from IPython.display import display, clear_output

# Output widget to display results
output_widget = widgets.Output()

# Dropdown for loop type selection
loop_type_selector = widgets.RadioButtons(
    options=['Range', 'String'],
    value='Range',
    description='Loop Type:',
    disabled=False
)

# Widgets for 'Range' options
start_input = widgets.IntText(value=0, description='Start:')
stop_input = widgets.IntText(value=5, description='Stop:')
step_input = widgets.IntText(value=1, description='Step:')
range_widgets = widgets.VBox([start_input, stop_input, step_input])
range_widgets.layout.visibility = 'visible' # Initialize as visible

# Widget for 'String' option
string_input = widgets.Text(value='hello', description='String:')
string_widgets = widgets.VBox([string_input])
string_widgets.layout.visibility = 'hidden' # Initialize as hidden

# Function to update widget visibility
def update_widgets(change):
    if loop_type_selector.value == 'Range':
        range_widgets.layout.visibility = 'visible'
        string_widgets.layout.visibility = 'hidden'
    else:
        range_widgets.layout.visibility = 'hidden'
        string_widgets.layout.visibility = 'visible'

# Attach observer to update widgets when loop type changes
loop_type_selector.observe(update_widgets, names='value')

# Function to execute the loop and display output
def run_loop(b):
    with output_widget:
        clear_output()
        print('Loop Output:')
        if loop_type_selector.value == 'Range':
            try:
                for i in range(start_input.value, stop_input.value, step_input.value):
                    print(i)
            except Exception as e:
                print(f"Error in Range loop: {e}")
        else:
            for char in string_input.value:
                print(char)

# Run button
run_button = widgets.Button(description="Run Loop")
run_button.on_click(run_loop)

# Arrange and display all widgets
display(loop_type_selector, range_widgets, string_widgets, run_button, output_widget)

# Initial display of widgets (ensuring only relevant ones are visible)
update_widgets({'new': loop_type_selector.value})
