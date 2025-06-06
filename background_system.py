import pygame
import os
import random
from entities.portal import Portal
from config.settings import WIDTH, HEIGHT

class BackgroundSystem:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height

        # scene change related
        self.SCENE_CHANGE_DISTANCE = 2000  # every 2000m, change scene
        self.current_distance = 0  # current distance
        self.background_sequence = ['space', 'another-world', 'land', 'forest', 'mountain']  # scene change sequence
        self.current_sequence_index = 0  # current scene index

        # portal related
        self.portal = Portal(WIDTH - 300, HEIGHT//2 - 150)  # create portal on the right side of the screen, slightly left
        self.portal_activation_distance = 200  # show portal 200m before scene change
        self.portal_after_effect_distance = 50  # continue to show portal for 50m after scene change

        # theme related
        self.THEME_SPACE = "space"  # space theme
        self.THEME_NATURE = "nature"  # nature theme
        self.current_theme = self.THEME_SPACE
        self.background_themes = {
            self.THEME_SPACE: {
                'space_layers': {  # space layer
                    'background': None,
                    'stars': None,
                    'far_planets': None,
                    'ring_planet': None,
                    'big_planet': None
                },
                'another_world': {  # another-world layer
                    'sky': None,
                    'composed': None
                },
                'land': {  # land layer
                    'sky': None,
                    'back': None
                }
            },
            self.THEME_NATURE: {
                'forest_layers': {  # forest layer
                    'back_trees': None,
                    'lights': None,
                    'middle_trees': None,
                    'front_trees': None
                },
                'mountain_layers': {  # mountain layer
                    'sky': None,
                    'mountains': None,
                    'far_mountains': None,
                    'trees': None,
                    'foreground_trees': None
                }
            }
        }

        # parallax scrolling speed
        self.parallax_speeds = {
            # space layer speed
            'background': 0.2,
            'stars': 0.3,
            'far_planets': 0.4,
            'ring_planet': 0.6,
            'big_planet': 0.8,
            # another-world layer speed
            'sky': 0.2,
            'composed': 0.4,
            # land layer speed
            'back': 0.4,
            # forest layer speed
            'back_trees': 0.2,
            'lights': 0.3,
            'middle_trees': 0.6,
            'front_trees': 0.8,
            # mountain layer speed
            'far_mountains': 0.3,
            'mountains': 0.4,
            'trees': 0.6,
            'foreground_trees': 0.8
        }

        # layer positions
        self.layer_positions = {
            # space layer positions
            'background': [0, 0],
            'stars': [0, 0],
            'far_planets': [0, 0],
            'ring_planet': [0, 0],
            'big_planet': [0, 0],
            # another-world layer positions
            'sky': [0, 0],
            'composed': [0, 0],
            # land layer positions
            'back': [0, 0],
            # forest layer positions
            'back_trees': [0, 0],
            'lights': [0, 0],
            'middle_trees': [0, 0],
            'front_trees': [0, 0],
            # mountain layer positions
            'far_mountains': [0, 0],
            'mountains': [0, 0],
            'trees': [0, 0],
            'foreground_trees': [0, 0]
        }

        # current used background type
        self.current_background_type = 'space'  # optional values: 'space', 'another-world', 'land', 'forest', 'mountain'

        # load background images
        self.load_background_images()

    def load_background_images(self):
        print("Start loading background images...")
        # load space theme parallax background images
        space_folder = os.path.join("backgrounds", "space_background_pack")
        print(f"Checking space background folder: {space_folder}")

        # load space layer parallax background images
        if os.path.exists(space_folder):
            layer_files = {
                'background': os.path.join('layers', 'parallax-space-background.png'),  # fix spelling error
                'stars': os.path.join('layers', 'parallax-space-stars.png'),
                'far_planets': os.path.join('layers', 'parallax-space-far-planets.png'),
                'ring_planet': os.path.join('layers', 'parallax-space-ring-planet.png'),
                'big_planet': os.path.join('layers', 'parallax-space-big-planet.png')
            }

            for layer, filename in layer_files.items():
                file_path = os.path.join(space_folder, filename)
                print(f"Trying to load file: {file_path}")
                if os.path.exists(file_path):
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                        self.background_themes[self.THEME_SPACE]['space_layers'][layer] = img
                        print(f"Successfully loaded space {layer} layer: {filename}")
                    except pygame.error as e:
                        print(f"Failed to load image {file_path}: {e}")
                else:
                    print(f"Missing space layer file: {file_path}")

            # load another-world layer
            another_world_folder = os.path.join(space_folder, 'another-world')
            print(f"Checking another-world folder: {another_world_folder}")
            if os.path.exists(another_world_folder):
                layer_files = {
                    'sky': 'sky.png',
                    'composed': 'composed-bg.png'
                }

                for layer, filename in layer_files.items():
                    file_path = os.path.join(another_world_folder, filename)
                    print(f"Trying to load file: {file_path}")
                    if os.path.exists(file_path):
                        try:
                            img = pygame.image.load(file_path).convert_alpha()
                            img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                            self.background_themes[self.THEME_SPACE]['another_world'][layer] = img
                            print(f"Successfully loaded another-world {layer} layer: {filename}")
                        except pygame.error as e:
                            print(f"Failed to load image {file_path}: {e}")
                    else:
                        print(f"Missing another-world layer file: {file_path}")

            # load land layer
            land_folder = os.path.join(space_folder, 'land')
            print(f"Checking land folder: {land_folder}")
            if os.path.exists(land_folder):
                layer_files = {
                    'sky': 'sky.png',
                    'back': 'back.png'
                }

                for layer, filename in layer_files.items():
                    file_path = os.path.join(land_folder, filename)
                    print(f"Trying to load file: {file_path}")
                    if os.path.exists(file_path):
                        try:
                            img = pygame.image.load(file_path).convert_alpha()
                            img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                            self.background_themes[self.THEME_SPACE]['land'][layer] = img
                            print(f"Successfully loaded land {layer} layer: {filename}")
                        except pygame.error as e:
                            print(f"Failed to load image {file_path}: {e}")
                    else:
                        print(f"Missing land layer file: {file_path}")
        else:
            print(f"Space background folder not found: {space_folder}")

        # load forest theme parallax background
        forest_folder = os.path.join("backgrounds", "parallax_forest_pack")
        print(f"Checking forest background folder: {forest_folder}")
        if os.path.exists(forest_folder):
            layer_files = {
                'back_trees': os.path.join('layers', 'parallax-forest-back-trees.png'),
                'lights': os.path.join('layers', 'parallax-forest-lights.png'),
                'middle_trees': os.path.join('layers', 'parallax-forest-middle-trees.png'),
                'front_trees': os.path.join('layers', 'parallax-forest-front-trees.png')
            }

            for layer, filename in layer_files.items():
                file_path = os.path.join(forest_folder, filename)
                print(f"Trying to load file: {file_path}")
                if os.path.exists(file_path):
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                        self.background_themes[self.THEME_NATURE]['forest_layers'][layer] = img
                        print(f"Successfully loaded forest {layer} layer: {filename}")
                    except pygame.error as e:
                        print(f"Failed to load image {file_path}: {e}")
                else:
                    print(f"Missing forest layer file: {file_path}")
        else:
            print(f"Forest background folder not found: {forest_folder}")

        # load mountain theme parallax background
        mountain_folder = os.path.join("backgrounds", "parallax_mountain_pack")
        print(f"Checking mountain background folder: {mountain_folder}")
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
                print(f"Trying to load file: {file_path}")
                if os.path.exists(file_path):
                    try:
                        img = pygame.image.load(file_path).convert_alpha()
                        img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                        self.background_themes[self.THEME_NATURE]['mountain_layers'][layer] = img
                        print(f"Successfully loaded mountain {layer} layer: {filename}")
                    except pygame.error as e:
                        print(f"Failed to load image {file_path}: {e}")
                else:
                    print(f"Missing mountain layer file: {file_path}")
        else:
            print(f"Mountain background folder not found: {mountain_folder}")

        # check if any background was loaded
        if (not any(self.background_themes[self.THEME_SPACE]['space_layers'].values()) and
            not any(self.background_themes[self.THEME_SPACE]['another_world'].values()) and
            not any(self.background_themes[self.THEME_SPACE]['land'].values()) and
            not any(self.background_themes[self.THEME_NATURE]['forest_layers'].values()) and
            not any(self.background_themes[self.THEME_NATURE]['mountain_layers'].values())):
            print("Warning: No background images were loaded successfully!")
        else:
            print("Background loading completed!")

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

        # select layers to draw based on current background type
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

        # draw each layer
        for layer_name, layer_image in layers.items():
            if layer_image is not None:
                # get layer position
                x = self.layer_positions[layer_name][0]
                y = self.layer_positions[layer_name][1]

                # draw main layer
                screen.blit(layer_image, (x, y))

                # if layer is out of screen, draw a duplicate layer behind
                if x + layer_image.get_width() < self.WIDTH:
                    screen.blit(layer_image, (x + layer_image.get_width(), y))

                # if not pause, update layer position
                if not pause:
                    speed = self.parallax_speeds[layer_name] * game_speed
                    self.layer_positions[layer_name][0] -= speed

                    # if layer is completely out of screen, reset position
                    if self.layer_positions[layer_name][0] <= -layer_image.get_width():
                        self.layer_positions[layer_name][0] = 0

        # draw portal at the end
        self.portal.draw(screen)

    def change_theme(self, new_theme):
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            if new_theme == self.THEME_SPACE:
                self.current_background_type = random.choice(['space', 'another-world', 'land'])
            else:  # THEME_NATURE
                self.current_background_type = random.choice(['forest', 'mountain'])
            print(f"Switching theme to: {new_theme} ({self.current_background_type})")

    def change_background_type(self, new_type):
        if new_type in ['space', 'another-world', 'land', 'forest', 'mountain']:
            if new_type in ['space', 'another-world', 'land']:
                self.current_theme = self.THEME_SPACE
            else:
                self.current_theme = self.THEME_NATURE
            self.current_background_type = new_type
            print(f"Switching background type to: {new_type}")

    def update(self, pause=False, distance=None, game_speed=3, player_rect=None):
        """Update background state"""
        if not pause and distance is not None:
            # update background position
            self.update_layer_positions(game_speed)

            # calculate distance to next scene change point
            current_section = int(distance // self.SCENE_CHANGE_DISTANCE)
            next_change_point = (current_section + 1) * self.SCENE_CHANGE_DISTANCE
            distance_to_change = next_change_point - distance

            # debug information output
            if int(distance) % 100 == 0:  # print info every 100 meters
                print(f"Current distance: {distance:.1f}m")
                print(f"Next change point: {next_change_point}m")
                print(f"Distance to change: {distance_to_change:.1f}m")
                print(f"Portal status: {'active' if self.portal.active else 'inactive'}")
                print(f"Portal trigger status: {'triggered' if self.portal.triggered else 'not triggered'}")

            # force close portal conditions
            if distance_to_change > self.portal_activation_distance + 100:  # when far from change point
                if self.portal.active or self.portal.triggered:  # if portal is still active
                    print(f"Force closing portal and resetting state")
                    self.portal.reset()
                    self.portal.x = self.WIDTH - 300
                    self.portal.y = self.HEIGHT//2 - 150

            # handle portal appearance
            elif distance_to_change <= self.portal_activation_distance and not self.portal.active:
                print(f"=== Portal Trigger Condition Check ===")
                print(f"Distance to change point: {distance_to_change:.1f} <= {self.portal_activation_distance}")
                print(f"Current total distance: {distance:.1f}")
                print(f"Portal current status: {self.portal.active}")
                print(f"Portal triggered status: {self.portal.triggered}")

                print(f"Portal appears! Remaining distance: {distance_to_change:.1f}m")
                self.portal.activate()
                # ensure portal appears from right side
                self.portal.x = self.WIDTH - 300
                self.portal.y = self.HEIGHT//2 - 150

            # update portal
            if self.portal.active:
                self.portal.update(game_speed)

                # check if player collides with portal
                if player_rect and not self.portal.triggered:
                    portal_rect = self.portal.get_rect()
                    if portal_rect.colliderect(player_rect):
                        print("Player hit portal! Preparing scene change...")
                        self.portal.triggered = True
                        new_sequence_index = current_section % len(self.background_sequence)
                        if new_sequence_index != self.current_sequence_index:
                            self.current_sequence_index = new_sequence_index
                            new_background = self.background_sequence[self.current_sequence_index]
                            print(f"Through portal! Switching background to: {new_background}, current distance: {distance}m")
                            self.change_background_type(new_background)
                            self.portal.deactivate()
                            # ensure portal is fully reset
                            self.portal.reset()

            self.current_distance = distance

    def update_by_distance(self, distance):
        """update background by distance

        Args:
            distance (float): current total distance (unit: meter)
        """
        # calculate new scene index
        new_sequence_index = int(distance // self.SCENE_CHANGE_DISTANCE) % len(self.background_sequence)
        if new_sequence_index != self.current_sequence_index:
            self.current_sequence_index = new_sequence_index
            new_background = self.background_sequence[self.current_sequence_index]
            print(f"Switching background to: {new_background}, current distance: {distance}m")
            self.change_background_type(new_background)

        self.current_distance = distance

    def reset(self):
        """reset background to initial state"""
        self.current_distance = 0
        self.current_sequence_index = 0
        self.current_background_type = 'space'
        self.current_theme = self.THEME_SPACE

        # reset all layer positions
        for layer_name in self.layer_positions:
            self.layer_positions[layer_name] = [0, 0]
            
        # reset portal
        self.portal.reset()  # use Portal class's reset method
        self.portal.x = self.WIDTH - 300  # reset portal position to initial position
        self.portal.y = self.HEIGHT//2 - 150 