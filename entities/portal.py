import pygame
import math
import random

class Portal:
    def __init__(self, x, y, width=200, height=300):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_time = 0
        self.active = False
        self.alpha = 255  # 透明度
        self.particles = []  # 粒子效果
        self.fade_out = False  # 是否正在淡出
        self.fade_speed = 2  # 淡出速度
        self.move_speed = 3  # 传送门移动速度
        self.triggered = False  # 是否已经触发传送效果
        
    def reset(self):
        """重置传送门状态"""
        self.animation_time = 0
        self.active = False
        self.alpha = 0  # 初始时完全透明
        self.particles = []
        self.fade_out = False
        self.triggered = False
        
    def activate(self):
        """激活传送门"""
        self.active = True
        self.animation_time = 0
        self.alpha = 255
        self.particles = []
        self.fade_out = False
        self.triggered = False
        
    def deactivate(self):
        """开始传送门的淡出效果"""
        self.fade_out = True
        
    def update(self, game_speed=3):
        """更新传送门动画和位置"""
        if not self.active:
            return
            
        # 更新传送门位置（向左移动）
        if not self.triggered:
            self.x -= self.move_speed * game_speed
            
        self.animation_time += 1
        
        # 处理淡出效果
        if self.fade_out:
            self.alpha = max(0, self.alpha - self.fade_speed)
            if self.alpha == 0:
                self.active = False
                self.fade_out = False
                self.triggered = False
                return
        
        # 生成新的粒子
        if self.animation_time % 2 == 0:
            # 增加粒子数量
            for _ in range(5):
                particle_x = self.x + self.width/2 + random.randint(-50, 50)
                particle_y = self.y + random.randint(0, self.height)
                self.particles.append({
                    'x': particle_x,
                    'y': particle_y,
                    'life': 45,
                    'speed': random.uniform(-2, 2),
                    'color': (
                        random.randint(100, 255),
                        random.randint(100, 255),
                        random.randint(200, 255)
                    )
                })
            
        # 更新现有粒子
        for particle in self.particles[:]:
            particle['life'] -= 1
            particle['x'] += particle['speed']  # 应用水平移动
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
    def draw(self, screen):
        """绘制传送门"""
        if not self.active:
            return
            
        # 绘制传送门主体
        portal_surface = pygame.Surface((self.width + 120, self.height + 120), pygame.SRCALPHA)
        
        # 计算波浪效果
        wave_offset = math.sin(self.animation_time * 0.1) * 25
        
        # 绘制外部光晕效果
        for i in range(8):
            alpha = max(0, self.alpha - i * 40)
            size_mult = 1 + i * 0.3
            rect = pygame.Rect(
                (self.width + 120) * (1 - size_mult) / 2 + wave_offset,
                (self.height + 120) * (1 - size_mult) / 2,
                (self.width + 120) * size_mult,
                (self.height + 120) * size_mult
            )
            color = (100 + i * 20, 150 + i * 10, 255, alpha)
            pygame.draw.ellipse(portal_surface, color, rect)
            
        # 绘制传送门的中心
        center_color = (200, 220, 255, self.alpha)
        pygame.draw.ellipse(portal_surface, center_color,
                          (wave_offset + 60, 60, self.width, self.height))
                          
        # 绘制能量波纹
        for i in range(4):
            wave_phase = (self.animation_time * 0.2 + i * math.pi / 2) % (math.pi * 2)
            wave_size = math.sin(wave_phase) * 40
            wave_alpha = int((1 - wave_phase / (math.pi * 2)) * self.alpha)
            wave_color = (150, 200, 255, wave_alpha)
            wave_rect = pygame.Rect(
                wave_offset + 60 - wave_size/2,
                60 - wave_size/2,
                self.width + wave_size,
                self.height + wave_size
            )
            pygame.draw.ellipse(portal_surface, wave_color, wave_rect, 3)
                          
        # 绘制粒子
        for particle in self.particles:
            alpha = int((particle['life'] / 45) * self.alpha)
            size = int((particle['life'] / 45) * 8)
            color = (*particle['color'], alpha)
            pygame.draw.circle(portal_surface, color,
                             (particle['x'] - self.x + 60, particle['y'] - self.y + 60), size)
            
        
        screen.blit(portal_surface, (self.x - 30, self.y - 60))
        
    def get_rect(self):
        """获取传送门的碰撞区域"""
        return pygame.Rect(self.x, self.y, self.width, self.height) 