import os

class StyleManager:
    def __init__(self, theme: str = "dark"):
        self.theme = theme

    def get_stylesheet(self):
        icon_color = "#FFFFFF" if self.theme == "dark" else "#000000"
        base_style = {
            "light": {
                "background": "#F5F5F5", "color": "#333", "group_bg": "#FFFFFF", "group_border": "#DDD",
                "tab_bg": "#E5E5E5", "tab_selected": "#2563EB", "tab_hover": "#D1D5DB",
                "input_bg": "#FFFFFF", "input_border": "#CCC", "progress_bg": "#E5E5E5",
                "table_bg": "#FFFFFF", "table_border": "#DDD", "scroll_bg": "#F5F5F5", "scroll_handle": "#A0A0A0"
            },
            "dark": {
                "background": "#1E1E1E", "color": "#E0E0E0", "group_bg": "#252526", "group_border": "#333",
                "tab_bg": "#2B2B2B", "tab_selected": "#2563EB", "tab_hover": "#3A3A3B",
                "input_bg": "#2B2B2B", "input_border": "#444", "progress_bg": "#2B2B2B",
                "table_bg": "#1A1A1A", "table_border": "#333", "scroll_bg": "#252526", "scroll_handle": "#4B5563"
            }
        }[self.theme]

        dropdown_open_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons", "dropdown_open.svg").replace('\\', '/')
        dropdown_close_icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons", "dropdown_close.svg").replace('\\', '/')

        return f"""
            QWidget {{ font-family: Arial; font-size: 13px; background: {base_style['background']}; color: {base_style['color']}; }}
            QGroupBox {{ background: {base_style['group_bg']}; border: 1px solid {base_style['group_border']}; border-radius: 8px; padding: 12px; }}
            QPushButton {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #60A5FA, stop:1 #2563EB); color: {icon_color}; padding: 8px 16px; border-radius: 8px; border: none; }}
            QPushButton:hover {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #93C5FD, stop:1 #1D4ED8); }}
            QPushButton:disabled {{ background: {'#555' if self.theme == 'dark' else '#A0A0A0'}; }}
            QLineEdit, QTextEdit, QDoubleSpinBox, QSpinBox {{ background: {base_style['input_bg']}; color: {base_style['color']}; border: 1px solid {base_style['input_border']}; border-radius: 6px; padding: 6px; }}
            QComboBox {{ background: {base_style['input_bg']}; color: {base_style['color']}; border: 1px solid {base_style['input_border']}; border-radius: 6px; padding: 6px; }}
            QComboBox::drop-down {{ width: 20px; border: none; }}
            QComboBox::down-arrow {{ image: url({dropdown_close_icon}); width: 16px; height: 16px; }}
            QComboBox::down-arrow:on {{ image: url({dropdown_open_icon}); }}
            QTableView {{ background: {base_style['table_bg']}; border: 1px solid {base_style['table_border']}; border-radius: 6px; }}
            QProgressBar {{ background: {base_style['progress_bg']}; border: 1px solid {base_style['input_border']}; border-radius: 6px; text-align: center; color: {base_style['color']}; }}
            QProgressBar::chunk {{ background: #2563EB; border-radius: 6px; }}
        """