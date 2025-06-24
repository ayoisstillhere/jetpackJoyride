import os

DATA_FILE = "data/player_info.txt"

class GameState:
    def __init__(self):
        self.paused = False
        self.restart_requested = False

        self.distance: float = 0.0
        self.high_score = 0
        self.lifetime_distance = 0

        self.coin_count = 0
        self.projectiles = []

        self._load_player_data()

    def _load_player_data(self):
        """
        Read high score and lifetime distance from file.
        """
        if not os.path.exists(DATA_FILE):
            self.high_score = 0
            self.lifetime_distance = 0
            return

        with open(DATA_FILE, "r") as f:
            lines = f.readlines()
            self.high_score = int(lines[0].strip())
            self.lifetime_distance = int(lines[1].strip())

    def save_player_data(self):
        """
        Save high score and lifetime distance to file.
        """
        if self.distance > self.high_score:
            self.high_score = self.distance
        self.lifetime_distance += self.distance

        with open(DATA_FILE, "w") as f:
            f.write(f"{int(self.high_score)}\n")
            f.write(f"{int(self.lifetime_distance)}")

    def reset_run(self):
        """
        Reset runtime stats for a new game round.
        """
        self.distance = 0
        self.coin_count = 0
        self.restart_requested = False
        self.paused = False

    def reset(self):
        """
        Reset runtime stats for a new game round.
        Alias for reset_run for compatibility.
        """
        self.reset_run()
