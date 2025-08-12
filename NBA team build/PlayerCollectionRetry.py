import os
import time
import random
from nba_api.stats.endpoints import CommonPlayerInfo
from requests.exceptions import ReadTimeout, ConnectionError

class PlayerCollectionRetry:
    def __init__(self, skipped_file="skipped_players.txt", max_retries=3, retry_delay_range=(2, 5)):
        self.skipped_file = skipped_file
        self.max_retries = max_retries
        self.retry_delay_range = retry_delay_range
        self.skipped_players = set(self._load_skipped_players())  # no duplicates

    def _load_skipped_players(self):
        if os.path.exists(self.skipped_file):
            with open(self.skipped_file, "r") as f:
                return [int(line.strip()) for line in f if line.strip().isdigit()]
        return []

    def save_skipped_players(self):
        if self.skipped_players:
            with open(self.skipped_file, "w") as f:
                for pid in sorted(self.skipped_players):
                    f.write(f"{pid}\n")
        elif os.path.exists(self.skipped_file):
            os.remove(self.skipped_file)

    def attempt_player_fetch(self, player_id, fetch_func):
        for attempt in range(1, self.max_retries + 1):
            try:
                result = fetch_func(player_id)
                if result:
                    self.mark_player_success(player_id)
                return result
            except Exception as e:
                print(f"[Retry {attempt}/{self.max_retries}] Player {player_id} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(random.uniform(*self.retry_delay_range))
        self.skipped_players.add(player_id)
        self.save_skipped_players()
        return None

    def mark_player_success(self, player_id):
        if player_id in self.skipped_players:
            self.skipped_players.remove(player_id)
            self.save_skipped_players()

    def run_until_empty(self, fetch_func):
        while self.skipped_players:
            for pid in list(self.skipped_players):
                fetch_func(pid)
            if not self.skipped_players:
                print("✅ All skipped players processed.")
