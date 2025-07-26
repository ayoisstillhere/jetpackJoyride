import pygame
import os
import random
from entities.portal import Portal
from config.settings import WIDTH, HEIGHT

class BackgroundSystem:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height

        # Scene configuration
        self.SCENE_CHANGE_DISTANCE = 800 
        self.current_distance = 0
        self.background_sequence = ['space', 'another-world', 'land', 'forest', 'mountain']
        self.current_sequence_index = 0

        # Portal configuration
        self.portal = Portal(WIDTH - 300, HEIGHT//2 - 150)
        self.portal_activation_distance = 200
        self.portal_after_effect_distance = 50

        # Theme configuration
        self.THEME_SPACE = "space"
        self.THEME_NATURE = "nature"
        self.current_theme = self.THEME_SPACE

        # Initialize theme structure
        self.background_themes = self._initialize_theme_structure()

        # Initialize layer configurations
        self.parallax_speeds = self._initialize_parallax_speeds()
        self.layer_positions = self._initialize_layer_positions()

        # Current background state
        self.current_background_type = 'space'

        # Load background images
        self.load_background_images()

    def _initialize_theme_structure(self):
        """Initialize the theme structure with empty layers"""
        return {
            self.THEME_SPACE: {
                'space_layers': {layer: None for layer in ['background', 'stars', 'far_planets', 'ring_planet', 'big_planet']},
                'another_world': {layer: None for layer in ['sky', 'composed']},
                'land': {layer: None for layer in ['sky', 'back']}
            },
            self.THEME_NATURE: {
                'forest_layers': {layer: None for layer in ['back_trees', 'lights', 'middle_trees', 'front_trees']},
                'mountain_layers': {layer: None for layer in ['sky', 'mountains', 'far_mountains', 'trees', 'foreground_trees']}
            }
        }

    def _initialize_parallax_speeds(self):
        """Initialize parallax scrolling speeds for all layers"""
        return {
            # Space theme speeds
            'background': 0.2, 'stars': 0.3, 'far_planets': 0.4,
            'ring_planet': 0.6, 'big_planet': 0.8,
            # Another-world theme speeds
            'sky': 0.2, 'composed': 0.4,
            # Land theme speeds
            'back': 0.4,
            # Forest theme speeds
            'back_trees': 0.2, 'lights': 0.3,
            'middle_trees': 0.6, 'front_trees': 0.8,
            # Mountain theme speeds
            'far_mountains': 0.3, 'mountains': 0.4,
            'trees': 0.6, 'foreground_trees': 0.8
        }

    def _initialize_layer_positions(self):
        """Initialize positions for all layers"""
        return {layer: [0, 0] for layer in self.parallax_speeds.keys()}

    def _load_theme_images(self, theme_folder, layer_files, theme_key, layer_dict):
        """Load images for a specific theme and its layers"""
        if not os.path.exists(theme_folder):
            print(f"Theme folder not found: {theme_folder}")
            return

        for layer, filename in layer_files.items():
            file_path = os.path.join(theme_folder, filename)
            if os.path.exists(file_path):
                try:
                    img = pygame.image.load(file_path).convert_alpha()
                    img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                    self.background_themes[theme_key][layer_dict][layer] = img
                    print(f"Successfully loaded {layer} layer: {filename}")
                except pygame.error as e:
                    print(f"Failed to load image {file_path}: {e}")
            else:
                print(f"Missing layer file: {file_path}")

    def load_background_images(self):
        """Load all background images for different themes"""
        print("Start loading background images...")

        # Load space theme
        space_folder = os.path.join("backgrounds", "space_background_pack")
        space_layers = {
            'background': os.path.join('layers', 'parallax-space-background.png'),
            'stars': os.path.join('layers', 'parallax-space-stars.png'),
            'far_planets': os.path.join('layers', 'parallax-space-far-planets.png'),
            'ring_planet': os.path.join('layers', 'parallax-space-ring-planet.png'),
            'big_planet': os.path.join('layers', 'parallax-space-big-planet.png')
        }
        self._load_theme_images(space_folder, space_layers, self.THEME_SPACE, 'space_layers')

        # Load another-world theme
        another_world_folder = os.path.join(space_folder, 'another-world')
        another_world_layers = {
            'sky': 'sky.png',
            'composed': 'composed-bg.png'
        }
        self._load_theme_images(another_world_folder, another_world_layers, self.THEME_SPACE, 'another_world')

        # Load land theme
        land_folder = os.path.join(space_folder, 'land')
        land_layers = {
            'sky': 'sky.png',
            'back': 'back.png'
        }
        self._load_theme_images(land_folder, land_layers, self.THEME_SPACE, 'land')

        # Load forest theme
        forest_folder = os.path.join("backgrounds", "parallax_forest_pack")
        forest_layers = {
            'back_trees': os.path.join('layers', 'parallax-forest-back-trees.png'),
            'lights': os.path.join('layers', 'parallax-forest-lights.png'),
            'middle_trees': os.path.join('layers', 'parallax-forest-middle-trees.png'),
            'front_trees': os.path.join('layers', 'parallax-forest-front-trees.png')
        }
        self._load_theme_images(forest_folder, forest_layers, self.THEME_NATURE, 'forest_layers')

        # Load mountain theme
        mountain_folder = os.path.join("backgrounds", "parallax_mountain_pack")
        mountain_layers = {
            'sky': os.path.join('layers', 'parallax-mountain-bg.png'),
            'mountains': os.path.join('layers', 'parallax-mountain-mountains.png'),
            'far_mountains': os.path.join('layers', 'parallax-mountain-montain-far.png'),
            'trees': os.path.join('layers', 'parallax-mountain-trees.png'),
            'foreground_trees': os.path.join('layers', 'parallax-mountain-foreground-trees.png')
        }
        self._load_theme_images(mountain_folder, mountain_layers, self.THEME_NATURE, 'mountain_layers')

        # Verify loading success
        if not any(any(layers.values()) for theme in self.background_themes.values() for layers in theme.values()):
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
                # print(f"Next change point: {next_change_point}m")
                # print(f"Distance to change: {distance_to_change:.1f}m")
                # print(f"Portal status: {'active' if self.portal.active else 'inactive'}")
                # print(f"Portal trigger status: {'triggered' if self.portal.triggered else 'not triggered'}")

            # force close portal conditions
            if distance_to_change > self.portal_activation_distance + 100:  # when far from change point
                if self.portal.active or self.portal.triggered:  # if portal is still active
                    print(f"Force closing portal and resetting state")
                    self.portal.reset()
                    self.portal.x = self.WIDTH - 300
                    self.portal.y = self.HEIGHT//2 - 150

            # handle portal appearance and immediate background change
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
                
                new_sequence_index = current_section % len(self.background_sequence)
                if new_sequence_index != self.current_sequence_index:
                    self.current_sequence_index = new_sequence_index
                    new_background = self.background_sequence[self.current_sequence_index]
                    self.change_background_type(new_background)

            if self.portal.active:
                self.portal.update(game_speed)

                if distance_to_change > self.portal_activation_distance - 50:  # Close when 50 meters away from switch point
                    if not self.portal.triggered:
                        print("Portal automatically closes")
                        self.portal.triggered = True
                        self.portal.deactivate()
                        self.portal.reset()
                
                elif player_rect and not self.portal.triggered:
                    portal_rect = self.portal.get_rect()
                    if portal_rect.colliderect(player_rect):
                        self.portal.triggered = True
                        self.portal.deactivate()
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