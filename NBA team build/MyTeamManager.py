import tkinter as tk
from tkinter import ttk

class MyTeamManager:
    def __init__(self, app):
        self.app = app
        self.my_team_window = None  # This will hold the MyTeam window

    def show_my_team(self):
        """Show the MyTeam window with the list of players."""
        if self.my_team_window is None or not self.my_team_window.winfo_exists():
            self.my_team_window = tk.Toplevel(self.app.root)
            self.my_team_window.title("MyTeam")

            # Create the header row
            header = ["Player ID", "Player", "Number", "Team", "Position", "Height", "Weight", "Country", "Active?", "Remove"]
            for col, title in enumerate(header):
                label = ttk.Label(self.my_team_window, text=title, font=('Arial', 10, 'bold'))
                label.grid(row=0, column=col, padx=5, pady=5)

        self.refresh_display()

    def refresh_display(self):
        """Refresh the display of players in the 'MyTeam' window."""
        # Clear any existing rows from the MyTeam display
        for widget in self.my_team_window.winfo_children():
            if isinstance(widget, ttk.Label) or isinstance(widget, ttk.Button):
                if widget.grid_info()["row"] > 0:  # Don't remove the header row
                    widget.destroy()

        if len(self.app.my_team) == 0:
            # Display a message indicating the team is empty
            empty_label = ttk.Label(self.my_team_window, text="Your MyTeam is empty.", font=('Arial', 12, 'italic'), foreground="red")
            empty_label.grid(row=1, column=0, columnspan=10, padx=5, pady=10)
        else:
            # Render each player in "MyTeam"
            for row, player in enumerate(self.app.my_team):
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

    def remove_from_my_team(self, player):
        """Remove a player from 'MyTeam'."""
        if player in self.app.my_team:
            self.app.my_team.remove(player)
            self.refresh_display()  # Refresh the display after removing the player
