class DifficultySystem:
    def __init__(self):
        self.reset()
        
    def reset(self):
        """reset difficulty system"""
        self.difficulty_level = 1
        self.game_speed = 2  # initial speed
        self.last_distance = 0  # last update difficulty distance
        self.distance_per_level = 500  # every 500m, update difficulty
        
    def update(self, current_distance):
        """according to the current distance, update difficulty
        
        Args:
            current_distance (float): current distance
            
        Returns:
            bool: difficulty changed
        """
        # update game speed (faster speed growth)
        if current_distance < 50000:
            self.game_speed = 3 + (current_distance // 500) / 5  # every 500m, increase 0.2 speed
        else:
            self.game_speed = 13  # max speed
            
        # calculate new difficulty level
        new_level = int(current_distance // self.distance_per_level) + 1
        if new_level != self.difficulty_level:
            self.difficulty_level = new_level
            self.last_distance = current_distance
            return True
        return False
        
    # def get_current_theme(self):
    #     """根据当前难度等级返回对应的主题"""
    #     if self.difficulty_level <= 3:
    #         return "space"
    #     elif self.difficulty_level <= 6:
    #         return "another-world"
    #     elif self.difficulty_level <= 9:
    #         return "land"
    #     elif self.difficulty_level <= 12:
    #         return "forest"
    #     else:
    #         return "mountain"
            
    def get_obstacle_frequency(self):
        """return the obstacle generation frequency of the current difficulty
        
        Returns:
            dict: contains the generation interval of various obstacles (frames)
        """
        # with increasing difficulty, the generation interval decreases (generate more frequently)
        return {
            'rocket': max(200 - self.difficulty_level * 15, 100),  # rocket generation interval: 200->100 frames
            'laser': max(300 - self.difficulty_level * 20, 120)    # laser generation interval: 300->120 frames
        } 