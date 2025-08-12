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

        self.my_team = []

        # Fetch unique teams and countries
        self.teams = sorted(set(team[3] for team in self.collector.get_team_info_db()))
        self.positions = ["Guard", "Center", "Forward"]
        self.countries = sorted(set(player[8] for player in self.original_player_list if player[8]))

        # Create the filter and table
        self.create_filter_section()
        self.create_table()

        # Create navigation buttons
        self.create_navigation()

    def create_filter_section(self):
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(pady=10)

        # Name filter
        ttk.Label(filter_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(filter_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Team filter
        ttk.Label(filter_frame, text="Team:").grid(row=0, column=2, padx=5, pady=5)
        self.team_var = tk.StringVar()
        self.team_dropdown = ttk.Combobox(filter_frame, textvariable=self.team_var, values=["All"] + self.teams, state="readonly")
        self.team_dropdown.grid(row=0, column=3, padx=5, pady=5)
        self.team_dropdown.current(0)

        # Position filter
        ttk.Label(filter_frame, text="Position:").grid(row=0, column=4, padx=5, pady=5)
        self.position_var = tk.StringVar()
        self.position_dropdown = ttk.Combobox(filter_frame, textvariable=self.position_var, values=["All"] + self.positions, state="readonly")
        self.position_dropdown.grid(row=0, column=5, padx=5, pady=5)
        self.position_dropdown.current(0)

        # Country filter
        ttk.Label(filter_frame, text="Country:").grid(row=0, column=6, padx=5, pady=5)
        self.country_var = tk.StringVar()
        self.country_dropdown = ttk.Combobox(filter_frame, textvariable=self.country_var, values=["All"] + self.countries, state="readonly")
        self.country_dropdown.grid(row=0, column=7, padx=5, pady=5)
        self.country_dropdown.current(0)

        # Active filter
        self.active_var = tk.BooleanVar()
        self.active_checkbox = ttk.Checkbutton(filter_frame, text="Active Only", variable=self.active_var)
        self.active_checkbox.grid(row=0, column=8, padx=5, pady=5)

        # Filter button
        self.filter_button = ttk.Button(filter_frame, text="Filter", command=self.apply_filter)
        self.filter_button.grid(row=0, column=9, padx=5, pady=5)

    def create_table(self):
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.pack(pady=10)

        # Create the header row
        header = ["Player ID", "Player", "Number", "Team", "Position", "Height", "Weight", "Country", "Active?", "Add to MyTeam"]
        for col, title in enumerate(header):
            label = ttk.Label(self.table_frame, text=title, font=('Arial', 10, 'bold'))
            label.grid(row=0, column=col, padx=5, pady=5)

        self.data_labels = []
        self.add_buttons = []
        for row in range(self.page_size):
            row_labels = []
            for col in range(len(header)):
                label = ttk.Label(self.table_frame, text="")
                label.grid(row=row + 1, column=col, padx=5, pady=5)
                row_labels.append(label)
            self.data_labels.append(row_labels)

            add_button = ttk.Button(self.table_frame, text="+", command=lambda r=row: self.add_to_my_team(r), width=3)
            add_button.grid(row=row + 1, column=len(header) - 1, padx=5, pady=5)
            self.add_buttons.append(add_button)

        self.update_table()

    def create_navigation(self):
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(pady=10)

        self.prev_button = ttk.Button(nav_frame, text="<", command=self.previous_page, width=3)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = ttk.Button(nav_frame, text=">", command=self.next_page, width=3)
        self.next_button.grid(row=0, column=1, padx=5)

        self.my_team_button = ttk.Button(nav_frame, text="MyTeam", command=self.show_my_team)
        self.my_team_button.grid(row=0, column=2, padx=10)

        self.update_navigation()

    def apply_filter(self):
        name_filter = self.name_entry.get().strip().lower()
        team_filter = self.team_var.get()
        position_filter = self.position_var.get()
        country_filter = self.country_var.get()
        active_filter = self.active_var.get()

        team_ab = None
        if team_filter != "All":
            for team in self.collector.get_team_info_db():
                if team[3] == team_filter:
                    team_ab = team[2]
                    break

        self.player_list = [
            player for player in self.original_player_list
            if (name_filter in player[1].lower() if name_filter else True) and
            (team_ab is None or player[4] == team_ab) and
            (position_filter == "All" or position_filter.lower() in player[5].lower()) and
            (country_filter == "All" or player[8] == country_filter) and
            (player[9] == "Active" if active_filter else True)
        ]

        self.total_players = len(self.player_list)
        self.total_pages = (self.total_players + self.page_size - 1) // self.page_size
        self.current_page = 0
        self.update_table()
        self.update_navigation()

    def add_to_my_team(self, row):
        start_index = self.current_page * self.page_size
        player_index = start_index + row
        if player_index < len(self.player_list):
            player = self.player_list[player_index]
            if player not in self.my_team:
                if len(self.my_team) < 5:
                    self.my_team.append(player)
                    print(f"Added to MyTeam: {player[1]}")  # Debugging/logging
                else:
                    print("MyTeam is full. Cannot add more players.")

    def update_my_team_display(self):
        # Clear any existing rows from the MyTeam display
        for widget in self.my_team_window.winfo_children():
            if isinstance(widget, ttk.Label) or isinstance(widget, ttk.Button):
                if widget.grid_info()["row"] > 0:  # Don't remove the header row
                    widget.destroy()

        # Render each player in "MyTeam"
        for row, player in enumerate(self.my_team):
            for col, value in enumerate(player[:10]):  # Display player attributes
                label = ttk.Label(self.my_team_window, text=value)
                label.grid(row=row + 1, column=col, padx=5, pady=5)

            # Add "Remove" button
            remove_button = ttk.Button(
                self.my_team_window,
                text="-",
                command=lambda p=player: self.remove_from_my_team(p),
                width=3
            )
            remove_button.grid(row=row + 1, column=len(player[:10]), padx=5, pady=5)

    def show_my_team(self):
        # Check if the MyTeam window already exists
        if hasattr(self, 'my_team_window') and self.my_team_window.winfo_exists():
            # Bring it to the front and refresh content
            self.my_team_window.lift()
            self.update_my_team_display()
            return

        # Create a new "MyTeam" window
        self.my_team_window = tk.Toplevel(self.root)
        self.my_team_window.title("MyTeam")

        # Add table header
        header = ["Player ID", "Player", "Number", "Team name", "Team ab.", "Position", "Height", "Weight (lbs)", "Country", "Active?", "Remove"]
        for col, title in enumerate(header):
            label = ttk.Label(self.my_team_window, text=title, font=('Arial', 10, 'bold'))
            label.grid(row=0, column=col, padx=5, pady=5)

        # Display players in "MyTeam"
        self.update_my_team_display()

    def remove_from_my_team(self, player):
        # Remove the player from "MyTeam"
        if player in self.my_team:
            self.my_team.remove(player)
            print(f"Removed from MyTeam: {player[1]}")  # Debugging/logging
            self.update_my_team_display()  # Refresh the MyTeam window display

    def update_table(self):
        # Get the players for the current page
        start_index = self.current_page * self.page_size
        end_index = start_index + self.page_size
        current_page_players = self.player_list[start_index:end_index]

        # Update the table with the current page players
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

            # Show the Add button only if there is a player
            self.add_buttons[i].grid(row=i + 1, column=len(self.data_labels[i]), padx=5, pady=5)
            
        # Hide the remaining Add buttons (in case there are fewer players than the page size)
        for i in range(len(current_page_players), self.page_size):
            for label in self.data_labels[i]:
                label['text'] = ""  # Clear remaining player info
            
            # Hide the Add button
            self.add_buttons[i].grid_forget()

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
        self.prev_button['state'] = 'normal' if self.current_page > 0 else 'disabled'
        self.next_button['state'] = 'normal' if (self.current_page + 1) * self.page_size < self.total_players else 'disabled'


if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerDisplayApp(root)
    root.mainloop()
