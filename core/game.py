import pygame
import random, os

from ai import RuleBasedAgent
from config.settings import WIDTH, HEIGHT, FPS, BG_COLOR, FONT_PATH
from core.state import GameState
from core.events import handle_events
from systems.meteor_system import MeteorSystem
from systems.ui import draw_screen
from systems.physics import apply_gravity, update_vertical_position, check_platform_collisions
from entities.player import Player
from entities.rocket import Rocket
from entities.laser import Laser
from entities.coin import Coin, spawn_coins, update_coins, draw_coins, draw_coin_counter
from entities.meteor import Meteor
from background_system import BackgroundSystem
from difficulty_system import DifficultySystem

class GameStates:
    START = "start"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    CHARACTER_SELECT = "character_select"

class Game:
    def __init__(self, render=True):
        pygame.init()
        self.render = render

        if self.render:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("AI Jetpack Runner")
        else:
            self.screen = None
        self.surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_PATH, 32)
        self.title_font = pygame.font.Font(FONT_PATH, 64)
        self.small_font = pygame.font.Font(FONT_PATH, 24)

        # Core state
        self.state = GameState()
        self.game_state = GameStates.START

        # Game systems
        self.background_system = BackgroundSystem(WIDTH, HEIGHT)
        self.difficulty_system = DifficultySystem()

        # Game elements
        self.player = Player(render=self.render)
        self.rocket = Rocket(render=self.render)
        self.laser = Laser(render=self.render)
        self.lines = [0, WIDTH/4, WIDTH/2, 3*WIDTH/4]
        self.bg_color = BG_COLOR

        # Character selection
        self.character_buttons = {}
        self.selected_character = "boy"

        # Coin system
        self.coins = []
        self.last_coin_spawn = 0
        self.coin_spawn_distance = 400

        # Meteor system
        self.meteor_system = MeteorSystem()

        # UI buttons
        self.start_button = None
        self.restart_button = None
        self.quit_button = None
        self.character_button = None
        self.back_button = None

        # AI
        # self.agent = RuleBasedAgent()
        self.player.controlled_by_ai = False

        self.running = True

    def run(self):
        while self.running:
            events = pygame.event.get()
            self.clock.tick(FPS)

            # === Events ===
            if self.game_state == GameStates.START:
                self._handle_start_events(events)

            elif self.game_state == GameStates.CHARACTER_SELECT:
                self._handle_character_select_events()

            elif self.game_state == GameStates.PLAYING:
                quit_requested = handle_events(self.state, self.player, None, None, events)
                if quit_requested:
                    self.running = False
                    break

                if self.state.paused:
                    self.game_state = GameStates.PAUSED

            elif self.game_state == GameStates.PAUSED:
                quit_requested = handle_events(self.state, self.player, self.restart_button, self.quit_button)
                if quit_requested:
                    self.running = False
                    break
                if self.state.restart_requested:
                    self._start_new_game()
                elif not self.state.paused:
                    self.game_state = GameStates.PLAYING

            elif self.game_state == GameStates.GAME_OVER:
                self._handle_game_over_events(events)

            # === Draw ===
            if self.render:
                if self.game_state == GameStates.START:
                    self._draw_start_screen()
                elif self.game_state == GameStates.CHARACTER_SELECT:
                    self._draw_character_select_screen()
                elif self.game_state == GameStates.GAME_OVER:
                    self._draw_game_over_screen()
                else:
                    self._draw_game_screen()

                pygame.display.flip()

        pygame.quit()

    def _handle_start_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button and self.start_button.collidepoint(event.pos):
                    self._start_new_game()
                elif self.character_button and self.character_button.collidepoint(event.pos):
                    self.game_state = GameStates.CHARACTER_SELECT
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._start_new_game()
                elif event.key == pygame.K_c:
                    self.game_state = GameStates.CHARACTER_SELECT

    def _handle_character_select_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button and self.start_button.collidepoint(event.pos):
                    self._start_new_game()
                elif self.back_button and self.back_button.collidepoint(event.pos):
                    self.game_state = GameStates.START
                # Check character selection
                for char_type, button in self.character_buttons.items():
                    if button.collidepoint(event.pos):
                        self.selected_character = char_type
                        self.player.change_character(char_type)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = GameStates.START
                elif event.key == pygame.K_SPACE:
                    self._start_new_game()

    def _handle_game_over_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.restart_button and self.restart_button.collidepoint(event.pos):
                    self._start_new_game()
                elif self.quit_button and self.quit_button.collidepoint(event.pos):
                    self.game_state = GameStates.START
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._start_new_game()
                elif event.key == pygame.K_ESCAPE:
                    self.game_state = GameStates.START

    def _draw_start_screen(self):
        # Use background system's color
        self.background_system.draw_background(self.screen, False, 0)

        # Title
        title_text = self.title_font.render("AI JETPACK RUNNER", True, 'white')
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(title_text, title_rect)

        # Instructions
        instructions = [
            "Use SPACE to boost your jetpack",
            "Collect coins and avoid obstacles",
            "Press SPACE or click START to begin",
            "Press C or click CHARACTER to choose character"
        ]

        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, 'white')
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 40 + i * 40))
            self.screen.blit(text, text_rect)

        # Start button
        self.start_button = pygame.draw.rect(self.screen, 'green', [WIDTH//2 - 150, HEIGHT*3//4 - 25, 140, 50], 0, 10)
        pygame.draw.rect(self.screen, 'white', [WIDTH//2 - 150, HEIGHT*3//4 - 25, 140, 50], 3, 10)
        start_text = self.font.render("START", True, 'white')
        start_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, start_rect)

        # Character button
        self.character_button = pygame.draw.rect(self.screen, 'blue', [WIDTH//2 + 10, HEIGHT*3//4 - 25, 140, 50], 0, 10)
        pygame.draw.rect(self.screen, 'white', [WIDTH//2 + 10, HEIGHT*3//4 - 25, 140, 50], 3, 10)
        char_font = pygame.font.Font(FONT_PATH, 20)  # Smaller font size
        char_text = char_font.render("CHARACTER", True, 'white')
        char_rect = char_text.get_rect(center=self.character_button.center)
        self.screen.blit(char_text, char_rect)

        # High score display
        if self.state.high_score > 0:
            high_score_text = self.font.render(f"High Score: {int(self.state.high_score)}", True, 'yellow')
            high_score_rect = high_score_text.get_rect(center=(WIDTH//2, HEIGHT - 50))
            self.screen.blit(high_score_text, high_score_rect)

    def _draw_character_select_screen(self):
        self.screen.fill(self.bg_color)

        # Title
        title_text = self.title_font.render("CHOOSE CHARACTER", True, 'white')
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(title_text, title_rect)

        # Character selection buttons
        characters = ["boy", "girl", "raccoon"]
        button_width = 120
        button_height = 160
        spacing = 20
        total_width = (button_width * len(characters)) + (spacing * (len(characters) - 1))
        start_x = (WIDTH - total_width) // 2

        for i, char_type in enumerate(characters):
            x = start_x + (button_width + spacing) * i
            y = HEIGHT//2 - button_height//2

            # Draw character button
            button_color = 'green' if char_type == self.selected_character else 'blue'
            self.character_buttons[char_type] = pygame.draw.rect(
                self.screen, button_color,
                [x, y, button_width, button_height], 0, 10
            )
            pygame.draw.rect(
                self.screen, 'white',
                [x, y, button_width, button_height], 3, 10
            )

            # Draw character name
            char_text = self.small_font.render(char_type.upper(), True, 'white')
            char_rect = char_text.get_rect(center=(x + button_width//2, y + button_height - 20))
            self.screen.blit(char_text, char_rect)

            # Draw character preview
            try:
                preview = pygame.transform.scale(
                    pygame.image.load(f"assets/{char_type}/run/1.PNG").convert_alpha(),
                    (button_width - 20, button_height - 40)
                )
                preview_rect = preview.get_rect(center=(x + button_width//2, y + button_height//2 - 10))
                self.screen.blit(preview, preview_rect)
            except:
                pass  # Skip preview if image not found

        # Buttons
        button_y = HEIGHT*3//4
        button_spacing = 20
        button_width = 120

        # Start button
        self.start_button = pygame.draw.rect(self.screen, 'green',
            [WIDTH//2 - button_width - button_spacing//2, button_y, button_width, 50], 0, 10)
        pygame.draw.rect(self.screen, 'white',
            [WIDTH//2 - button_width - button_spacing//2, button_y, button_width, 50], 3, 10)
        start_text = self.font.render("START", True, 'white')
        start_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, start_rect)

        # Back button
        self.back_button = pygame.draw.rect(self.screen, 'red',
            [WIDTH//2 + button_spacing//2, button_y, button_width, 50], 0, 10)
        pygame.draw.rect(self.screen, 'white',
            [WIDTH//2 + button_spacing//2, button_y, button_width, 50], 3, 10)
        back_text = self.font.render("BACK", True, 'white')
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)

        # Instructions
        instruction_text = self.font.render("Click a character to select, SPACE to start, ESC to go back", True, 'gray')
        instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT - 50))
        self.screen.blit(instruction_text, instruction_rect)

    def _draw_game_over_screen(self):
        self.screen.fill((50, 50, 50))  # Dark background

        # Game Over title
        game_over_text = self.title_font.render("GAME OVER", True, 'red')
        game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(game_over_text, game_over_rect)

        # Score information
        score_info = [
            f"Distance: {int(self.state.distance)}",
            f"Coins Collected: {self.state.coin_count}",
            f"High Score: {int(self.state.high_score)}"
        ]

        for i, info in enumerate(score_info):
            color = 'yellow' if 'High Score' in info else 'white'
            text = self.font.render(info, True, color)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20 + i * 40))
            self.screen.blit(text, text_rect)

        # Buttons
        button_y = HEIGHT*2//3
        button_font = pygame.font.Font(None, 24)

        # Restart button
        self.restart_button = pygame.draw.rect(self.screen, 'green', [WIDTH//2 - 150, button_y, 140, 50], 0, 10)
        pygame.draw.rect(self.screen, 'white', [WIDTH//2 - 150, button_y, 140, 50], 3, 10)
        restart_text = button_font.render("RESTART", True, 'white')
        restart_rect = restart_text.get_rect(center=self.restart_button.center)
        self.screen.blit(restart_text, restart_rect)

        # Menu button
        self.quit_button = pygame.draw.rect(self.screen, 'red', [WIDTH//2 + 10, button_y, 140, 50], 0, 10)
        pygame.draw.rect(self.screen, 'white', [WIDTH//2 + 10, button_y, 140, 50], 3, 10)
        menu_text = button_font.render("MENU", True, 'white')
        menu_rect = menu_text.get_rect(center=self.quit_button.center)
        self.screen.blit(menu_text, menu_rect)

        # Instructions
        instruction_text = self.font.render("Press SPACE to restart or ESC for menu", True, 'gray')
        instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT - 50))
        self.screen.blit(instruction_text, instruction_rect)

    def _draw_game_screen(self):
        # === Draw Background ===
        self.background_system.draw_background(self.screen, self.state.paused, self.difficulty_system.game_speed)

        # === Draw Game ===
        self.lines, self.top_plat, self.bot_plat, self.laser.points, self.laser_rect = draw_screen(
            screen=self.screen,
            surface=self.surface,
            font=self.font,
            bg_color=self.bg_color,
            lines=self.lines,
            laser_obj=self.laser,
            distance=self.state.distance,
            high_score=self.state.high_score,
            pause=self.state.paused,
            game_speed=self.difficulty_system.game_speed
        )

        # === Update ===
        if not self.state.paused:
            self._update_game_logic()

        self._draw_entities()

        # --- AI Mode HUD box ---
        mode_label = 'AI MODE: ON' if self.player.controlled_by_ai else 'AI MODE: OFF'
        color = 'green' if self.player.controlled_by_ai else 'gray'
        mode_text = self.font.render(mode_label, True, 'white')
        text_rect = mode_text.get_rect()
        box_width = text_rect.width + 20
        box_height = text_rect.height + 10

        box_x = WIDTH - box_width - 20
        box_y = HEIGHT - box_height - 20

        pygame.draw.rect(self.screen, color, (box_x, box_y, box_width, box_height), border_radius=8)
        pygame.draw.rect(self.screen, 'white', (box_x, box_y, box_width, box_height), width=2, border_radius=8)

        self.screen.blit(mode_text, (box_x + 10, box_y + 5))

        if self.state.paused:
            self.restart_button, self.quit_button = self._draw_pause_menu()

    def _start_new_game(self):
        self.game_state = GameStates.PLAYING
        self.state.reset()
        self.player.reset()
        self.rocket.reset()
        self.laser.reset()
        self.coins = []
        self.meteor_system.clear_meteors()

        # Reset systems
        self.difficulty_system.reset()
        self.background_system.reset()
        self.background_system.update_by_distance(0)

    def _update_game_logic(self):
        if not self.state.paused:
            # Update difficulty
            if self.difficulty_system.update(self.state.distance):
                # Update the background if the difficulty level changes
                self.background_system.update_by_distance(self.state.distance)

            # Update game speed based on difficulty
            game_speed = self.difficulty_system.game_speed

            # Update background
            self.background_system.update(pause=False, distance=self.state.distance, game_speed=game_speed)

            # Update other game elements with the new speed
            self.state.distance += game_speed

            # Animation + Distance
            self.player.update_animation()

            # meteor updates
            self._update_meteors()

        # === AI Decision ===
        if self.player.controlled_by_ai:
            game_obs = {
                "player_y": self.player.y,
                "player": self.player,
                "laser": self.laser.get_hitbox(),
                "rocket": self.rocket.get_hitbox(),
                "coins": [coin.rect for coin in self.coins],
            }
            # action = self.agent.decide(game_obs)
            # print(f"AI action: {action}")

            self.player.booster = False
            if False:
                self.player.booster_duration = self.player.max_booster_duration

        # Coin spawning
        if self.state.distance - self.last_coin_spawn > self.coin_spawn_distance:
            spawn_coins(self.coins)
            self.last_coin_spawn = self.state.distance

        update_coins(self.coins, self.state, self.player.get_hitbox(), self.state.paused, self.difficulty_system.game_speed)

        # Rocket
        if not self.rocket.active:
            self.rocket.counter += 1
            if self.rocket.counter > 180:
                self.rocket.activate()

        self.rocket.update(self.player.y, self.state.paused, self.difficulty_system.game_speed)

        # Laser
        self.laser.update(self.difficulty_system.game_speed)
        if self.laser.is_offscreen():
            self.laser = Laser()

        # Physics
        apply_gravity(self.player)
        self.top_hit, self.bot_hit = check_platform_collisions(self.player.get_hitbox(), self.top_plat, self.bot_plat)
        update_vertical_position(self.player, self.top_hit, self.bot_hit)

        # Update player position (including horizontal movement)
        self.player.update_position(self.top_hit, self.bot_hit)

        # Collision
        rocket_rect = self.rocket.get_hitbox()
        if rocket_rect and rocket_rect.colliderect(self.player.get_hitbox()):
            self._trigger_game_over()

        laser_box = self.laser.get_hitbox()
        if laser_box and laser_box.colliderect(self.player.get_hitbox()):
            self._trigger_game_over()

        # Meteor Collision Checks
        self._check_meteor_collisions()

        # Background color variation
        if self.state.distance % 500 == 0:
            self.bg_color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

        # Projectile logic
        for projectile in self.state.projectiles[:]:
            projectile.update()
            if not projectile.active:
                self.state.projectiles.remove(projectile)
            else:
                # Check if rocket is active and has a valid hitbox before collision detection
                rocket_hitbox = self.rocket.get_hitbox()
                if self.rocket.active and rocket_hitbox is not None and projectile.collides_with(self.rocket):
                    self.rocket.active = False
                    projectile.active = False
                    self.state.projectiles.remove(projectile)

    def _trigger_game_over(self):
        self.state.save_player_data()
        self.game_state = GameStates.GAME_OVER
        self.background_system.reset()

    def _draw_entities(self):
        draw_coins(self.coins, self.screen)
        draw_coin_counter(self.screen, self.font, self.state.coin_count)
        self.player.draw(self.screen, self.state.paused)
        self.rocket.draw(self.screen, self.font)
        for projectile in self.state.projectiles:
            projectile.draw(self.screen)
        self.meteor_system.draw_meteors(self.screen)

    def _draw_pause_menu(self):
        pygame.draw.rect(self.surface, (128, 128, 128, 150), [0, 0, WIDTH, HEIGHT])
        pygame.draw.rect(self.surface, 'dark gray', [200, 150, 600, 50], 0, 10)
        self.surface.blit(self.font.render('Game Paused. Press ESC to Resume', True, 'black'), (220, 160))
        restart_btn = pygame.draw.rect(self.surface, 'white', [200, 220, 280, 50], 0, 10)
        self.surface.blit(self.font.render('Restart', True, 'black'), (220, 230))
        quit_btn = pygame.draw.rect(self.surface, 'white', [520, 220, 280, 50], 0, 10)
        self.surface.blit(self.font.render('Quit', True, 'black'), (540, 230))
        pygame.draw.rect(self.surface, 'dark gray', [200, 300, 600, 50], 0, 10)
        self.surface.blit(self.font.render(f'Lifetime Distance: {int(self.state.lifetime_distance)}', True, 'black'), (220, 310))
        self.screen.blit(self.surface, (0, 0))
        return restart_btn, quit_btn

    def _restart_game(self):
        self.state.reset_run()
        self.player.reset()
        self.rocket.reset()
        self.laser = Laser()
        self.coins.clear()
        self.last_coin_spawn = 0
        self.bg_color = BG_COLOR

    def _get_speed(self):
        """Retrieve current game speed (retained for compatibility with other possible calls)"""
        return self.difficulty_system.game_speed

    def _update_meteors(self):
        """Update meteor system"""
        if not self.state.paused:
            self.meteor_system.update_difficulty(self.state.distance)
            self.meteor_system.spawn_meteor()
            self.meteor_system.update_meteors(self.state.paused, self.difficulty_system.game_speed)

    def _check_meteor_collisions(self):
        """Check meteor collisions with player"""
        colliding_meteor = self.meteor_system.check_collisions(self.player.get_hitbox())

        if colliding_meteor:
            self._trigger_game_over()
            return True
        return False
