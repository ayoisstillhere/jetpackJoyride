import pygame
import os
import random

class BackgroundSystem:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        
        # 场景切换相关
        self.SCENE_CHANGE_DISTANCE = 2000  # 每2000米（2km）切换一次场景
        self.current_distance = 0  # 当前行进距离
        self.background_sequence = ['space', 'land', 'mountain']  # 场景切换顺序
        self.current_sequence_index = 0  # 当前场景索引
        
        # 主题相关
        self.THEME_SPACE = "space"  # 太空主题（包括太空、another-world和land）
        self.THEME_NATURE = "nature"  # 自然主题（包括森林和山脉）
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
                'another_world': {  # another-world层
                    'sky': None,
                    'composed': None
                },
                'land': {  # land层
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
            # another-world层速度
            'sky': 0.2,
            'composed': 0.4,
            # land层速度
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
            # another-world层位置
            'sky': [0, 0],
            'composed': [0, 0],
            # land层位置
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
        # 加载太空主题的分层背景
        space_folder = os.path.join("backgrounds", "space_background_pack")
        
        # 加载太空层
        if os.path.exists(space_folder):
            layer_files = {
                'background': os.path.join('layers', 'parallax-space-backgound.png'),
                'stars': os.path.join('layers', 'parallax-space-stars.png'),
                'far_planets': os.path.join('layers', 'parallax-space-far-planets.png'),
                'ring_planet': os.path.join('layers', 'parallax-space-ring-planet.png'),
                'big_planet': os.path.join('layers', 'parallax-space-big-planet.png')
            }
            
            for layer, filename in layer_files.items():
                file_path = os.path.join(space_folder, filename)
                if os.path.exists(file_path):
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                        self.background_themes[self.THEME_SPACE]['space_layers'][layer] = img
                        print(f"Loaded space {layer} layer: {filename}")
                    except pygame.error as e:
                        print(f"Could not load image {file_path}: {e}")
                else:
                    print(f"Missing space layer: {file_path}")

            # 加载another-world层
            another_world_folder = os.path.join(space_folder, 'another-world')
            if os.path.exists(another_world_folder):
                layer_files = {
                    'sky': 'sky.png',
                    'composed': 'composed-bg.png'
                }
                
                for layer, filename in layer_files.items():
                    file_path = os.path.join(another_world_folder, filename)
                    if os.path.exists(file_path):
                        try:
                            img = pygame.image.load(file_path).convert_alpha()
                            img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                            self.background_themes[self.THEME_SPACE]['another_world'][layer] = img
                            print(f"Loaded another-world {layer} layer: {filename}")
                        except pygame.error as e:
                            print(f"Could not load image {file_path}: {e}")
                    else:
                        print(f"Missing another-world layer: {file_path}")

            # 加载land层
            land_folder = os.path.join(space_folder, 'land')
            if os.path.exists(land_folder):
                layer_files = {
                    'sky': 'sky.png',
                    'back': 'back.png'
                }
                
                for layer, filename in layer_files.items():
                    file_path = os.path.join(land_folder, filename)
                    if os.path.exists(file_path):
                        try:
                            img = pygame.image.load(file_path).convert_alpha()
                            img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                            self.background_themes[self.THEME_SPACE]['land'][layer] = img
                            print(f"Loaded land {layer} layer: {filename}")
                        except pygame.error as e:
                            print(f"Could not load image {file_path}: {e}")
                    else:
                        print(f"Missing land layer: {file_path}")

        # 加载森林主题的分层背景
        forest_folder = os.path.join("backgrounds", "parallax_forest_pack")
        if os.path.exists(forest_folder):
            layer_files = {
                'back_trees': os.path.join('layers', 'parallax-forest-back-trees.png'),
                'lights': os.path.join('layers', 'parallax-forest-lights.png'),
                'middle_trees': os.path.join('layers', 'parallax-forest-middle-trees.png'),
                'front_trees': os.path.join('layers', 'parallax-forest-front-trees.png')
            }
            
            for layer, filename in layer_files.items():
                file_path = os.path.join(forest_folder, filename)
                if os.path.exists(file_path):
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                        self.background_themes[self.THEME_NATURE]['forest_layers'][layer] = img
                        print(f"Loaded forest {layer} layer: {filename}")
                    except pygame.error as e:
                        print(f"Could not load image {file_path}: {e}")
                else:
                    print(f"Missing forest layer: {file_path}")

        # 加载山脉主题的分层背景
        mountain_folder = os.path.join("backgrounds", "parallax_mountain_pack")
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
                if os.path.exists(file_path):
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                        self.background_themes[self.THEME_NATURE]['mountain_layers'][layer] = img
                        print(f"Loaded mountain {layer} layer: {filename}")
                    except pygame.error as e:
                        print(f"Could not load image {file_path}: {e}")
                else:
                    print(f"Missing mountain layer: {file_path}")

        # 检查是否有任何背景被加载
        if (not any(self.background_themes[self.THEME_SPACE]['space_layers'].values()) and 
            not any(self.background_themes[self.THEME_SPACE]['another_world'].values()) and
            not any(self.background_themes[self.THEME_SPACE]['land'].values()) and
            not any(self.background_themes[self.THEME_NATURE]['forest_layers'].values()) and 
            not any(self.background_themes[self.THEME_NATURE]['mountain_layers'].values())):
            print("警告：没有成功加载任何背景图片！")

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
        screen.fill('black')  # 设置默认背景色为黑色

        if self.current_theme == self.THEME_SPACE:
            if self.current_background_type == 'space':
                # 绘制太空分层背景
                layers = ['background', 'stars', 'far_planets', 'ring_planet', 'big_planet']
                for layer in layers:
                    img = self.background_themes[self.THEME_SPACE]['space_layers'][layer]
                    if img is not None:
                        # 绘制两次以实现无缝滚动
                        x = self.layer_positions[layer][0]
                        screen.blit(img, (x, 0))
                        screen.blit(img, (x + self.WIDTH, 0))
            elif self.current_background_type == 'another-world':
                # 绘制another-world分层背景
                layers = ['sky', 'composed']
                for layer in layers:
                    img = self.background_themes[self.THEME_SPACE]['another_world'][layer]
                    if img is not None:
                        x = self.layer_positions[layer][0]
                        screen.blit(img, (x, 0))
                        screen.blit(img, (x + self.WIDTH, 0))
            else:  # land
                # 绘制land分层背景
                layers = ['sky', 'back']
                for layer in layers:
                    img = self.background_themes[self.THEME_SPACE]['land'][layer]
                    if img is not None:
                        x = self.layer_positions[layer][0]
                        screen.blit(img, (x, 0))
                        screen.blit(img, (x + self.WIDTH, 0))
        else:  # THEME_NATURE
            if self.current_background_type == 'forest':
                # 绘制森林分层背景
                layers = ['back_trees', 'lights', 'middle_trees', 'front_trees']
                for layer in layers:
                    img = self.background_themes[self.THEME_NATURE]['forest_layers'][layer]
                    if img is not None:
                        x = self.layer_positions[layer][0]
                        screen.blit(img, (x, 0))
                        screen.blit(img, (x + self.WIDTH, 0))
            else:  # mountain
                # 绘制山脉分层背景
                layers = ['sky', 'far_mountains', 'mountains', 'trees', 'foreground_trees']
                for layer in layers:
                    img = self.background_themes[self.THEME_NATURE]['mountain_layers'][layer]
                    if img is not None:
                        x = self.layer_positions[layer][0]
                        screen.blit(img, (x, 0))
                        screen.blit(img, (x + self.WIDTH, 0))

    def change_theme(self, new_theme):
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            if new_theme == self.THEME_SPACE:
                self.current_background_type = random.choice(['space', 'another-world', 'land'])
            else:  # THEME_NATURE
                self.current_background_type = random.choice(['forest', 'mountain'])
            print(f"Changed theme to: {new_theme} ({self.current_background_type})")

    def change_background_type(self, new_type):
        if new_type in ['space', 'another-world', 'land', 'forest', 'mountain']:
            if new_type in ['space', 'another-world', 'land']:
                self.current_theme = self.THEME_SPACE
            else:
                self.current_theme = self.THEME_NATURE
            self.current_background_type = new_type
            print(f"Changed background type to: {new_type}")

    def update_by_distance(self, distance):
        """根据行进距离更新背景场景
        
        Args:
            distance (float): 当前行进的总距离（单位：米）
        """
        # 检查是否需要切换场景
        if int(distance / self.SCENE_CHANGE_DISTANCE) > int(self.current_distance / self.SCENE_CHANGE_DISTANCE):
            # 切换到序列中的下一个场景
            self.current_sequence_index = (self.current_sequence_index + 1) % len(self.background_sequence)
            new_background = self.background_sequence[self.current_sequence_index]
            self.change_background_type(new_background)
        
        self.current_distance = distance

    def update(self, pause=False, distance=None):
        """更新背景状态
        
        Args:
            pause (bool): 是否暂停
            distance (float, optional): 当前行进的总距离（单位：米）
        """
        if not pause:
            # 如果提供了距离信息，更新场景
            if distance is not None:
                self.update_by_distance(distance)
            
            # 更新视差滚动
            if self.current_background_type in ['space', 'another-world', 'land', 'forest', 'mountain']:
                self.update_layer_positions(3)  # 更新视差滚动位置 