class DifficultySystem:
    def __init__(self, initial_speed=1, distance_per_level=500, max_speed=13):
        """Initialize difficulty system with configurable parameters
        
        Args:
            initial_speed (float): Initial game speed
            distance_per_level (int): Distance required to increase difficulty level
            max_speed (float): Maximum game speed cap
        """
        self.initial_speed = initial_speed
        self.distance_per_level = distance_per_level
        self.max_speed = max_speed
        self.reset()

    def reset(self):
        """Reset the difficulty system"""
        self.difficulty_level = 1
        self.game_speed = self.initial_speed
        self.last_distance = 0

    def update(self, current_distance):
        """Update difficulty based on current distance

        Args:
            current_distance (float): Current distance traveled

        Returns:
            bool: Whether the difficulty has changed
        """
        # Update game speed (faster speed increase)
        if current_distance < 50000:
            self.game_speed = min(
                self.initial_speed + (current_distance // 500) / 8,  # every 500m, increase 0.125 speed
                self.max_speed
            )
        else:
            self.game_speed = self.max_speed

        # Calculate new difficulty level
        new_level = int(current_distance // self.distance_per_level) + 1
        if new_level != self.difficulty_level:
            self.difficulty_level = new_level
            self.last_distance = current_distance
            return True
        return False

    def get_current_theme(self):
        """Return the theme based on the current difficulty level"""
        themes = {
            (1, 3): "space",
            (4, 6): "another-world",
            (7, 9): "land",
            (10, 12): "forest",
            (13, float('inf')): "mountain"
        }
        
        for (min_level, max_level), theme in themes.items():
            if min_level <= self.difficulty_level <= max_level:
                return theme
        return "mountain"  # Default theme

    def get_obstacle_frequency(self):
        """Return the obstacle spawn frequency for the current difficulty

        Returns:
            dict: Contains spawn intervals (in frames) for each obstacle type
        """
        base_intervals = {
            'rocket': 200,
            'laser': 300
        }
        
        min_intervals = {
            'rocket': 100,
            'laser': 120
        }
        
        return {
            obstacle: max(
                base - self.difficulty_level * (15 if obstacle == 'rocket' else 20),
                min_interval
            )
            for (obstacle, base), min_interval in zip(base_intervals.items(), min_intervals.values())
        }