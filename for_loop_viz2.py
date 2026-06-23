import ipywidgets as widgets
from IPython.display import display, clear_output, HTML

# ─────────────────────────────────────────────────────────────
# SECTION: How a for loop works — visual explainer with arrows
# ─────────────────────────────────────────────────────────────

VISUAL_HTML = """
<style>
  #fldemo * { box-sizing: border-box; font-family: monospace; }
  #fldemo { padding: 12px; background: #f8f8f8; border: 1px solid #ddd;
            border-radius: 8px; margin-bottom: 16px; }
  #fldemo h3 { font-family: sans-serif; font-size: 14px; margin: 0 0 10px;
               color: #333; font-weight: 600; }
  .fl-row { display: flex; align-items: flex-start; gap: 0; margin: 8px 0; }
  .fl-box { border: 1.5px solid #aaa; border-radius: 5px; padding: 6px 10px;
            background: #fff; font-size: 13px; min-width: 36px; text-align: center;
            color: #222; position: relative; }
  .fl-box.active { border-color: #1a73e8; background: #e8f0fe; color: #1a73e8;
                   font-weight: bold; }
  .fl-box.done   { border-color: #34a853; background: #e6f4ea; color: #34a853; }
  .fl-arrow { font-size: 18px; color: #1a73e8; line-height: 34px; padding: 0 4px; }
  .fl-label { font-family: sans-serif; font-size: 12px; color: #555;
              margin-left: 10px; align-self: center; }
  .fl-var   { font-family: monospace; font-size: 13px; color: #1a73e8;
              margin-left: 10px; align-self: center; }
  .fl-output { background: #fff; border: 1px solid #ccc; border-radius: 4px;
               padding: 6px 10px; font-size: 13px; min-height: 32px;
               margin-top: 8px; color: #333; }
  .fl-code { background: #272822; color: #f8f8f2; border-radius: 5px;
             padding: 8px 12px; font-size: 13px; margin-bottom: 10px;
             white-space: pre; display: inline-block; }
  .kw { color: #66d9e8; } .var { color: #a6e22e; } .val { color: #ae81ff; }
  .btn-step { font-family: sans-serif; font-size: 12px; padding: 4px 12px;
              border: 1px solid #1a73e8; border-radius: 4px; background: #e8f0fe;
              color: #1a73e8; cursor: pointer; margin-right: 6px; }
  .btn-reset { font-family: sans-serif; font-size: 12px; padding: 4px 12px;
               border: 1px solid #aaa; border-radius: 4px; background: #fff;
               color: #555; cursor: pointer; }
</style>

<div id="fldemo">
  <h3>🔁 How the for loop works — step through with arrows</h3>

  <div class="fl-code"><span class="kw">for</span> <span class="var">i</span> <span class="kw">in</span> <span class="val">range(0, 5, 1)</span>:
    print(<span class="var">i</span>)</div>

  <div style="font-family:sans-serif;font-size:12px;color:#555;margin-bottom:8px;">
    Items in the sequence — arrow shows which one is current:
  </div>

  <div class="fl-row" id="fl-boxes"></div>

  <div style="margin:6px 0 2px;font-family:sans-serif;font-size:12px;color:#555;">
    Current variable value:
  </div>
  <div class="fl-var" id="fl-varval" style="margin-bottom:8px;">
    (not started)
  </div>

  <div style="margin:6px 0 2px;font-family:sans-serif;font-size:12px;color:#555;">
    Output so far:
  </div>
  <div class="fl-output" id="fl-output">&nbsp;</div>

  <div style="margin-top:10px;">
    <button class="btn-step" onclick="flStep()">▶ Next step</button>
    <button class="btn-reset" onclick="flReset()">↺ Reset</button>
    <span id="fl-status" style="font-family:sans-serif;font-size:12px;
          color:#888;margin-left:8px;"></span>
  </div>
</div>

<script>
(function() {
  var items = [0, 1, 2, 3, 4];
  var idx = 0;
  var output = [];

  function render() {
    var boxRow = document.getElementById('fl-boxes');
    var html = '';
    for (var i = 0; i < items.length; i++) {
      var cls = 'fl-box';
      if (i === idx && idx < items.length) cls += ' active';
      if (i < idx) cls += ' done';
      if (i === idx && idx < items.length) {
        html += '<span class="fl-arrow">&#8595;</span>';
      } else if (i > 0) {
        html += '<span style="padding:0 4px"></span>';
      }
      html += '<span class="' + cls + '">' + items[i] + '</span>';
    }
    boxRow.innerHTML = html;

    var varEl = document.getElementById('fl-varval');
    if (idx < items.length) {
      varEl.textContent = 'i = ' + items[idx];
    } else {
      varEl.textContent = '(loop finished)';
    }

    var outEl = document.getElementById('fl-output');
    outEl.textContent = output.length ? output.join('  ') : '\u00a0';

    var st = document.getElementById('fl-status');
    if (idx >= items.length) {
      st.textContent = '✓ All ' + items.length + ' iterations complete.';
      st.style.color = '#34a853';
    } else {
      st.textContent = 'Iteration ' + (idx + 1) + ' of ' + items.length;
      st.style.color = '#888';
    }
  }

  window.flStep = function() {
    if (idx < items.length) {
      output.push(items[idx]);
      idx++;
      render();
    }
  };

  window.flReset = function() {
    idx = 0;
    output = [];
    render();
  };

  render();
})();
</script>
"""

display(HTML(VISUAL_HTML))

# ─────────────────────────────────────────────────────────────
# SECTION: Interactive loop runner widget (original code below)
# ─────────────────────────────────────────────────────────────

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
stop_input  = widgets.IntText(value=5, description='Stop:')
step_input  = widgets.IntText(value=1, description='Step:')
range_widgets = widgets.VBox([start_input, stop_input, step_input])
range_widgets.layout.visibility = 'visible'   # Initialize as visible

# Widget for 'String' option
string_input   = widgets.Text(value='hello', description='String:')
string_widgets = widgets.VBox([string_input])
string_widgets.layout.visibility = 'hidden'   # Initialize as hidden

# Function to update widget visibility
def update_widgets(change):
    if loop_type_selector.value == 'Range':
        range_widgets.layout.visibility  = 'visible'
        string_widgets.layout.visibility = 'hidden'
    else:
        range_widgets.layout.visibility  = 'hidden'
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
