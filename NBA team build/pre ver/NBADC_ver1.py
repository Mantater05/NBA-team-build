# Import necessary libraries
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import CommonPlayerInfo
import sqlite3

class NBADataCollector:
    def __init__(self, db_name='nba_info.db'):
        # Initialize the NBADataCollector with a database connection
        self.db_name = db_name
        self.db = sqlite3.connect(self.db_name)
        self.cursor = self.db.cursor()
        self.player_table = []
        self.team_table = []

    def get_all_players_api(self):
        # Retrieve all NBA players from the nba_api
        return players.get_players()

    def get_all_teams_api(self):
        # Retrieve all NBA teams from the nba_api
        return teams.get_teams()

    def player_exists(self, player_id):
        """Check if a player already exists in the database."""
        self.cursor.execute("SELECT COUNT(*) FROM Players WHERE player_id = ?", (player_id,))
        return self.cursor.fetchone()[0] > 0

    def team_exists(self, team_id):
        """Check if a team already exists in the database."""
        self.cursor.execute("SELECT COUNT(*) FROM Teams WHERE team_id = ?", (team_id,))
        return self.cursor.fetchone()[0] > 0

    def add_player_to_db(self, 
                         player_id, 
                         player_name, 
                         player_num, 
                         team_name, 
                         team_ab, 
                         position, 
                         height, 
                         weight, 
                         country, 
                         is_active):
        
        # Add player information to the database if not already present
        if not self.player_exists(player_id):
            insert = '''
                INSERT INTO Players (
                    player_id, 
                    full_name, 
                    jersey_num, 
                    team_name, 
                    team_ab, 
                    pos, 
                    height, 
                    weight, 
                    country, 
                    is_active
                )
                VALUES (?,?,?,?,?,?,?,?,?,?)
            '''
            try:
                self.cursor.execute(insert, 
                    [
                        player_id,
                        player_name, 
                        player_num, 
                        team_name, 
                        team_ab, 
                        position, 
                        height, 
                        weight, 
                        country, 
                        is_active
                    ]
                ) 
                self.db.commit()
            except sqlite3.IntegrityError:
                pass

    def add_teams_to_db(self):
        # Add team information to the database if not already present
        for team in self.team_table:
            if not self.team_exists(team[0]):  # team[0] is the team_id
                insert = '''
                    INSERT INTO Teams (
                        team_id, 
                        team_name, 
                        team_ab, 
                        team_nickname, 
                        city, 
                        state, 
                        year_founded
                    )
                    VALUES (?,?,?,?,?,?,?)
                '''
                try:
                    self.cursor.execute(insert, 
                        [
                            team[0],
                            team[1], 
                            team[2], 
                            team[3], 
                            team[4], 
                            team[5], 
                            team[6]
                        ]
                    ) 
                    self.db.commit()
                except sqlite3.IntegrityError:
                    pass

    def get_player_id_api(self):
        # Extract player IDs into a list
        return [player[0] for player in self.player_table]

    def get_player_info_api(self, player_ids):
        # Fetch detailed information for each player ID
        for player_id in player_ids:
            print(f"Fetching info for player ID: {player_id}")
            player_info = CommonPlayerInfo(player_id=player_id)
            player_info_df = player_info.get_data_frames()[0]

            # Extracting specific information from the DataFrame
            player_name = player_info_df.at[0, 'DISPLAY_FIRST_LAST']
            player_num = player_info_df.at[0, 'JERSEY']
            team_name = player_info_df.at[0, 'TEAM_NAME']
            team_ab = player_info_df.at[0, 'TEAM_ABBREVIATION']
            position = player_info_df.at[0, 'POSITION']
            height = player_info_df.at[0, 'HEIGHT']
            weight = player_info_df.at[0, 'WEIGHT']
            country = player_info_df.at[0, 'COUNTRY']
            is_active = next(iter([player[1] for player in self.player_table if player[0] == player_id]))

            self.add_player_to_db(player_id, player_name, player_num, team_name, team_ab, position, height, weight, country, is_active)

    def collect_data(self):
        # Main method to collect NBA player and team data
        all_nba_players = self.get_all_players_api()
        all_nba_teams = self.get_all_teams_api()

        # Create a table with NBA player information
        self.player_table = [
            [player['id'], 'Active' if player['is_active'] else 'Not Active']
            for player in all_nba_players
        ]

        # Create a table with NBA team information
        self.team_table = [
            [team['id'], team['full_name'], team['abbreviation'], team['nickname'], team['city'], team['state'], team['year_founded']]
            for team in all_nba_teams
        ]

        player_ids = self.get_player_id_api()
        self.get_player_info_api(player_ids)
        self.add_teams_to_db()
        print('Data collection completed.')

    def get_player_info_db(self):
        fetch = 'SELECT * FROM Players'
        self.cursor.execute(fetch)
        return self.cursor.fetchall()

    def get_team_info_db(self):
        fetch = 'SELECT * FROM Teams ORDER BY team_nickname'
        self.cursor.execute(fetch)
        return self.cursor.fetchall()

    def close(self):
        # Close the database connection
        self.db.close()

def main():
    collector = NBADataCollector()
    collector.collect_data()
    collector.close()

if __name__ == "__main__":
    main()