class DifficultySystem:
    def __init__(self):
        # 基础游戏参数
        self.base_game_speed = 3
        self.speed_multiplier = 1.0
        self.difficulty_level = 1
        self.game_speed = self.base_game_speed
        
        # 难度调整参数
        self.last_speed_increase = 0
        self.distance_per_level = 1000  # 每1000米提升一次难度
        self.speed_increase_rate = 0.2  # 每次提升速度20%
        
        # 主题变化阈值
        self.theme_thresholds = {
            "forest": (1, 3),    # 1-3级
            "night": (4, 6),     # 4-6级
            "desert": (7, 9),    # 7-9级
            "snow": (10, float('inf'))  # 10级以上
        }
        
    def update(self, current_distance):
        """根据当前距离更新难度"""
        if current_distance - self.last_speed_increase >= self.distance_per_level:
            self.last_speed_increase = current_distance
            self.increase_difficulty()
            return True
        return False
            
    def increase_difficulty(self):
        """提升游戏难度"""
        self.difficulty_level += 1
        self.speed_multiplier += self.speed_increase_rate
        self.game_speed = self.base_game_speed * self.speed_multiplier
        print(f"难度提升！当前等级：{self.difficulty_level}，速度倍数：{self.speed_multiplier:.1f}")
        
    def get_current_theme(self):
        """根据当前难度等级返回对应的主题"""
        for theme, (min_level, max_level) in self.theme_thresholds.items():
            if min_level <= self.difficulty_level <= max_level:
                return theme
        return "snow"  # 默认返回雪地主题
        
    def get_obstacle_frequency(self):
        """返回当前难度下的障碍物生成频率"""
        return {
            'rocket': max(180 - self.difficulty_level * 10, 120),  # 火箭生成间隔
            'spike': max(120 - self.difficulty_level * 5, 60)      # 尖刺生成间隔
        }
        
    def reset(self):
        """重置难度系统"""
        self.speed_multiplier = 1.0
        self.difficulty_level = 1
        self.game_speed = self.base_game_speed
        self.last_speed_increase = 0 