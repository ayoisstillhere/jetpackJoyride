class DifficultySystem:
    def __init__(self):
        self.reset()

    def reset(self):
        """reset difficulty system"""
        """Reset the difficulty system"""
        self.difficulty_level = 1
        self.game_speed = 3  # Initial speed
        self.last_distance = 0  # Distance at last difficulty update
        self.distance_per_level = 500  # Increase difficulty every 500 meters

    def update(self, current_distance):
        """Update difficulty based on current distance

        Args:
            current_distance (float): Current distance traveled

        Returns:
            bool: difficulty changed
            bool: Whether the difficulty has changed
        """
        # update game speed (faster speed growth)
        # Update game speed (faster speed increase)
        if current_distance < 50000:
            self.game_speed = 3 + (current_distance // 500) / 5  # every 500m, increase 0.2 speed
            self.game_speed = 3 + (current_distance // 500) / 5  # Increase speed by 0.2 every 500 meters
        else:
            self.game_speed = 13  # Max speed

        # Calculate new difficulty level
        new_level = int(current_distance // self.distance_per_level) + 1
        if new_level != self.difficulty_level:
            self.difficulty_level = new_level
            self.last_distance = current_distance
            return True
        return False

    def get_current_theme(self):
        """Return the theme based on the current difficulty level"""
        if self.difficulty_level <= 3:
            return "space"
        elif self.difficulty_level <= 6:
            return "another-world"
        elif self.difficulty_level <= 9:
            return "land"
        elif self.difficulty_level <= 12:
            return "forest"
        else:
            return "mountain"

    def get_obstacle_frequency(self):
        """Return the obstacle spawn frequency for the current difficulty

        Returns:
            dict: contains the generation interval of various obstacles (frames)
            dict: Contains spawn intervals (in frames) for each obstacle type
        """
        # with increasing difficulty, the generation interval decreases (generate more frequently)
        # As difficulty increases, spawn intervals decrease (more frequent obstacles)
        return {
            'rocket': max(200 - self.difficulty_level * 15, 100),  # Rocket spawn interval: 200->100 frames
            'laser': max(300 - self.difficulty_level * 20, 120)    # Laser spawn interval: 300->120 frames
        }