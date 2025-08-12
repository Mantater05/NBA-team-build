from nba_api.stats.endpoints import CommonPlayerInfo
from requests.exceptions import ReadTimeout, ConnectionError
import sqlite3
import time
import os

DB_NAME = "nba_info.db"
SKIPPED_FILE = "skipped_players.txt"

def fetch_player(player_id, cursor, db, player_table):
    for attempt in range(3):
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
            is_active = next(iter([p[1] for p in player_table if p[0] == player_id]), "Unknown")

            cursor.execute('''
                INSERT OR IGNORE INTO Players (
                    player_id, full_name, jersey_num, team_name, team_ab, pos, height, weight, country, is_active
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
            ''', (player_id, player_name, player_num, team_name, team_ab, position, height, weight, country, is_active))
            db.commit()
            return True

        except (ReadTimeout, ConnectionError) as e:
            wait_time = 2 ** attempt
            print(f"Retrying {player_id} in {wait_time} seconds due to error: {e}")
            time.sleep(wait_time)

        except Exception as e:
            print(f"Failed to fetch {player_id} due to unexpected error: {e}")
            break

    return False

def main():
    # Load skipped players
    try:
        with open(SKIPPED_FILE, "r") as f:
            skipped_players = [int(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        print("No skipped_players.txt found.")
        return

    if not skipped_players:
        print("No players to retry.")
        return

    # Connect to DB
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()

    # Get minimal player_table so we can get 'is_active' info
    cursor.execute("SELECT player_id, is_active FROM Players")
    player_table = cursor.fetchall()

    # Keep track of players that still fail
    still_failed = []

    for pid in skipped_players:
        print(f"Retrying player {pid}...")
        success = fetch_player(pid, cursor, db, player_table)
        if success:
            print(f"Successfully added {pid}")
        else:
            print(f"Still failed to add {pid}")
            still_failed.append(pid)

    db.close()

    # Update skipped_players.txt with only the ones that failed again
    if still_failed:
        with open(SKIPPED_FILE, "w") as f:
            f.write("\n".join(str(pid) for pid in still_failed))
        print(f"Updated {SKIPPED_FILE} with {len(still_failed)} remaining players.")
    else:
        if os.path.exists(SKIPPED_FILE):
            os.remove(SKIPPED_FILE)
        print("All skipped players processed successfully. File removed.")

if __name__ == "__main__":
    main()
