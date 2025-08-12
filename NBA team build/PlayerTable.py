import tkinter as tk
from tkinter import ttk

class PlayerTable:
    def __init__(self, app, root, page_size=10):
        self.app = app
        self.page_size = page_size
        self.current_page = 0

        self.frame = ttk.Frame(root)
        self.frame.pack(pady=10)

        self.data_labels = []
        self.add_buttons = []

        # Create table
        self._create_header()
        self._create_rows()
        self.update_table(self.app.player_list[:self.page_size])

    def _create_header(self):
        header = ["Player ID", "Player", "Number", "Team", "Position", "Height", "Weight", "Country", "Active?", "Add"]
        for col, title in enumerate(header):
            label = ttk.Label(self.frame, text=title, font=('Arial', 10, 'bold'))
            label.grid(row=0, column=col, padx=5, pady=5)

    def _create_rows(self):
        for row in range(self.page_size):
            row_labels = []
            for col in range(10):  # 10 columns
                label = ttk.Label(self.frame, text="")
                label.grid(row=row + 1, column=col, padx=5, pady=5)
                row_labels.append(label)
            self.data_labels.append(row_labels)

            # Add the "+ Add" button for each row
            add_button = ttk.Button(self.frame, text="+", command=lambda r=row: self.app.add_to_my_team(r), width=3)
            add_button.grid(row=row + 1, column=9, padx=5, pady=5)
            self.add_buttons.append(add_button)

    def update_table(self, current_page_players):
        for i, playerinfo in enumerate(current_page_players):
            self.data_labels[i][0]['text'] = playerinfo[0]  # Player ID
            self.data_labels[i][1]['text'] = playerinfo[1]  # Player Name
            self.data_labels[i][2]['text'] = playerinfo[2]  # Player Number
            self.data_labels[i][3]['text'] = playerinfo[4]  # Team
            self.data_labels[i][4]['text'] = playerinfo[5]  # Position
            self.data_labels[i][5]['text'] = playerinfo[6]  # Height
            self.data_labels[i][6]['text'] = f"{playerinfo[7]} lbs"  # Weight
            self.data_labels[i][7]['text'] = playerinfo[8]  # Country
            self.data_labels[i][8]['text'] = playerinfo[9]  # Active?

        # Clear extra rows
        for i in range(len(current_page_players), self.page_size):
            for label in self.data_labels[i]:
                label['text'] = ""
            self.add_buttons[i].grid_forget()
