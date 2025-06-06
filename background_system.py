import pygame
import os
import random
from entities.portal import Portal
from config.settings import WIDTH, HEIGHT

class BackgroundSystem:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height

        # 场景切换相关
        self.SCENE_CHANGE_DISTANCE = 2000  # 每2000米切换一次场景
        self.current_distance = 0  # 当前行进距离
        self.background_sequence = ['space', 'another-world', 'land', 'forest', 'mountain']  # 场景切换顺序
        self.current_sequence_index = 0  # 当前场景索引

        # 传送门相关
        self.portal = Portal(WIDTH - 300, HEIGHT//2 - 150)  # 在屏幕右侧中间创建传送门，位置稍微靠左
        self.portal_activation_distance = 200  # 在切换前200米显示传送门
        self.portal_after_effect_distance = 50  # 切换后继续显示50米

        # 主题相关
        self.THEME_SPACE = "space"  # 太空主题
        self.THEME_NATURE = "nature"  # 自然主题
        self.current_theme = self.THEME_SPACE
        self.background_themes = {
            self.THEME_SPACE: {
                'space_layers': {  # 太空层
                    'background': None,
                    'stars': None,
                    'far_planets': None,
                    'ring_planet': None,
                    'big_planet': None
                },
                'another_world': {  # 异世界层
                    'sky': None,
                    'composed': None
                },
                'land': {  # 陆地层
                    'sky': None,
                    'back': None
                }
            },
            self.THEME_NATURE: {
                'forest_layers': {  # 森林层
                    'back_trees': None,
                    'lights': None,
                    'middle_trees': None,
                    'front_trees': None
                },
                'mountain_layers': {  # 山脉层
                    'sky': None,
                    'mountains': None,
                    'far_mountains': None,
                    'trees': None,
                    'foreground_trees': None
                }
            }
        }

        # 视差滚动速度
        self.parallax_speeds = {
            # 太空层速度
            'background': 0.2,
            'stars': 0.3,
            'far_planets': 0.4,
            'ring_planet': 0.6,
            'big_planet': 0.8,
            # 异世界层速度
            'sky': 0.2,
            'composed': 0.4,
            # 陆地层速度
            'back': 0.4,
            # 森林层速度
            'back_trees': 0.2,
            'lights': 0.3,
            'middle_trees': 0.6,
            'front_trees': 0.8,
            # 山脉层速度
            'far_mountains': 0.3,
            'mountains': 0.4,
            'trees': 0.6,
            'foreground_trees': 0.8
        }

        # 图层位置
        self.layer_positions = {
            # 太空层位置
            'background': [0, 0],
            'stars': [0, 0],
            'far_planets': [0, 0],
            'ring_planet': [0, 0],
            'big_planet': [0, 0],
            # 异世界层位置
            'sky': [0, 0],
            'composed': [0, 0],
            # 陆地层位置
            'back': [0, 0],
            # 森林层位置
            'back_trees': [0, 0],
            'lights': [0, 0],
            'middle_trees': [0, 0],
            'front_trees': [0, 0],
            # 山脉层位置
            'far_mountains': [0, 0],
            'mountains': [0, 0],
            'trees': [0, 0],
            'foreground_trees': [0, 0]
        }

        # 当前使用的背景类型
        self.current_background_type = 'space'  # 可选值: 'space', 'another-world', 'land', 'forest', 'mountain'

        # 加载背景
        self.load_background_images()

    def load_background_images(self):
        print("开始加载背景图片...")
        # 加载太空主题的分层背景
        space_folder = os.path.join("backgrounds", "space_background_pack")
        print(f"检查太空背景文件夹: {space_folder}")

        # 加载太空层
        if os.path.exists(space_folder):
            layer_files = {
                'background': os.path.join('layers', 'parallax-space-background.png'),  # 修正拼写错误
                'stars': os.path.join('layers', 'parallax-space-stars.png'),
                'far_planets': os.path.join('layers', 'parallax-space-far-planets.png'),
                'ring_planet': os.path.join('layers', 'parallax-space-ring-planet.png'),
                'big_planet': os.path.join('layers', 'parallax-space-big-planet.png')
            }

            for layer, filename in layer_files.items():
                file_path = os.path.join(space_folder, filename)
                print(f"尝试加载文件: {file_path}")
                if os.path.exists(file_path):
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                        self.background_themes[self.THEME_SPACE]['space_layers'][layer] = img
                        print(f"成功加载太空 {layer} 层: {filename}")
                    except pygame.error as e:
                        print(f"无法加载图片 {file_path}: {e}")
                else:
                    print(f"缺失太空层文件: {file_path}")

            # 加载异世界层
            another_world_folder = os.path.join(space_folder, 'another-world')
            print(f"检查异世界文件夹: {another_world_folder}")
            if os.path.exists(another_world_folder):
                layer_files = {
                    'sky': 'sky.png',
                    'composed': 'composed-bg.png'
                }

                for layer, filename in layer_files.items():
                    file_path = os.path.join(another_world_folder, filename)
                    print(f"尝试加载文件: {file_path}")
                    if os.path.exists(file_path):
                        try:
                            img = pygame.image.load(file_path).convert_alpha()
                            img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                            self.background_themes[self.THEME_SPACE]['another_world'][layer] = img
                            print(f"成功加载异世界 {layer} 层: {filename}")
                        except pygame.error as e:
                            print(f"无法加载图片 {file_path}: {e}")
                    else:
                        print(f"缺失异世界层文件: {file_path}")

            # 加载陆地层
            land_folder = os.path.join(space_folder, 'land')
            print(f"检查陆地文件夹: {land_folder}")
            if os.path.exists(land_folder):
                layer_files = {
                    'sky': 'sky.png',
                    'back': 'back.png'
                }

                for layer, filename in layer_files.items():
                    file_path = os.path.join(land_folder, filename)
                    print(f"尝试加载文件: {file_path}")
                    if os.path.exists(file_path):
                        try:
                            img = pygame.image.load(file_path).convert_alpha()
                            img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                            self.background_themes[self.THEME_SPACE]['land'][layer] = img
                            print(f"成功加载陆地 {layer} 层: {filename}")
                        except pygame.error as e:
                            print(f"无法加载图片 {file_path}: {e}")
                    else:
                        print(f"缺失陆地层文件: {file_path}")
        else:
            print(f"找不到太空背景文件夹: {space_folder}")

        # 加载森林主题的分层背景
        forest_folder = os.path.join("backgrounds", "parallax_forest_pack")
        print(f"检查森林背景文件夹: {forest_folder}")
        if os.path.exists(forest_folder):
            layer_files = {
                'back_trees': os.path.join('layers', 'parallax-forest-back-trees.png'),
                'lights': os.path.join('layers', 'parallax-forest-lights.png'),
                'middle_trees': os.path.join('layers', 'parallax-forest-middle-trees.png'),
                'front_trees': os.path.join('layers', 'parallax-forest-front-trees.png')
            }

            for layer, filename in layer_files.items():
                file_path = os.path.join(forest_folder, filename)
                print(f"尝试加载文件: {file_path}")
                if os.path.exists(file_path):
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                        self.background_themes[self.THEME_NATURE]['forest_layers'][layer] = img
                        print(f"成功加载森林 {layer} 层: {filename}")
                    except pygame.error as e:
                        print(f"无法加载图片 {file_path}: {e}")
                else:
                    print(f"缺失森林层文件: {file_path}")
        else:
            print(f"找不到森林背景文件夹: {forest_folder}")

        # 加载山脉主题的分层背景
        mountain_folder = os.path.join("backgrounds", "parallax_mountain_pack")
        print(f"检查山脉背景文件夹: {mountain_folder}")
        if os.path.exists(mountain_folder):
            layer_files = {
                'sky': os.path.join('layers', 'parallax-mountain-bg.png'),
                'mountains': os.path.join('layers', 'parallax-mountain-mountains.png'),
                'far_mountains': os.path.join('layers', 'parallax-mountain-montain-far.png'),
                'trees': os.path.join('layers', 'parallax-mountain-trees.png'),
                'foreground_trees': os.path.join('layers', 'parallax-mountain-foreground-trees.png')
            }

            for layer, filename in layer_files.items():
                file_path = os.path.join(mountain_folder, filename)
                print(f"尝试加载文件: {file_path}")
                if os.path.exists(file_path):
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                        self.background_themes[self.THEME_NATURE]['mountain_layers'][layer] = img
                        print(f"成功加载山脉 {layer} 层: {filename}")
                    except pygame.error as e:
                        print(f"无法加载图片 {file_path}: {e}")
                else:
                    print(f"缺失山脉层文件: {file_path}")
        else:
            print(f"找不到山脉背景文件夹: {mountain_folder}")

        # 检查是否有任何背景被加载
        if (not any(self.background_themes[self.THEME_SPACE]['space_layers'].values()) and
            not any(self.background_themes[self.THEME_SPACE]['another_world'].values()) and
            not any(self.background_themes[self.THEME_SPACE]['land'].values()) and
            not any(self.background_themes[self.THEME_NATURE]['forest_layers'].values()) and
            not any(self.background_themes[self.THEME_NATURE]['mountain_layers'].values())):
            print("警告：没有成功加载任何背景图片！")
        else:
            print("背景加载完成！")

    def update_layer_positions(self, game_speed):
        if self.current_background_type == 'space':
            layers = ['background', 'stars', 'far_planets', 'ring_planet', 'big_planet']
            theme = self.THEME_SPACE
            layer_dict = 'space_layers'
        elif self.current_background_type == 'another-world':
            layers = ['sky', 'composed']
            theme = self.THEME_SPACE
            layer_dict = 'another_world'
        elif self.current_background_type == 'land':
            layers = ['sky', 'back']
            theme = self.THEME_SPACE
            layer_dict = 'land'
        elif self.current_background_type == 'forest':
            layers = ['back_trees', 'lights', 'middle_trees', 'front_trees']
            theme = self.THEME_NATURE
            layer_dict = 'forest_layers'
        elif self.current_background_type == 'mountain':
            layers = ['sky', 'far_mountains', 'mountains', 'trees', 'foreground_trees']
            theme = self.THEME_NATURE
            layer_dict = 'mountain_layers'
        else:
            return

        for layer in layers:
            if self.background_themes[theme][layer_dict][layer] is not None:
                speed = self.parallax_speeds.get(layer, 0.5) * game_speed
                self.layer_positions[layer][0] -= speed
                if self.layer_positions[layer][0] <= -self.WIDTH:
                    self.layer_positions[layer][0] = 0

    def draw_background(self, screen, pause=False, game_speed=3):
        if pause:
            game_speed = 0

        # 根据当前背景类型选择要绘制的图层
        current_type = self.current_background_type
        if current_type == 'space':
            layers = self.background_themes[self.THEME_SPACE]['space_layers']
        elif current_type == 'another-world':
            layers = self.background_themes[self.THEME_SPACE]['another_world']
        elif current_type == 'land':
            layers = self.background_themes[self.THEME_SPACE]['land']
        elif current_type == 'forest':
            layers = self.background_themes[self.THEME_NATURE]['forest_layers']
        elif current_type == 'mountain':
            layers = self.background_themes[self.THEME_NATURE]['mountain_layers']

        # 绘制每一层
        for layer_name, layer_image in layers.items():
            if layer_image is not None:
                # 获取图层位置
                x = self.layer_positions[layer_name][0]
                y = self.layer_positions[layer_name][1]

                # 绘制主图层
                screen.blit(layer_image, (x, y))

                # 如果图层移出屏幕，在后面绘制一个重复的图层
                if x + layer_image.get_width() < self.WIDTH:
                    screen.blit(layer_image, (x + layer_image.get_width(), y))

                # 如果不是暂停状态，更新图层位置
                if not pause:
                    speed = self.parallax_speeds[layer_name] * game_speed
                    self.layer_positions[layer_name][0] -= speed

                    # 如果图层完全移出屏幕，重置位置
                    if self.layer_positions[layer_name][0] <= -layer_image.get_width():
                        self.layer_positions[layer_name][0] = 0

        # 在最后绘制传送门
        self.portal.draw(screen)

    def change_theme(self, new_theme):
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            if new_theme == self.THEME_SPACE:
                self.current_background_type = random.choice(['space', 'another-world', 'land'])
            else:  # THEME_NATURE
                self.current_background_type = random.choice(['forest', 'mountain'])
            print(f"切换主题到: {new_theme} ({self.current_background_type})")

    def change_background_type(self, new_type):
        if new_type in ['space', 'another-world', 'land', 'forest', 'mountain']:
            if new_type in ['space', 'another-world', 'land']:
                self.current_theme = self.THEME_SPACE
            else:
                self.current_theme = self.THEME_NATURE
            self.current_background_type = new_type
            print(f"切换背景类型到: {new_type}")

    def update(self, pause=False, distance=None, game_speed=3, player_rect=None):
        """更新背景状态"""
        if not pause and distance is not None:
            # 更新背景位置
            self.update_layer_positions(game_speed)

            # 计算到下一个场景切换点的距离
            current_section = int(distance // self.SCENE_CHANGE_DISTANCE)
            next_change_point = (current_section + 1) * self.SCENE_CHANGE_DISTANCE
            distance_to_change = next_change_point - distance

            # 调试信息输出
            if int(distance) % 100 == 0:  # 每100米打印一次信息
                print(f"当前距离: {distance:.1f}米")
                print(f"下一个切换点: {next_change_point}米")
                print(f"距离切换还有: {distance_to_change:.1f}米")
                print(f"传送门状态: {'激活' if self.portal.active else '未激活'}")
                print(f"传送门触发状态: {'已触发' if self.portal.triggered else '未触发'}")

            # 强制关闭传送门的条件
            if distance_to_change > self.portal_activation_distance + 100:  # 在远离切换点时
                if self.portal.active or self.portal.triggered:  # 如果传送门还在活动
                    print(f"强制关闭传送门并重置状态")
                    self.portal.reset()
                    self.portal.x = self.WIDTH - 300
                    self.portal.y = self.HEIGHT//2 - 150

            # 处理传送门出现
            elif distance_to_change <= self.portal_activation_distance and not self.portal.active:
                print(f"=== 传送门触发条件检查 ===")
                print(f"距离切换点距离: {distance_to_change:.1f} <= {self.portal_activation_distance}")
                print(f"当前总距离: {distance:.1f}")
                print(f"传送门当前状态: {self.portal.active}")
                print(f"传送门已触发状态: {self.portal.triggered}")

                print(f"传送门出现！剩余距离: {distance_to_change:.1f}米")
                self.portal.activate()
                # 确保传送门从右侧出现
                self.portal.x = self.WIDTH - 300
                self.portal.y = self.HEIGHT//2 - 150

            # 更新传送门
            if self.portal.active:
                self.portal.update(game_speed)

                # 检查玩家是否与传送门碰撞
                if player_rect and not self.portal.triggered:
                    portal_rect = self.portal.get_rect()
                    if portal_rect.colliderect(player_rect):
                        print("玩家碰到传送门！准备切换场景...")
                        self.portal.triggered = True
                        new_sequence_index = current_section % len(self.background_sequence)
                        if new_sequence_index != self.current_sequence_index:
                            self.current_sequence_index = new_sequence_index
                            new_background = self.background_sequence[self.current_sequence_index]
                            print(f"通过传送门！切换背景到: {new_background}，当前距离: {distance}米")
                            self.change_background_type(new_background)
                            self.portal.deactivate()
                            # 确保传送门完全重置
                            self.portal.reset()

            self.current_distance = distance

    def update_by_distance(self, distance):
        """根据距离更新背景场景

        Args:
            distance (float): 当前行进的总距离（单位：米）
        """
        # 计算新的场景索引
        new_sequence_index = int(distance // self.SCENE_CHANGE_DISTANCE) % len(self.background_sequence)
        if new_sequence_index != self.current_sequence_index:
            self.current_sequence_index = new_sequence_index
            new_background = self.background_sequence[self.current_sequence_index]
            print(f"切换背景到: {new_background}，当前距离: {distance}米")
            self.change_background_type(new_background)

        self.current_distance = distance

    def reset(self):
        """重置背景到初始状态"""
        self.current_distance = 0
        self.current_sequence_index = 0
        self.current_background_type = 'space'
        self.current_theme = self.THEME_SPACE

        # 重置所有图层位置
        for layer_name in self.layer_positions:
            self.layer_positions[layer_name] = [0, 0]

        # 重置传送门
        self.portal.reset()  # 使用Portal类的reset方法
        self.portal.x = self.WIDTH - 300  # 重置传送门位置到初始位置
        self.portal.y = self.HEIGHT//2 - 150