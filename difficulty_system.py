class DifficultySystem:
    def __init__(self):
        self.reset()
        
    def reset(self):
        """重置难度系统"""
        self.difficulty_level = 1
        self.game_speed = 3  # 初始速度
        self.last_distance = 0  # 上次更新难度的距离
        self.distance_per_level = 500  # 每500米提升一次难度
        
    def update(self, current_distance):
        """根据当前距离更新难度
        
        Args:
            current_distance (float): 当前行进距离
            
        Returns:
            bool: 难度是否发生变化
        """
        # 更新游戏速度（更快的速度增长）
        if current_distance < 50000:
            self.game_speed = 3 + (current_distance // 500) / 5  # 每500米增加0.2的速度
        else:
            self.game_speed = 13  # 最大速度
            
        # 计算新的难度等级
        new_level = int(current_distance // self.distance_per_level) + 1
        if new_level != self.difficulty_level:
            self.difficulty_level = new_level
            self.last_distance = current_distance
            return True
        return False
        
    def get_current_theme(self):
        """根据当前难度等级返回对应的主题"""
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
        """返回当前难度下的障碍物生成频率
        
        Returns:
            dict: 包含各种障碍物的生成间隔（帧数）
        """
        # 随难度提升，生成间隔减少（生成更频繁）
        return {
            'rocket': max(200 - self.difficulty_level * 15, 100),  # 火箭生成间隔：200->100帧
            'laser': max(300 - self.difficulty_level * 20, 120)    # 激光生成间隔：300->120帧
        } 