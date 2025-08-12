import tkinter as tk
from tkinter import ttk
from NBADataCollector import NBADataCollector
from FilterSection import FilterSection
from PlayerTable import PlayerTable
from MyTeamManager import MyTeamManager

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
        self.filter_section = FilterSection(self, root)
        self.player_table = PlayerTable(self, root)
        self.my_team_manager = MyTeamManager(self)

        # Create navigation buttons
        self.create_navigation()

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
        name_filter = self.filter_section.name_entry.get().strip().lower()
        team_filter = self.filter_section.team_var.get()
        position_filter = self.filter_section.position_var.get()
        country_filter = self.filter_section.country_var.get()
        active_filter = self.filter_section.active_var.get()

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
        self.my_team_manager.refresh_display()

    def show_my_team(self):
        self.my_team_manager.show_my_team()

    def remove_from_my_team(self, player):
        self.my_team.remove(player)
        self.my_team_manager.refresh_display()

    def update_table(self):
        start_index = self.current_page * self.page_size
        end_index = start_index + self.page_size
        current_page_players = self.player_list[start_index:end_index]
        self.player_table.update_table(current_page_players)

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