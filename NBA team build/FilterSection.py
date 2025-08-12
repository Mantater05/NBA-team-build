import tkinter as tk
from tkinter import ttk

class FilterSection:
    def __init__(self, app, root):
        self.app = app
        self.frame = ttk.Frame(root)
        self.frame.pack(pady=10)

        self.filters = {}

        # Create filters
        self.name_entry = self._add_entry("Name:", 0)
        self.team_var = self._add_dropdown("Team:", 2, ["All"] + sorted(set(team[3] for team in app.collector.get_team_info_db())))
        self.position_var = self._add_dropdown("Position:", 4, ["All", "Guard", "Center", "Forward"])
        self.country_var = self._add_dropdown("Country:", 6, ["All"] + sorted(set(player[8] for player in app.original_player_list if player[8])))
        self.active_var = tk.BooleanVar()
        self.active_checkbox = ttk.Checkbutton(self.frame, text="Active Only", variable=self.active_var)
        self.active_checkbox.grid(row=0, column=8, padx=5, pady=5)

        # Filter button
        self.filter_button = ttk.Button(self.frame, text="Filter", command=self._apply_filter)
        self.filter_button.grid(row=0, column=9, padx=5, pady=5)

    def _add_entry(self, label_text, col):
        ttk.Label(self.frame, text=label_text).grid(row=0, column=col, padx=5, pady=5)
        entry = ttk.Entry(self.frame)
        entry.grid(row=0, column=col + 1, padx=5, pady=5)
        return entry

    def _add_dropdown(self, label_text, col, values):
        ttk.Label(self.frame, text=label_text).grid(row=0, column=col, padx=5, pady=5)
        var = tk.StringVar()
        dropdown = ttk.Combobox(self.frame, textvariable=var, values=values, state="readonly")
        dropdown.grid(row=0, column=col + 1, padx=5, pady=5)
        dropdown.current(0)
        return var

    def _apply_filter(self):
        self.filters = {
            'name': self.name_entry.get(),
            'team': self.team_var.get(),
            'position': self.position_var.get(),
            'country': self.country_var.get(),
            'active': self.active_var.get()
        }
        self.app.apply_filter()
