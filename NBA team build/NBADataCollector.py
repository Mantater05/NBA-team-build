import os
import time
import random
import sqlite3
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import CommonPlayerInfo
from requests.exceptions import ReadTimeout, ConnectionError


class NBADataCollector:
    def __init__(self, db_name='nba_info.db', skipped_file="skipped_players.txt"):
        # Database
        self.db_name = db_name
        self.db = sqlite3.connect(self.db_name)
        self.cursor = self.db.cursor()

        # Player/team storage
        self.player_table = []
        self.team_table = []

        # Retry/skipped player tracking
        self.skipped_file = skipped_file
        self.skipped_players = set(self._load_skipped_players())

    # -----------------------
    # Skipped player handling
    # -----------------------
    def _load_skipped_players(self):
        if os.path.exists(self.skipped_file):
            with open(self.skipped_file, "r") as f:
                return [int(line.strip()) for line in f if line.strip().isdigit()]
        return []

    def _save_skipped_players(self):
        if self.skipped_players:
            with open(self.skipped_file, "w") as f:
                for pid in sorted(self.skipped_players):
                    f.write(f"{pid}\n")
        elif os.path.exists(self.skipped_file):
            os.remove(self.skipped_file)

    def _mark_player_success(self, player_id):
        if player_id in self.skipped_players:
            self.skipped_players.remove(player_id)
            self._save_skipped_players()

    def _mark_player_failed(self, player_id):
        self.skipped_players.add(player_id)
        self._save_skipped_players()

    # -----------------------
    # Database checks/inserts
    # -----------------------
    def player_exists(self, player_id):
        self.cursor.execute("SELECT COUNT(*) FROM Players WHERE player_id = ?", (player_id,))
        return self.cursor.fetchone()[0] > 0

    def team_exists(self, team_id):
        self.cursor.execute("SELECT COUNT(*) FROM Teams WHERE team_id = ?", (team_id,))
        return self.cursor.fetchone()[0] > 0

    def add_player_to_db(self, player_id, player_name, player_num, team_name, team_ab,
                         position, height, weight, country, is_active):
        if not self.player_exists(player_id):
            insert = '''
                INSERT INTO Players (
                    player_id, full_name, jersey_num, team_name, team_ab,
                    pos, height, weight, country, is_active
                )
                VALUES (?,?,?,?,?,?,?,?,?,?)
            '''
            try:
                self.cursor.execute(insert, [
                    player_id, player_name, player_num, team_name, team_ab,
                    position, height, weight, country, is_active
                ])
                self.db.commit()
            except sqlite3.IntegrityError:
                pass

    def add_teams_to_db(self):
        for team in self.team_table:
            if not self.team_exists(team[0]):
                insert = '''
                    INSERT INTO Teams (
                        team_id, team_name, team_ab, team_nickname,
                        city, state, year_founded
                    )
                    VALUES (?,?,?,?,?,?,?)
                '''
                try:
                    self.cursor.execute(insert, team)
                    self.db.commit()
                except sqlite3.IntegrityError:
                    pass

    # -----------------------
    # API data retrieval
    # -----------------------
    def get_all_players_api(self):
        return players.get_players()

    def get_all_teams_api(self):
        return teams.get_teams()

    def get_player_id_api(self):
        return [player[0] for player in self.player_table]

    def fetch_and_save_player(self, player_id, max_retries=3, retry_delay_range=(2, 5)):
        """Fetch a single player's info and save to DB, with retry."""
        for attempt in range(1, max_retries + 1):
            print(f"Fetching info for player ID: {player_id} (Attempt {attempt})")
            try:
                player_info = CommonPlayerInfo(player_id=player_id, timeout=60)
                df = player_info.get_data_frames()[0]

                player_name = df.at[0, 'DISPLAY_FIRST_LAST']
                player_num = df.at[0, 'JERSEY']
                team_name = df.at[0, 'TEAM_NAME']
                team_ab = df.at[0, 'TEAM_ABBREVIATION']
                position = df.at[0, 'POSITION']
                height = df.at[0, 'HEIGHT']
                weight = df.at[0, 'WEIGHT']
                country = df.at[0, 'COUNTRY']
                is_active = next(iter([p[1] for p in self.player_table if p[0] == player_id]), "Unknown")

                self.add_player_to_db(player_id, player_name, player_num, team_name,
                                    team_ab, position, height, weight, country, is_active)

                self._mark_player_success(player_id)
                time.sleep(0.5)  # small delay to prevent rate limit
                return True

            except (ReadTimeout, ConnectionError) as e:
                print(f"[Attempt {attempt}/{max_retries}] Timeout for player {player_id}: {e}")
                if attempt < max_retries:
                    time.sleep(random.uniform(*retry_delay_range))
            except Exception as e:
                print(f"Unexpected error for player {player_id}: {e}")
                break  # unknown error, don't retry

        self._mark_player_failed(player_id)
        print(f"Skipping player {player_id} after {max_retries} failed attempts.")
        return False

    # -----------------------
    # Main collection logic
    # -----------------------
    def get_player_info_api(self, player_ids):
        for pid in player_ids:
            self.fetch_and_save_player(pid)

    def retry_skipped_players_until_done(self):
        """Keep retrying skipped players until the file is gone."""
        while self.skipped_players:
            print(f"Retrying {len(self.skipped_players)} skipped players...")
            for pid in list(self.skipped_players):
                self.fetch_and_save_player(pid)
            if not self.skipped_players:
                print("All skipped players processed!")

    def collect_data(self):
        # Load from API
        all_nba_players = self.get_all_players_api()
        all_nba_teams = self.get_all_teams_api()

        self.player_table = [[p['id'], 'Active' if p['is_active'] else 'Not Active']
                             for p in all_nba_players]
        self.team_table = [[t['id'], t['full_name'], t['abbreviation'], t['nickname'],
                            t['city'], t['state'], t['year_founded']]
                           for t in all_nba_teams]

        # Add players & teams
        self.get_player_info_api(self.get_player_id_api())
        self.retry_skipped_players_until_done()
        self.add_teams_to_db()
        print('Data collection completed.')

    # -----------------------
    # Utility
    # -----------------------
    def get_player_info_db(self):
        self.cursor.execute('SELECT * FROM Players')
        return self.cursor.fetchall()

    def get_team_info_db(self):
        self.cursor.execute('SELECT * FROM Teams ORDER BY team_nickname')
        return self.cursor.fetchall()

    def close(self):
        self.db.close()


def main():
    collector = NBADataCollector()
    collector.collect_data()
    collector.close()


if __name__ == "__main__":
    main()
