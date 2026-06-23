from ipywidgets import interact, IntText, Text
from IPython.display import display, HTML

def my_function(text, start, stop, step):
    if not text:
        print("Please enter some text.")
        return

    # Ensure start, stop, step are within valid ranges
    n = len(text)
    # Adjust for negative indices if any
    actual_start = start if start >= 0 else max(0, n + start)
    actual_stop = stop if stop >= 0 else max(0, n + stop)

    # Handle default values and out-of-bounds for slicing gracefully
    # Python slicing handles this implicitly, but for visualization, we need to be careful
    # to highlight correctly.

    sliced_text = text[start:stop:step]

    highlighted_html = []
    current_index = 0
    
    # Create a list of characters with their original indices
    indexed_chars = []
    for i, char in enumerate(text):
        indexed_chars.append({'char': char, 'original_index': i})

    # Determine which characters are part of the slice
    slice_indices = set()
    try:
        temp_slice = text[start:stop:step]
        # Reconstruct the indices that would be included by the slice
        idx_iter = range(n)[start:stop:step]
        for i, _ in enumerate(temp_slice):
            slice_indices.add(idx_iter[i])
    except Exception: # Handle potential invalid slices from the UI
        pass

    # Build the HTML output
    header_html = "<div style='font-family: monospace; font-size: 14px;'>"
    indices_html = "<div>" + "&nbsp;&nbsp;".join(f'{i:<2}' for i in range(n)) + "</div>"
    text_html = "<div>" + "&nbsp;&nbsp;".join(char for char in text) + "</div>"
    
    char_display = []
    for i, char in enumerate(text):
        if i in slice_indices:
            char_display.append(f"<span style='background-color: red;'>{char}</span>")
        else:
            char_display.append(f"<span>{char}</span>")
    
    text_display_html = "<div>" + "&nbsp;&nbsp;".join(char_display) + "</div>"

    output_html = f"<div style='font-family: monospace; font-size: 16px;'>"
    output_html += f"<p><b>Original Text:</b> {text}</p>"
    output_html += f"<p><b>Sliced Text:</b> <span style='background-color: red;'>{sliced_text}</span></p>"
    output_html += f"<p><b>Indices:</b></p>"
    output_html += f"<pre>{' '.join(f'{i: <2}' for i in range(len(text)))}\n{' '.join(char for char in text)}</pre>"
    output_html += f"<p><b>Highlighted Slice:</b></p>"
    output_html += f"<pre>{' '.join(f'{i: <2}' for i in range(len(text)))}\n{text_display_html.replace('<div>', '').replace('</div>', '')}</pre>"
    output_html += "</div>"

    display(HTML(output_html))

# Create interactive widgets
text_widget = Text(value='Python Slicing Example', description='Text:')
start_slider = IntText(value=0, description='Start:')
stop_slider = IntText(value=10, description='Stop:') # Large enough initial value
step_slider = IntText(value=1, description='Step:')

# Link widgets to the visualization function
interact(my_function, text=text_widget, start=start_slider, stop=stop_slider, step=step_slider);
