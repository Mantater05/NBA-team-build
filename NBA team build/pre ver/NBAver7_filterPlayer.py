import tkinter as tk
from tkinter import ttk
from NBADataCollector import NBADataCollector

class PlayerDisplayApp:
    def __init__(self, root, page_size=10):
        self.root = root
        self.root.title("NBA Player Display")

        self.collector = NBADataCollector()
        self.page_size = page_size
        self.original_player_list = [player for player in self.collector.get_player_info_db() if player is not None]  # Ensure valid data
        self.player_list = self.original_player_list[:]  # Copy for filtering
        self.total_players = len(self.player_list)
        self.total_pages = (self.total_players + self.page_size - 1) // self.page_size
        self.current_page = 0

        # Fetch unique teams and countries
        self.teams = [team[3] for team in self.collector.get_team_info_db()]  # Assuming this method fetches teams
        self.positions = ["Guard", "Center", "Forward"]
        self.countries = sorted(set(player[8] for player in self.original_player_list if player[8]))

        # Create the filter and table
        self.create_filter_section()
        self.create_table()

        # Create navigation buttons
        self.create_navigation()

    def create_filter_section(self):
        # Create a frame for the filter section
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(pady=10)

        # Name filter
        ttk.Label(filter_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(filter_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Team filter (Dropdown)
        ttk.Label(filter_frame, text="Team:").grid(row=0, column=2, padx=5, pady=5)
        self.team_var = tk.StringVar()
        self.team_dropdown = ttk.Combobox(filter_frame, textvariable=self.team_var, values=["All"] + self.teams, state="readonly")
        self.team_dropdown.grid(row=0, column=3, padx=5, pady=5)
        self.team_dropdown.current(0)  # Default to "All"

        # Position filter (Dropdown)
        ttk.Label(filter_frame, text="Position:").grid(row=0, column=4, padx=5, pady=5)
        self.position_var = tk.StringVar()
        self.position_dropdown = ttk.Combobox(filter_frame, textvariable=self.position_var, values=["All"] + self.positions, state="readonly")
        self.position_dropdown.grid(row=0, column=5, padx=5, pady=5)
        self.position_dropdown.current(0)  # Default to "All"

        # Country filter (Dropdown)
        ttk.Label(filter_frame, text="Country:").grid(row=0, column=6, padx=5, pady=5)
        self.country_var = tk.StringVar()
        self.country_dropdown = ttk.Combobox(filter_frame, textvariable=self.country_var, values=["All"] + self.countries, state="readonly")
        self.country_dropdown.grid(row=0, column=7, padx=5, pady=5)
        self.country_dropdown.current(0)  # Default to "All"

        # Active filter (Checkbox)
        self.active_var = tk.BooleanVar()
        self.active_checkbox = ttk.Checkbutton(filter_frame, text="Active Only", variable=self.active_var)
        self.active_checkbox.grid(row=0, column=8, padx=5, pady=5)

        # Filter button
        self.filter_button = ttk.Button(filter_frame, text="Filter", command=self.apply_filter)
        self.filter_button.grid(row=0, column=9, padx=5, pady=5)

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

    def apply_filter(self):
        # Get filter values
        name_filter = self.name_entry.get().strip().lower()
        team_filter = self.team_var.get()
        position_filter = self.position_var.get()
        country_filter = self.country_var.get()
        active_filter = self.active_var.get()

        # Find the team abbreviation for the selected team
        team_ab = None
        if team_filter != "All":
            for team in self.collector.get_team_info_db():
                if team[3] == team_filter:  # Match the selected team nickname
                    team_ab = team[2]  # Get the team abbreviation
                    break
        
        active_stat = None
        if active_filter:
            active_stat = "Active"
        else:
            active_stat = "Not Active"

        # Filter the player list
        self.player_list = [
            player for player in self.original_player_list
            if (player[1].lower().startswith(name_filter) if name_filter else True) and
            (team_ab is None or player[4] == team_ab) and
            (position_filter == "All" or position_filter.lower() in player[5].lower()) and
            (country_filter == "All" or country_filter == player[8]) and
            (player[9] == active_stat)
        ]
        
        # Update pagination and table
        self.total_players = len(self.player_list)
        self.total_pages = (self.total_players + self.page_size - 1) // self.page_size
        self.current_page = 0
        self.update_table()
        self.update_navigation()

    def update_table(self):
        # Get the players for the current page
        start_index = self.current_page * self.page_size
        end_index = start_index + self.page_size
        current_page_players = self.player_list[start_index:end_index]

        # Update the table with the current page players
        for i, player in enumerate(current_page_players):
            self.data_labels[i][0]['text'] = player[0]  # Player ID
            self.data_labels[i][1]['text'] = player[1]  # Player Name
            self.data_labels[i][2]['text'] = player[2]  # Player Number
            self.data_labels[i][3]['text'] = player[4]  # Team
            self.data_labels[i][4]['text'] = player[5]  # Position
            self.data_labels[i][5]['text'] = player[6]  # Height
            self.data_labels[i][6]['text'] = f"{player[7]} lbs"  # Weight
            self.data_labels[i][7]['text'] = player[8]  # Country
            self.data_labels[i][8]['text'] = player[9]  # Active?

        # Clear the remaining rows (if fewer players than page size)
        for i in range(len(current_page_players), self.page_size):
            for label in self.data_labels[i]:
                label['text'] = ""

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
