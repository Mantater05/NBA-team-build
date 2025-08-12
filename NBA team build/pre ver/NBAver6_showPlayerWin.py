import tkinter as tk
from tkinter import ttk
from NBADataCollector import NBADataCollector

class PlayerDisplayApp:
    def __init__(self, root, page_size=10):
        self.root = root
        self.root.title("NBA Player Display")

        self.collector = NBADataCollector()
        self.page_size = page_size
        self.player_list = [player for player in self.collector.get_player_info_db() if player is not None]  # Ensure valid data
        self.total_players = len(self.player_list)
        self.total_pages = (self.total_players + self.page_size - 1) // self.page_size
        self.current_page = 0

        # Create the table
        self.create_table()

        # Create navigation buttons
        self.create_navigation()

    def create_table(self):
        # Create a frame for the table
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.pack(pady=10)

        # Create the header row
        header = ["Player ID", "Player", "Number", "Team", "Position", "Height", "Weight", "Country", "Active?"]
        for col, title in enumerate(header):
            label = ttk.Label(self.table_frame, text=title, font=('Arial', 10, 'bold'))
            label.grid(row=0, column=col, padx=5, pady=5)

        # Create the data rows
        self.data_labels = []
        for row in range(self.page_size):
            row_labels = []
            for col in range(len(header)):
                label = ttk.Label(self.table_frame, text="")
                label.grid(row=row + 1, column=col, padx=5, pady=5)
                row_labels.append(label)
            self.data_labels.append(row_labels)

        self.update_table()

    def create_navigation(self):
        # Create navigation buttons
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(pady=10)

        self.prev_button = ttk.Button(nav_frame, text="<", command=self.previous_page)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = ttk.Button(nav_frame, text=">", command=self.next_page)
        self.next_button.grid(row=0, column=1, padx=5)

        self.update_navigation()

    def update_table(self):
        # Get the players for the current page
        start_index = self.current_page * self.page_size
        current_page_players = []
        index = start_index

        while len(current_page_players) < self.page_size and index < self.total_players:
            player = self.player_list[index]
            if player:  # Skip if the player data is invalid or missing
                current_page_players.append(player)
            index += 1

        # Update the table with the current page players
        for i in range(self.page_size):
            if i < len(current_page_players):
                player = current_page_players[i]
                self.data_labels[i][0]['text'] = player[0]  # Player ID
                self.data_labels[i][1]['text'] = player[1]  # Player Name
                self.data_labels[i][2]['text'] = player[2]  # Player Number
                self.data_labels[i][3]['text'] = player[4]  # Team
                self.data_labels[i][4]['text'] = player[5]  # Position
                self.data_labels[i][5]['text'] = player[6]  # Height
                self.data_labels[i][6]['text'] = f"{player[7]} lbs"  # Weight
                self.data_labels[i][7]['text'] = player[8]  # Country
                self.data_labels[i][8]['text'] = player[9]  # Active?
            else:
                for j in range(9):
                    self.data_labels[i][j]['text'] = ""

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()
            self.update_navigation()

    def next_page(self):
        if (self.current_page + 1) * self.page_size < self.total_players:
            self.current_page += 1
            self.update_table()
            self.update_navigation()

    def update_navigation(self):
        # Disable buttons if at the boundaries
        self.prev_button['state'] = 'normal' if self.current_page > 0 else 'disabled'
        self.next_button['state'] = 'normal' if (self.current_page + 1) * self.page_size < self.total_players else 'disabled'

if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerDisplayApp(root)
    root.mainloop()
