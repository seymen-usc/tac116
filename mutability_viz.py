def main():
    from IPython.display import display, clear_output, HTML
    import ipywidgets as widgets
    import time
    import html

    # A compact Colab-friendly visualizer focused on mutability vs. immutability.
    # It reuses the same "arrow walks through the code" idea as the code-flow
    # tracer, but adds a Memory View panel that shows which variable points to
    # which object, and whether a change is a MUTATION (shared, visible outside)
    # or a REBIND (a brand-new object, invisible outside). Paste into Colab and
    # run the final cell.

    ARROW = {'normal': '\u279c', 'call': '\u21b4', 'return': '\u21a9'}
    LINE_BG = {
        'normal': ('#fef08a', '#111827'),
        'call':   ('#bfdbfe', '#1e3a8a'),
        'return': ('#ddd6fe', '#4c1d95'),
    }
    TAG_COLOR = {'A': '#3b82f6', 'B': '#f59e0b', 'C': '#ec4899'}

    # ------------------------------------------------------------------ #
    # Rendering helpers
    # ------------------------------------------------------------------ #

    def render_code(code_lines, active_line=None, executed=None,
                     title='code.py', jump_type='normal'):
        executed = executed or set()
        rows = []
        for i, line in enumerate(code_lines, start=1):
            escaped = html.escape(line) if line else '&nbsp;'
            is_active = i == active_line
            is_done = i in executed and not is_active

            if is_active:
                bg, fg = LINE_BG.get(jump_type, LINE_BG['normal'])
                style = f'background:{bg};color:{fg};font-weight:700;border-radius:4px;'
                arrow = ARROW.get(jump_type, ARROW['normal'])
            elif is_done:
                style = 'background:#dcfce7;color:#111827;border-radius:4px;'
                arrow = ' '
            else:
                style = 'color:#64748b;'
                arrow = ' '

            rows.append(
                f"<span style='display:block;white-space:pre;line-height:1.15;padding:0 2px;{style}'>{arrow} {i:>2} | {escaped}</span>"
            )

        return f"""
        <div style='border:1px solid #cbd5e1;border-radius:10px;background:#f8fafc;padding:6px 8px;'>
          <div style='font-family:monospace;font-size:12px;font-weight:700;color:#0f172a;margin-bottom:4px;'>{html.escape(title)}</div>
          <div style='font-family:monospace;font-size:12px;line-height:1.15;'>{''.join(rows)}</div>
        </div>
        """

    def render_explanation(message, jump_type='normal', step_num=None, total_steps=None):
        bg, _fg = LINE_BG.get(jump_type, LINE_BG['normal'])
        badge = ''
        if jump_type == 'call':
            badge = ("<span style='background:#1e3a8a;color:#fff;border-radius:6px;"
                      "padding:1px 6px;font-size:11px;margin-right:6px;'>CALLING A FUNCTION</span>")
        elif jump_type == 'return':
            badge = ("<span style='background:#4c1d95;color:#fff;border-radius:6px;"
                      "padding:1px 6px;font-size:11px;margin-right:6px;'>RETURNING</span>")
        step_label = ''
        if step_num is not None and total_steps is not None:
            step_label = (f"<span style='color:#94a3b8;font-size:11px;margin-right:6px;'>"
                           f"Step {step_num}/{total_steps}</span>")
        return f"""
        <div style='margin-top:6px;padding:6px 10px;border:1px solid #e2e8f0;border-left:4px solid {bg};
                     border-radius:8px;background:#ffffff;font-family:monospace;font-size:12.5px;color:#1e293b;'>
          {step_label}{badge}{html.escape(message)}
        </div>
        """

    def render_output_console(lines):
        if not lines:
            body = "<span style='color:#64748b;'>(nothing printed yet)</span>"
        else:
            body = '<br>'.join(html.escape(l) for l in lines)
        return f"""
        <div style='margin-top:8px;border:1px solid #0f172a;border-radius:8px;background:#0f172a;padding:8px 10px;'>
          <div style='font-family:monospace;font-size:11px;color:#94a3b8;margin-bottom:4px;'>&#9654; Program Output</div>
          <div style='font-family:monospace;font-size:13px;color:#4ade80;line-height:1.5;'>{body}</div>
        </div>
        """

    def var_box(var, empty_label):
        if var is None:
            return (
                "<div style='flex:1;border:2px dashed #cbd5e1;border-radius:8px;"
                "padding:8px 10px;font-family:monospace;font-size:12px;color:#94a3b8;"
                "text-align:center;'>" + html.escape(empty_label) + "</div>"
            )
        color = TAG_COLOR.get(var['tag'], '#6b7280')
        return f"""
        <div style='flex:1;border:2px solid {color};border-radius:8px;padding:8px 10px;
                     font-family:monospace;font-size:12px;background:{color}1a;'>
          <div style='font-weight:700;color:#0f172a;'>{html.escape(var['name'])}</div>
          <div style='color:#0f172a;margin:2px 0;'>{html.escape(var['value'])}</div>
          <div style='font-size:10px;color:{color};font-weight:700;'>Object {var['tag']}</div>
        </div>
        """

    def render_memory(main_var, func_var, main_empty, func_empty):
        left = var_box(main_var, main_empty)
        right = var_box(func_var, func_empty)
        note = ''
        if main_var is not None and func_var is not None:
            if main_var['tag'] == func_var['tag']:
                note = (
                    "<div style='margin-top:6px;font-family:monospace;font-size:11.5px;"
                    "color:#065f46;'>&#128279; Same object in memory \u2014 a change through "
                    "either variable is visible through the other.</div>"
                )
            else:
                note = (
                    "<div style='margin-top:6px;font-family:monospace;font-size:11.5px;"
                    "color:#7c2d12;'>&#9986; Different objects now \u2014 these two variables "
                    "are no longer linked.</div>"
                )
        return f"""
        <div style='margin-top:8px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;padding:8px 10px;'>
          <div style='font-family:monospace;font-size:11px;color:#94a3b8;margin-bottom:6px;'>Memory View</div>
          <div style='display:flex;gap:10px;'>{left}{right}</div>
          {note}
        </div>
        """

    # ------------------------------------------------------------------ #
    # The three example programs
    # ------------------------------------------------------------------ #

    def build_immutable_frames():
        code_lines = [
            'def grow_number(x):',                      # 1
            '    x = x + 100',                           # 2
            '    print("x INSIDE grow_number:", x)',     # 3
            '',                                           # 4
            'def main1():',                               # 5
            '    x = 5',                                   # 6
            '    print("x BEFORE grow_number:", x)',       # 7
            '    grow_number(x)',                           # 8
            '    print("x AFTER grow_number:", x)',         # 9
            '',                                              # 10
            'main1()',                                        # 11
        ]

        frames = []
        seen = set()

        def add(line, msg, jump='normal', out=None, main_var=None, func_var=None):
            seen.add(line)
            frames.append({
                'active': line, 'executed': set(seen), 'msg': msg, 'jump': jump,
                'out': out, 'main_var': main_var, 'func_var': func_var,
            })

        add(1, "Python finds def grow_number(x). This registers the function, "
                "but nothing inside it runs yet.")
        add(5, "Python finds def main1(). Same idea \u2014 main1 is now defined "
                "and ready to be called later.")
        add(11, "Python reaches the last line, main1(). This CALL is where real "
                 "execution actually begins.")
        add(5, "Execution jumps into main1(), starting at line 5.", jump='call')

        obj_a = 5
        mv = {'name': 'x (main1)', 'value': str(obj_a), 'tag': 'A'}
        add(6, "Line 6 runs: x is set to 5. This creates a new integer object "
                "\u2014 call it Object A \u2014 and x now refers to it.",
            main_var=mv)
        add(7, "Line 7 prints x's value before calling grow_number \u2014 keep "
                "this in mind so we can compare it to the value AFTER the call.",
            out="x BEFORE grow_number: 5", main_var=mv)
        add(8, "Line 8 calls grow_number(x). Python is about to jump into that "
                "function, handing it a reference to Object A.",
            main_var=mv)

        fv = {'name': 'x (grow_number)', 'value': str(obj_a), 'tag': 'A'}
        add(1, "Execution jumps into grow_number(), starting at line 1. The "
                "parameter x now also refers to Object A \u2014 right now both "
                "x's point to the exact same value.",
            jump='call', main_var=mv, func_var=fv)

        obj_b = obj_a + 100
        fv = {'name': 'x (grow_number)', 'value': str(obj_b), 'tag': 'B'}
        add(2, "Line 2 runs: x + 100 is computed as 105. Integers can never be "
                "changed in place, so Python creates a brand-new object (Object "
                "B) and rebinds the LOCAL x to it. The outer x in main1 is "
                "completely unaffected.",
            main_var=mv, func_var=fv)
        add(3, "Line 3 prints the function's local x \u2014 Object B's value.",
            out="x INSIDE grow_number: 105", main_var=mv, func_var=fv)

        add(9, "grow_number() has no more lines, so it ends. Its local x "
                "(Object B) disappears entirely. Execution returns to line 9, "
                "right after the call.",
            jump='return', main_var=mv, func_var=None)
        add(9, "Line 9 runs: print(...). The value is unchanged from BEFORE \u2014 "
                "reassigning inside the function never touched Object A.",
            out="x AFTER grow_number: 5", main_var=mv, func_var=None)
        add(11, "main1() has no more lines left either, so it ends too. The "
                 "program is finished!",
            jump='return', main_var=mv, func_var=None)

        return code_lines, frames

    def build_reassign_frames():
        code_lines = [
            'def grow_list(nums):',                                # 1
            '    nums = [8, 3]',                                    # 2
            '    nums.append(10)',                                   # 3
            '    nums.append(7)',                                     # 4
            '    print("nums INSIDE grow_list:", nums)',              # 5
            '',                                                        # 6
            'def main2():',                                            # 7
            '    nums = [8, 3]',                                        # 8
            '    print("nums BEFORE grow_list:", nums)',                 # 9
            '    grow_list(nums)',                                        # 10
            '    print("nums AFTER grow_list:", nums)',                    # 11
            '',                                                             # 12
            'main2()',                                                      # 13
        ]

        frames = []
        seen = set()

        def add(line, msg, jump='normal', out=None, main_var=None, func_var=None):
            seen.add(line)
            frames.append({
                'active': line, 'executed': set(seen), 'msg': msg, 'jump': jump,
                'out': out, 'main_var': main_var, 'func_var': func_var,
            })

        add(1, "Python finds def grow_list(nums). The function is registered, "
                "nothing inside it runs yet.")
        add(7, "Python finds def main2(). Same idea \u2014 defined and ready, "
                "not run yet.")
        add(13, "Python reaches the last line, main2(). This CALL is where real "
                 "execution actually begins.")
        add(7, "Execution jumps into main2(), starting at line 7.", jump='call')

        obj_a = [8, 3]
        mv = {'name': 'nums (main2)', 'value': str(obj_a), 'tag': 'A'}
        add(8, "Line 8 runs: nums is set to a new list [8, 3]. Call this "
                "Object A.",
            main_var=mv)
        add(9, "Line 9 prints nums before the call \u2014 remember this value "
                "to compare it to the value AFTER.",
            out="nums BEFORE grow_list: [8, 3]", main_var=mv)
        add(10, "Line 10 calls grow_list(nums). Python is about to jump into "
                 "that function, passing a REFERENCE to Object A \u2014 not a "
                 "copy of the list!",
            main_var=mv)

        fv = {'name': 'nums (grow_list)', 'value': str(obj_a), 'tag': 'A'}
        add(1, "Execution jumps into grow_list(). The parameter nums now points "
                "to the SAME list as main2's nums \u2014 Object A. Right now, "
                "they're linked.",
            jump='call', main_var=mv, func_var=fv)

        obj_b = [8, 3]
        fv = {'name': 'nums (grow_list)', 'value': str(obj_b), 'tag': 'B'}
        add(2, "Line 2 runs: nums is REASSIGNED to a brand-new list [8, 3] \u2014 "
                "call it Object B. This rebinds the local nums and BREAKS its "
                "link to Object A. main2's nums still points to Object A and "
                "knows nothing about this new list.",
            main_var=mv, func_var=fv)

        obj_b.append(10)
        fv = {'name': 'nums (grow_list)', 'value': str(obj_b), 'tag': 'B'}
        add(3, "Line 3 runs: append() mutates Object B directly \u2014 no new "
                "object this time, just new contents. But Object B still isn't "
                "connected to main2's list at all.",
            main_var=mv, func_var=fv)

        obj_b.append(7)
        fv = {'name': 'nums (grow_list)', 'value': str(obj_b), 'tag': 'B'}
        add(4, "Line 4 runs: another append() on Object B.",
            main_var=mv, func_var=fv)
        add(5, "Line 5 prints Object B's contents from inside the function.",
            out=f"nums INSIDE grow_list: {obj_b}", main_var=mv, func_var=fv)

        add(11, "grow_list() has no more lines, so it ends. Its local nums "
                 "(Object B) is discarded entirely. Execution returns to line "
                 "11, right after the call.",
            jump='return', main_var=mv, func_var=None)
        add(11, "Line 11 runs: print(...). Notice the value is UNCHANGED from "
                 "BEFORE! We appended to Object B, never to Object A \u2014 "
                 "main2's original list was never touched.",
            out=f"nums AFTER grow_list: {obj_a}", main_var=mv, func_var=None)
        add(13, "main2() finishes. The whole program is done.",
            jump='return', main_var=mv, func_var=None)

        return code_lines, frames

    def build_inplace_frames():
        code_lines = [
            'def grow_list_inplace(nums):',                          # 1
            '    nums.append(10)',                                    # 2
            '    nums.append(7)',                                      # 3
            '    print("nums INSIDE grow_list_inplace:", nums)',        # 4
            '',                                                          # 5
            'def main3():',                                              # 6
            '    nums = [8, 3]',                                          # 7
            '    print("nums BEFORE grow_list_inplace:", nums)',           # 8
            '    grow_list_inplace(nums)',                                 # 9
            '    print("nums AFTER grow_list_inplace:", nums)',            # 10
            '',                                                            # 11
            'main3()',                                                     # 12
        ]

        frames = []
        seen = set()

        def add(line, msg, jump='normal', out=None, main_var=None, func_var=None):
            seen.add(line)
            frames.append({
                'active': line, 'executed': set(seen), 'msg': msg, 'jump': jump,
                'out': out, 'main_var': main_var, 'func_var': func_var,
            })

        add(1, "Python finds def grow_list_inplace(nums). Registered, not run "
                "yet.")
        add(6, "Python finds def main3(). Registered, not run yet.")
        add(12, "Python reaches the last line, main3(). This CALL is where real "
                 "execution begins.")
        add(6, "Execution jumps into main3(), starting at line 6.", jump='call')

        obj_a = [8, 3]
        mv = {'name': 'nums (main3)', 'value': str(obj_a), 'tag': 'A'}
        add(7, "Line 7 runs: nums = [8, 3] creates Object A.", main_var=mv)
        add(8, "Line 8 prints nums before the call.",
            out="nums BEFORE grow_list_inplace: [8, 3]", main_var=mv)
        add(9, "Line 9 calls grow_list_inplace(nums) \u2014 about to jump in, "
                "passing a reference to Object A.",
            main_var=mv)

        fv = {'name': 'nums (grow_list_inplace)', 'value': str(obj_a), 'tag': 'A'}
        add(1, "Execution jumps in. This time the function does NOT reassign "
                "nums \u2014 both variables will point to Object A the entire "
                "time.",
            jump='call', main_var=mv, func_var=fv)

        obj_a.append(10)
        mv = {'name': 'nums (main3)', 'value': str(obj_a), 'tag': 'A'}
        fv = {'name': 'nums (grow_list_inplace)', 'value': str(obj_a), 'tag': 'A'}
        add(2, "Line 2 runs: append() mutates Object A directly. Because both "
                "nums variables refer to the SAME object, this change is "
                "visible through both of them at once.",
            main_var=mv, func_var=fv)

        obj_a.append(7)
        mv = {'name': 'nums (main3)', 'value': str(obj_a), 'tag': 'A'}
        fv = {'name': 'nums (grow_list_inplace)', 'value': str(obj_a), 'tag': 'A'}
        add(3, "Line 3 runs: another in-place append() on the shared Object A.",
            main_var=mv, func_var=fv)
        add(4, "Line 4 prints Object A's contents from inside the function.",
            out=f"nums INSIDE grow_list_inplace: {obj_a}", main_var=mv, func_var=fv)

        add(10, "grow_list_inplace() ends. Unlike the reassignment example, "
                 "there's no separate local object to throw away \u2014 nums "
                 "was always Object A, main3's own list.",
            jump='return', main_var=mv, func_var=None)
        add(10, "Line 10 runs: print(...). This time the value HAS changed "
                 "from BEFORE, because the function mutated the very same "
                 "object main3's nums points to, instead of creating a new "
                 "one.",
            out=f"nums AFTER grow_list_inplace: {obj_a}", main_var=mv, func_var=None)
        add(12, "main3() finishes. Program done.", jump='return',
            main_var=mv, func_var=None)

        return code_lines, frames

    EXAMPLES = {
        'Immutable: int (grow_number)': {
            'builder': build_immutable_frames,
            'main_empty': 'x (main1) \u2014 not created yet',
            'func_empty': 'x (grow_number) \u2014 function not running',
        },
        'Mutable + reassign (grow_list, the pitfall)': {
            'builder': build_reassign_frames,
            'main_empty': 'nums (main2) \u2014 not created yet',
            'func_empty': 'nums (grow_list) \u2014 function not running',
        },
        'Mutable + direct mutation (grow_list_inplace)': {
            'builder': build_inplace_frames,
            'main_empty': 'nums (main3) \u2014 not created yet',
            'func_empty': 'nums (grow_list_inplace) \u2014 function not running',
        },
    }

    # ------------------------------------------------------------------ #
    # The widget
    # ------------------------------------------------------------------ #

    class MutabilityVisualizer:
        def __init__(self):
            self.example_radio = widgets.RadioButtons(
                options=list(EXAMPLES.keys()),
                value=list(EXAMPLES.keys())[0],
                description='Example:',
                layout=widgets.Layout(width='420px'),
            )
            self.mode_radio = widgets.RadioButtons(
                options=['Automatic', 'Manual'],
                value='Automatic',
                description='Playback:',
                layout=widgets.Layout(width='260px'),
            )

            self.run_btn = widgets.Button(description='Run', button_style='success')
            self.reset_btn = widgets.Button(description='Reset')
            self.back_btn = widgets.Button(description='\u2190 Back', disabled=True)
            self.next_btn = widgets.Button(description='Next \u2192', disabled=True)
            self.output = widgets.Output()

            self.run_btn.on_click(self.run_program)
            self.reset_btn.on_click(self.reset_program)
            self.back_btn.on_click(self.go_back)
            self.next_btn.on_click(self.go_next)
            self.mode_radio.observe(self.on_mode_change, names='value')
            self.example_radio.observe(self.on_example_change, names='value')

            self.nav_box = widgets.HBox([self.back_btn, self.next_btn])
            self.nav_box.layout.display = 'none'

            self.container = widgets.VBox([
                widgets.HTML('<h3 style="margin:0 0 6px 0;">Mutability vs. Immutability \u2014 Code Flow</h3>'),
                widgets.HTML(
                    '<p style="margin:0 0 8px 0;color:#334155;">'
                    'Watch what happens to a variable BEFORE and AFTER it is passed into '
                    'a function. The Memory View below the code shows whether two variables '
                    'share the same object (a real mutation is visible everywhere) or point '
                    'to different objects (a reassignment stays local).'
                    '</p>'
                ),
                self.example_radio,
                self.mode_radio,
                widgets.HBox([self.run_btn, self.reset_btn]),
                self.nav_box,
                self.output,
            ])

            self.frames = []
            self.frame_index = -1
            self.code_lines = []
            self.render_start()

        def current_config(self):
            return EXAMPLES[self.example_radio.value]

        def on_mode_change(self, change):
            self.nav_box.layout.display = '' if change['new'] == 'Manual' else 'none'

        def on_example_change(self, change):
            self.render_start()

        def render_start(self):
            cfg = self.current_config()
            self.code_lines, _frames = cfg['builder']()
            self.frames = []
            self.frame_index = -1
            self.update_nav_buttons()
            with self.output:
                clear_output()
                display(HTML(render_code(self.code_lines, active_line=1, executed=set(),
                                          title='Not started yet')))
                display(HTML(render_explanation(
                    "Python always starts reading a file from the very top, line 1 \u2014 "
                    "that's where the arrow begins. Click Run to watch it move."
                )))
                display(HTML(render_memory(None, None, cfg['main_empty'], cfg['func_empty'])))
                display(HTML(render_output_console([])))

        def update_nav_buttons(self):
            self.back_btn.disabled = (self.frame_index <= 0)
            self.next_btn.disabled = (
                self.frame_index < 0 or self.frame_index >= len(self.frames) - 1
            )

        def display_index(self, idx):
            cfg = self.current_config()
            idx = max(0, min(idx, len(self.frames) - 1))
            self.frame_index = idx
            f = self.frames[idx]
            printed_so_far = [ff['out'] for ff in self.frames[:idx + 1] if ff['out']]
            with self.output:
                clear_output(wait=True)
                display(HTML(render_code(self.code_lines, active_line=f['active'],
                                          executed=f['executed'], title='Running\u2026',
                                          jump_type=f['jump'])))
                display(HTML(render_explanation(f['msg'], f['jump'], idx + 1, len(self.frames))))
                display(HTML(render_memory(f['main_var'], f['func_var'],
                                            cfg['main_empty'], cfg['func_empty'])))
                display(HTML(render_output_console(printed_so_far)))
                if idx == len(self.frames) - 1:
                    display(HTML(
                        "<p style='margin:8px 0 0 0;color:#065f46;font-weight:700;"
                        "font-family:monospace;'>Done \u2014 try another example or run it again!</p>"
                    ))

        def go_back(self, _):
            if self.frames:
                self.display_index(self.frame_index - 1)
                self.update_nav_buttons()

        def go_next(self, _):
            if self.frames:
                self.display_index(self.frame_index + 1)
                self.update_nav_buttons()

        def reset_program(self, _):
            self.render_start()

        def run_program(self, _):
            cfg = self.current_config()
            self.code_lines, frames = cfg['builder']()
            self.frames = frames
            self.frame_index = 0

            if self.mode_radio.value == 'Automatic':
                self.back_btn.disabled = True
                self.next_btn.disabled = True
                for i in range(len(frames)):
                    self.display_index(i)
                    time.sleep(1.5)
            else:
                self.display_index(0)
                self.update_nav_buttons()

    viz = MutabilityVisualizer()
    display(viz.container)
