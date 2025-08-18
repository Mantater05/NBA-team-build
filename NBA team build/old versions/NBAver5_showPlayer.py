from NBADataCollector import NBADataCollector
from tabulate import tabulate

class PlayerDisplay:
    def __init__(self, page_size=10):
        self.collector = NBADataCollector()
        self.page_size = page_size
        self.player_list = [player for player in self.collector.get_player_info_db() if player is not None]  # Ensure valid data
        self.total_players = len(self.player_list)
        self.total_pages = (self.total_players + self.page_size - 1) // self.page_size  # Calculate total pages
        self.current_page = 0

    def display_players(self):
        while True:
            # Fetch 10 players for the current page, ignoring gaps in IDs
            start_index = self.current_page * self.page_size
            current_page_players = []
            index = start_index

            while len(current_page_players) < self.page_size and index < self.total_players:
                player = self.player_list[index]
                if player:  # Skip if the player data is invalid or missing
                    current_page_players.append(player)
                index += 1

            # Prepare data for tabulation
            table_data = []
            for player in current_page_players:
                table_data.append([
                    player[0],  # player_id
                    player[1],  # player_name
                    player[2],  # player_num
                    player[4],  # team_ab
                    player[5],  # position
                    player[6],  # height
                    f"{player[7]} lbs",  # weight
                    player[8],  # country
                    player[9]   # is_active
                ])

            # Display players for the current page in a tabular format
            print(tabulate(table_data, headers=[
                "Player ID", "Player", "Number", "Team", "Position", "Height", "Weight", 
                "Country", "Active?"
            ], tablefmt="pretty"))

            # Navigation controls
            if self.current_page < self.total_pages - 1:
                user_input = input("\nPress 'n' for next page, 'p' for previous page, or 'q' to quit: ").strip().lower()
                if user_input == 'n':
                    self.current_page += 1
                elif user_input == 'p' and self.current_page > 0:
                    self.current_page -= 1
                elif user_input == 'q':
                    print("Exiting...")
                    break
                else:
                    print("Invalid input. Please try again.")
            else:
                print("You are on the last page.")
                user_input = input("\nPress 'p' for previous page or 'q' to quit: ").strip().lower()
                if user_input == 'p' and self.current_page > 0:
                    self.current_page -= 1
                elif user_input == 'q':
                    print("Exiting...")
                    break


def main():
    player_display = PlayerDisplay()
    player_display.display_players()

if __name__ == "__main__":
    main()
