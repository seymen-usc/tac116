def main():
    from IPython.display import display, clear_output, HTML
    import ipywidgets as widgets
    import time
    import html
    
    # A compact Colab-friendly code tracer.
    # Paste into Colab and run the final cell.
    
    CODE_LINES = [
        'def showWeather():',
        '    weather = int(input("What is the temperature? "))',
        '    if weather > 80:',
        '        print("It seems hot!")',
        '    else:',
        '        print("Nice weather!")',
        '',
        'def main():',
        '    print("Welcome to the weather checker!")',
        '    showWeather()',
        '    print("Thanks for using the weather checker!")',
        '',
        'main()',
    ]
    
    
    def render_code(active_line=None, executed=None, title='Weather Checker.py'):
        executed = executed or set()
        rows = []
    
        for i, line in enumerate(CODE_LINES, start=1):
            escaped = html.escape(line) if line else '&nbsp;'
            is_active = i == active_line
            is_done = i in executed and not is_active
    
            if is_active:
                style = (
                    'background:#fef08a;'
                    'color:#111827;'
                    'font-weight:700;'
                    'border-radius:4px;'
                )
                arrow = '➜'
            elif is_done:
                style = 'background:#dcfce7;color:#111827;border-radius:4px;'
                arrow = ' '
            else:
                style = 'color:#64748b;'
                arrow = ' '
    
            rows.append(
                f"<span style='display:block;white-space:pre;line-height:1.05;padding:0 2px;{style}'>{arrow} {i:>2} | {escaped}</span>"
            )
    
        return f"""
        <div style='border:1px solid #cbd5e1;border-radius:10px;background:#f8fafc;padding:6px 8px;'>
          <div style='font-family:monospace;font-size:12px;font-weight:700;color:#0f172a;margin-bottom:4px;'>{html.escape(title)}</div>
          <div style='font-family:monospace;font-size:12px;line-height:1.05;'>{''.join(rows)}</div>
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
    
            self.run_btn = widgets.Button(description='Run', button_style='success')
            self.reset_btn = widgets.Button(description='Reset')
            self.output = widgets.Output()
    
            self.run_btn.on_click(self.run_program)
            self.reset_btn.on_click(self.reset_program)
    
            self.container = widgets.VBox([
                widgets.HTML('<h3 style="margin:0 0 6px 0;">Weather Checker Code Flow</h3>'),
                widgets.HTML('<p style="margin:0 0 8px 0;">Click Run to step through the code. The active line gets the arrow and highlight.</p>'),
                self.temp,
                widgets.HBox([self.run_btn, self.reset_btn]),
                self.output,
            ])
    
            self.render_start()
    
        def render_start(self):
            with self.output:
                clear_output()
                display(HTML(render_code(active_line=13, executed={13}, title='Ready')))
                display(HTML('<p style="margin:8px 0 0 0;color:#475569;font-family:monospace;">Press Run to animate.</p>'))
    
        def show_frame(self, active_line, executed, message=''):
            with self.output:
                clear_output(wait=True)
                display(HTML(render_code(active_line=active_line, executed=executed, title='Running')))
                if message:
                    display(HTML(
                        f"<div style='margin-top:6px;padding:6px 8px;border:1px solid #e2e8f0;border-radius:8px;background:#ffffff;font-family:monospace;font-size:12px;'>{html.escape(message)}</div>"
                    ))
    
        def reset_program(self, _):
            self.render_start()
    
        def run_program(self, _):
            weather = self.temp.value
    
            frames = [
                (8, {8}, 'main() starts'),
                (9, {8, 9}, 'print("Welcome to the weather checker!")'),
                (10, {8, 9, 10}, 'showWeather() is called'),
                (1, {8, 9, 10, 1}, 'showWeather() begins'),
                (2, {8, 9, 10, 1, 2}, f'weather = {weather}'),
                (3, {8, 9, 10, 1, 2, 3}, f'if weather > 80 -> {weather > 80}'),
            ]
    
            if weather > 80:
                frames.append((4, {8, 9, 10, 1, 2, 3, 4}, 'print("It seems hot!")'))
                done_line = 4
            else:
                frames.append((5, {8, 9, 10, 1, 2, 3, 5}, 'else branch selected'))
                frames.append((6, {8, 9, 10, 1, 2, 3, 5, 6}, 'print("Nice weather!")'))
                done_line = 6
    
            frames.extend([
                (11, {8, 9, 10, 1, 2, 3, done_line, 11}, 'showWeather() ends'),
                (12, {8, 9, 10, 1, 2, 3, done_line, 11, 12}, 'print("Thanks for using the weather checker!")'),
                (13, {8, 9, 10, 1, 2, 3, done_line, 11, 12, 13}, 'Program finished'),
            ])
    
            for active_line, executed, message in frames:
                self.show_frame(active_line, executed, message)
                time.sleep(1.5)
    
            with self.output:
                display(HTML('<p style="margin:8px 0 0 0;color:#065f46;font-weight:700;font-family:monospace;">Done.</p>'))
    
    
    viz = CodeFlowVisualizer()
    display(viz.container)
