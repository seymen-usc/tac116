import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import json

# ─────────────────────────────────────────────────────────────
# SECTION: How a for loop works — live visual explainer
# Inputs are linked to the visualization: changing start/stop/
# step or the string instantly rebuilds the sequence display.
# ─────────────────────────────────────────────────────────────

VISUAL_HTML = """
<style>
  #fldemo * { box-sizing: border-box; }
  #fldemo { padding: 14px; background: #f8f8f8; border: 1px solid #ddd;
            border-radius: 8px; margin-bottom: 16px; font-family: sans-serif; }
  .fl-tabs { display: flex; gap: 8px; margin-bottom: 12px; }
  .fl-tab  { padding: 5px 14px; font-size: 13px; border: 1px solid #bbb;
             border-radius: 6px; background: #fff; color: #555; cursor: pointer; }
  .fl-tab.on { background: #e8f0fe; color: #1a73e8; border-color: #1a73e8; font-weight: 600; }
  .fl-ctrl { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
  .fl-ctrl label { font-size: 12px; color: #666; }
  .fl-ctrl input[type=number] { width: 52px; font-family: monospace; font-size: 13px;
                                 text-align: center; border: 1px solid #ccc; border-radius: 4px;
                                 padding: 3px 4px; }
  .fl-ctrl input[type=text]   { width: 110px; font-family: monospace; font-size: 13px;
                                 border: 1px solid #ccc; border-radius: 4px; padding: 3px 6px; }
  .fl-code { background: #272822; color: #f8f8f2; border-radius: 6px; padding: 8px 14px;
             font-family: monospace; font-size: 13px; margin-bottom: 12px; white-space: pre;
             display: inline-block; }
  .fl-kw  { color: #66d9e8; font-weight: bold; }
  .fl-val { color: #e6db74; }
  .fl-seq { display: flex; gap: 6px; flex-wrap: wrap; align-items: flex-end;
            min-height: 72px; margin-bottom: 12px; }
  .fl-seg { display: inline-flex; flex-direction: column; align-items: center; gap: 3px; }
  .fl-arr { font-size: 16px; color: #1a73e8; line-height: 1; visibility: hidden; }
  .fl-arr.show { visibility: visible; }
  .fl-box { border: 1px solid #bbb; border-radius: 5px; padding: 6px 0;
            font-family: monospace; font-size: 13px; text-align: center;
            color: #222; background: #fff; transition: all .15s; min-width: 36px; }
  .fl-box.active { border-color: #1a73e8; background: #e8f0fe; color: #1a73e8; font-weight: bold; }
  .fl-box.done   { border-color: #34a853; background: #e6f4ea; color: #1e6b35; }
  .fl-idx { font-family: monospace; font-size: 10px; color: #999; }
  .fl-vrow { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
  .fl-vval { font-family: monospace; font-size: 14px; color: #555; }
  .fl-pill { font-size: 11px; padding: 2px 10px; border-radius: 10px; }
  .fl-pill.idle    { background: #f1f1f1; color: #888; }
  .fl-pill.running { background: #e8f0fe; color: #1a73e8; }
  .fl-pill.done    { background: #e6f4ea; color: #1e6b35; }
  .fl-out { background: #fff; border: 1px solid #ddd; border-radius: 5px;
            padding: 7px 12px; font-family: monospace; font-size: 13px;
            min-height: 34px; color: #333; }
  .fl-out-line { animation: flSlide .2s ease both; }
  @keyframes flSlide { from{opacity:0;transform:translateY(-4px)} to{opacity:1;transform:translateY(0)} }
  .fl-btns { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; align-items: center; }
  .fl-btn  { padding: 5px 14px; font-size: 13px; border: 1px solid #bbb; border-radius: 6px;
             background: #fff; color: #444; cursor: pointer; }
  .fl-btn.primary { background: #e8f0fe; color: #1a73e8; border-color: #1a73e8; }
  .fl-slabel { font-size: 12px; color: #888; margin-left: 4px; }
</style>

<div id="fldemo">
  <div class="fl-tabs">
    <button class="fl-tab on" id="ftab-r" onclick="flTab('range')">range loop</button>
    <button class="fl-tab"    id="ftab-s" onclick="flTab('string')">string loop</button>
  </div>

  <div id="fctrl-r" class="fl-ctrl">
    <label>start</label>
    <input type="number" id="fr-start" value="0" min="-999" max="999" oninput="flInputChange()">
    <label>stop</label>
    <input type="number" id="fr-stop"  value="5" min="-999" max="999" oninput="flInputChange()">
    <label>step</label>
    <input type="number" id="fr-step"  value="1" min="-999"  max="999"  oninput="flInputChange()">
  </div>
  <div id="fctrl-s" class="fl-ctrl" style="display:none">
    <label>string</label>
    <input type="text" id="fs-val" value="hello" maxlength="14" oninput="flInputChange()">
  </div>

  <div class="fl-code" id="fl-code"></div>

  <div style="font-size:12px;color:#666;margin-bottom:6px">
    Sequence items — arrow marks the current one:
  </div>
  <div class="fl-seq" id="fl-seq"></div>

  <div class="fl-vrow">
    <div style="font-size:12px;color:#666">variable:</div>
    <div class="fl-vval" id="fl-vval">—</div>
    <div class="fl-pill idle" id="fl-pill">idle</div>
  </div>

  <div style="font-size:12px;color:#666;margin-bottom:5px">Output:</div>
  <div class="fl-out" id="fl-out"><span style="color:#bbb">run the loop to see output…</span></div>

  <div class="fl-btns">
    <button class="fl-btn primary" id="fl-runbtn" onclick="flTogglePlay()">&#9654; Run</button>
    <button class="fl-btn" onclick="flStep()">Step &#8594;</button>
    <button class="fl-btn" onclick="flReset()">&#8635; Reset</button>
    <span class="fl-slabel">speed</span>
    <input type="range" id="fl-speed" min="200" max="1600" value="800" step="100"
           style="width:80px">
  </div>
</div>

<script>
(function() {
  var _mode = 'range';
  var _items = [];
  var _idx = 0;
  var _out = [];
  var _playing = false;
  var _timer = null;

  function varName() { return _mode === 'range' ? 'i' : 'char'; }

  function getItems() {
    if (_mode === 'range') {
      var s = parseInt(document.getElementById('fr-start').value) || 0;
      var e = parseInt(document.getElementById('fr-stop').value)  || 5;
      var p = parseInt(document.getElementById('fr-step').value)  || 1;
      if (p < 1) p = 1;
      var a = [];
      for (var v = s; v < e; v += p) { a.push(v); if (a.length > 20) break; }
      return a;
    } else {
      return (document.getElementById('fs-val').value || '').split('').slice(0, 20);
    }
  }

  function getSpeed() { return 2000 - parseInt(document.getElementById('fl-speed').value); }

  function updateCode() {
    var el = document.getElementById('fl-code');
    if (_mode === 'range') {
      var s = document.getElementById('fr-start').value;
      var e = document.getElementById('fr-stop').value;
      var p = document.getElementById('fr-step').value;
      el.innerHTML = '<span class="fl-kw">for</span> i <span class="fl-kw">in</span> ' +
        '<span class="fl-val">range(' + s + ', ' + e + ', ' + p + ')</span>:\\n    print(i)';
    } else {
      var sv = document.getElementById('fs-val').value || '';
      el.innerHTML = '<span class="fl-kw">for</span> char <span class="fl-kw">in</span> ' +
        '<span class="fl-val">"' + sv + '"</span>:\\n    print(char)';
    }
  }

  function renderSeq() {
    var row = document.getElementById('fl-seq');
    var n = _items.length;
    if (!n) {
      row.innerHTML = '<span style="font-size:13px;color:#999">no items — check inputs</span>';
      return;
    }
    var bw = Math.min(56, Math.max(34, Math.floor((560 - (n-1)*6) / n)));
    var html = '';
    for (var i = 0; i < n; i++) {
      var isAct = (i === _idx && _idx < n);
      var isDone = (_idx > 0 && i < _idx);
      var bc = 'fl-box' + (isAct ? ' active' : isDone ? ' done' : '');
      var ac = 'fl-arr' + (isAct ? ' show' : '');
      html += '<div class="fl-seg" style="width:' + bw + 'px">' +
        '<div class="' + ac + '">&#8595;</div>' +
        '<div class="' + bc + '" style="width:' + bw + 'px">' + _items[i] + '</div>' +
        '<div class="fl-idx">[' + i + ']</div></div>';
    }
    row.innerHTML = html;
  }

  function renderVar() {
    var ve = document.getElementById('fl-vval');
    var pe = document.getElementById('fl-pill');
    if (_items.length === 0 || _idx < 0) {
      ve.textContent = '—'; ve.style.color = '#888';
      pe.className = 'fl-pill idle'; pe.textContent = 'idle';
    } else if (_idx >= _items.length) {
      ve.textContent = varName() + ' = (done)'; ve.style.color = '#1e6b35';
      pe.className = 'fl-pill done'; pe.textContent = 'complete';
    } else {
      ve.textContent = varName() + ' = ' + _items[_idx]; ve.style.color = '#1a73e8';
      pe.className = 'fl-pill running';
      pe.textContent = 'iter ' + (_idx + 1) + ' / ' + _items.length;
    }
  }

  function renderOut() {
    var el = document.getElementById('fl-out');
    if (!_out.length) {
      el.innerHTML = '<span style="color:#bbb">run the loop to see output…</span>'; return;
    }
    el.innerHTML = _out.map(function(l) {
      return '<div class="fl-out-line">' + l + '</div>';
    }).join('');
    if (_idx >= _items.length && _items.length > 0) {
      el.innerHTML += '<div class="fl-out-line" style="color:#1e6b35;margin-top:3px;' +
        'font-family:sans-serif;font-size:12px">&#10003; loop finished</div>';
    }
  }

  function render() { renderSeq(); renderVar(); renderOut(); }

  function updateBtn() {
    var b = document.getElementById('fl-runbtn');
    b.innerHTML = _playing ? '&#9646;&#9646; Pause' : '&#9654; Run';
  }

  window.flInputChange = function() {
    stopTimer(); _playing = false; updateBtn();
    _items = getItems(); _idx = 0; _out = [];
    updateCode(); render();
  };

  window.flTab = function(m) {
    _mode = m;
    document.getElementById('ftab-r').className = 'fl-tab' + (m==='range' ? ' on' : '');
    document.getElementById('ftab-s').className = 'fl-tab' + (m==='string' ? ' on' : '');
    document.getElementById('fctrl-r').style.display = m==='range' ? '' : 'none';
    document.getElementById('fctrl-s').style.display = m==='string' ? '' : 'none';
    flInputChange();
  };

  window.flReset = function() {
    stopTimer(); _playing = false; updateBtn();
    _items = getItems(); _idx = 0; _out = []; render();
  };

  window.flStep = function() {
    stopTimer(); _playing = false; updateBtn();
    if (_idx === 0) _out = [];
    if (_idx >= _items.length) { render(); return; }
    _out.push(String(_items[_idx])); _idx++;
    render();
  };

  function runStep() {
    if (!_playing) return;
    if (_idx >= _items.length) { _playing = false; updateBtn(); render(); return; }
    _out.push(String(_items[_idx])); _idx++;
    render();
    _timer = setTimeout(runStep, getSpeed());
  }

  window.flTogglePlay = function() {
    if (_playing) { stopTimer(); _playing = false; updateBtn(); renderSeq(); return; }
    if (_idx >= _items.length) { _idx = 0; _out = []; }
    if (_idx === 0) _out = [];
    _playing = true; updateBtn();
    runStep();
  };

  function stopTimer() { if (_timer) { clearTimeout(_timer); _timer = null; } }

  updateCode(); _items = getItems(); render();
})();
</script>
"""

display(HTML(VISUAL_HTML))

# ─────────────────────────────────────────────────────────────
# SECTION: Interactive loop runner widget (original code below)
# ─────────────────────────────────────────────────────────────

output_widget = widgets.Output()

loop_type_selector = widgets.RadioButtons(
    options=['Range', 'String'],
    value='Range',
    description='Loop Type:',
    disabled=False
)

start_input = widgets.IntText(value=0, description='Start:')
stop_input  = widgets.IntText(value=5, description='Stop:')
step_input  = widgets.IntText(value=1, description='Step:')
range_widgets = widgets.VBox([start_input, stop_input, step_input])
range_widgets.layout.visibility = 'visible'

string_input   = widgets.Text(value='hello', description='String:')
string_widgets = widgets.VBox([string_input])
string_widgets.layout.visibility = 'hidden'

def update_widgets(change):
    if loop_type_selector.value == 'Range':
        range_widgets.layout.visibility  = 'visible'
        string_widgets.layout.visibility = 'hidden'
    else:
        range_widgets.layout.visibility  = 'hidden'
        string_widgets.layout.visibility = 'visible'

loop_type_selector.observe(update_widgets, names='value')

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

run_button = widgets.Button(description="Run Loop")
run_button.on_click(run_loop)

display(loop_type_selector, range_widgets, string_widgets, run_button, output_widget)
update_widgets({'new': loop_type_selector.value})
