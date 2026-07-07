def main():
    from IPython.display import display, clear_output, HTML
    import ipywidgets as widgets
    import time
    import html

    # A compact Colab-friendly code tracer.
    # Paste into Colab and run the final cell.

    CODE_LINES = [
        'def showWeather():',                                          # 1
        '    weather = int(input("What is the temperature? "))',       # 2
        '    if weather > 80:',                                        # 3
        '        print("It seems hot!")',                              # 4
        '    else:',                                                   # 5
        '        print("Nice weather!")',                              # 6
        '',                                                            # 7
        'def main():',                                                 # 8
        '    print("Welcome to the weather checker!")',                # 9
        '    showWeather()',                                           # 10
        '    print("Thanks for using the weather checker!")',          # 11
        '',                                                            # 12
        'main()',                                                      # 13
    ]

    # Visual language for each kind of "step":
    #   normal -> plain execution of a line
    #   call   -> execution is jumping INTO a function
    #   return -> execution is jumping BACK out of a function
    ARROW = {'normal': '\u279c', 'call': '\u21b4', 'return': '\u21a9'}
    LINE_BG = {
        'normal': ('#fef08a', '#111827'),
        'call':   ('#bfdbfe', '#1e3a8a'),
        'return': ('#ddd6fe', '#4c1d95'),
    }

    def render_code(active_line=None, executed=None, title='Weather Checker.py', jump_type='normal'):
        executed = executed or set()
        rows = []

        for i, line in enumerate(CODE_LINES, start=1):
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

    class CodeFlowVisualizer:
        def __init__(self):
            self.temp = widgets.IntSlider(
                value=75,
                min=0,
                max=120,
                step=1,
                description='Temp:',
                continuous_update=False,
                layout=widgets.Layout(width='320px'),
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

            self.nav_box = widgets.HBox([self.back_btn, self.next_btn])
            self.nav_box.layout.display = 'none'  # hidden until Manual mode is selected

            self.container = widgets.VBox([
                widgets.HTML('<h3 style="margin:0 0 6px 0;">Weather Checker \u2014 Code Flow</h3>'),
                widgets.HTML(
                    '<p style="margin:0 0 8px 0;color:#334155;">'
                    'Watch Python execute this program one line at a time. '
                    'The arrow shows exactly where Python is right now, and the '
                    'output panel fills in live as <code>print()</code> statements run. '
                    'Choose Automatic to watch it play out, or Manual to step through '
                    'it yourself with Back / Next.'
                    '</p>'
                ),
                self.temp,
                self.mode_radio,
                widgets.HBox([self.run_btn, self.reset_btn]),
                self.nav_box,
                self.output,
            ])

            self.printed = []
            self.frames = []
            self.frame_index = -1
            self.render_start()

        def on_mode_change(self, change):
            self.nav_box.layout.display = '' if change['new'] == 'Manual' else 'none'

        def render_start(self):
            self.printed = []
            self.frames = []
            self.frame_index = -1
            self.update_nav_buttons()
            with self.output:
                clear_output()
                display(HTML(render_code(active_line=1, executed=set(), title='Not started yet')))
                display(HTML(render_explanation(
                    "Python always starts reading a file from the very top, line 1 \u2014 "
                    "that's where the arrow begins. Click Run to watch it move."
                )))
                display(HTML(render_output_console([])))

        def update_nav_buttons(self):
            self.back_btn.disabled = (self.frame_index <= 0)
            self.next_btn.disabled = (
                self.frame_index < 0 or self.frame_index >= len(self.frames) - 1
            )

        def display_index(self, idx):
            idx = max(0, min(idx, len(self.frames) - 1))
            self.frame_index = idx
            f = self.frames[idx]
            printed_so_far = [ff['out'] for ff in self.frames[:idx + 1] if ff['out']]
            with self.output:
                clear_output(wait=True)
                display(HTML(render_code(active_line=f['active'], executed=f['executed'],
                                          title='Running\u2026', jump_type=f['jump'])))
                display(HTML(render_explanation(f['msg'], f['jump'], idx + 1, len(self.frames))))
                display(HTML(render_output_console(printed_so_far)))
                if idx == len(self.frames) - 1:
                    display(HTML(
                        "<p style='margin:8px 0 0 0;color:#065f46;font-weight:700;"
                        "font-family:monospace;'>Done \u2014 try a different temperature and run it again!</p>"
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
            weather = self.temp.value
            hot = weather > 80

            frames = []
            seen = set()

            def add(line, msg, jump='normal', out=None):
                seen.add(line)
                frames.append({
                    'active': line,
                    'executed': set(seen),
                    'msg': msg,
                    'jump': jump,
                    'out': out,
                })

            # --- Phase 1: Python reads the top-level function definitions first ---
            add(1, "Python finds \"def showWeather():\". This registers the function "
                    "and remembers its code, but it does NOT run the code inside yet.")
            add(8, "Python finds \"def main():\". Same idea \u2014 main() is now defined "
                    "and ready to be called later, but its body hasn't run yet either.")

            # --- Phase 2: the call at the bottom kicks off real execution ---------
            add(13, "Python reaches the last line, \"main()\". This is a function CALL "
                     "\u2014 this is the moment real execution actually begins.")
            add(8, "Execution jumps into main(). We start at its very first line, line 8.",
                jump='call')
            add(9, "Line 9 runs: print(...). Whatever is inside the parentheses gets "
                    "sent straight to the output panel below, in real time.",
                out="Welcome to the weather checker!")
            add(10, "Line 10 calls showWeather(). Just like before, Python is about "
                     "to jump into that function's code.")
            add(1, "Execution jumps into showWeather(), starting at its first line, line 1.",
                jump='call')
            add(2, f"Line 2 runs: weather is set to {weather} \u2014 the value from your slider.")
            add(3, f"Line 3 checks the condition: weather > 80, which is {hot}.")

            if hot:
                add(4, "The condition was True, so Python runs the if-branch and prints "
                        "its message.",
                    out="It seems hot!")
                last_body_line = 4
            else:
                add(5, "The condition was False, so Python skips the if-branch entirely "
                        "and moves to the else-branch.")
                add(6, "Line 6 runs the else-branch's print(...).",
                    out="Nice weather!")
                last_body_line = 6

            add(11, "showWeather() has no more lines left, so it ends. Execution jumps "
                     "BACK to main() \u2014 right after the line that called it, line 11.",
                jump='return')
            add(11, "Line 11 runs: print(...).",
                out="Thanks for using the weather checker!")
            add(13, "main() has no more lines left either, so it ends too. The program "
                     "is finished!",
                jump='return')

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

    viz = CodeFlowVisualizer()
    display(viz.container)
