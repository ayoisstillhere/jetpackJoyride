import pygame
import random

from config.settings import WIDTH, HEIGHT, FPS, BG_COLOR, FONT_PATH
from core.state import GameState
from core.events import handle_events
from systems.ui import draw_screen
from systems.physics import apply_gravity, update_vertical_position, check_platform_collisions
from entities.player import Player
from entities.rocket import Rocket
from entities.laser import Laser
from entities.coin import Coin, spawn_coins, update_coins, draw_coins, draw_coin_counter

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.display.set_caption("AI Jetpack Runner")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_PATH, 32)

        # Core state
        self.state = GameState()

        # Game elements
        self.player = Player()
        self.rocket = Rocket()
        self.laser = Laser()
        self.lines = [0, WIDTH/4, WIDTH/2, 3*WIDTH/4]
        self.bg_color = BG_COLOR

        # Coin system
        self.coins = []
        self.last_coin_spawn = 0
        self.coin_spawn_distance = 400

        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            # === Events ===
            quit_requested = handle_events(self.state, self.player, self.restart_button if self.state.paused else None, self.quit_button if self.state.paused else None)
            if quit_requested:
                self.running = False
                break

            # === Draw ===
            self.lines, self.top_plat, self.bot_plat, self.laser.points, self.laser_rect = draw_screen(
                screen=self.screen,
                surface=self.surface,
                font=self.font,
                bg_color=self.bg_color,
                lines=self.lines,
                laser=self.laser.points,
                distance=self.state.distance,
                high_score=self.state.high_score,
                pause=self.state.paused,
                game_speed=self._get_speed()
            )

            # === Update ===
            if not self.state.paused:
                self._update_game_logic()

            self._draw_entities()

            if self.state.paused:
                self.restart_button, self.quit_button = self._draw_pause_menu()

            pygame.display.flip()

        pygame.quit()

    def _update_game_logic(self):
        # Animation + Distance
        self.player.update_animation()
        self.state.distance += self._get_speed()

        # Coin spawning
        if self.state.distance - self.last_coin_spawn > self.coin_spawn_distance:
            spawn_coins(self.coins)
            self.last_coin_spawn = self.state.distance

        update_coins(self.coins, self.state, self.player.get_hitbox(), self.state.paused, self._get_speed())

        # Rocket
        if not self.rocket.active:
            self.rocket.counter += 1
            if self.rocket.counter > 180:
                self.rocket.activate()

        self.rocket.update(self.player.y, self.state.paused, self._get_speed())

        # Laser
        self.laser.update(self._get_speed())
        if self.laser.is_offscreen():
            self.laser = Laser()

        # Physics
        apply_gravity(self.player, self.player.booster)
        self.top_hit, self.bot_hit = check_platform_collisions(self.player.get_hitbox(), self.top_plat, self.bot_plat)
        update_vertical_position(self.player, self.top_hit, self.bot_hit)

        # Collision
        rocket_rect = self.rocket.get_hitbox()
        if rocket_rect and rocket_rect.colliderect(self.player.get_hitbox()):
            self.state.restart_requested = True

        if self.laser_rect.colliderect(self.player.get_hitbox()):
            self.state.restart_requested = True

        if self.state.restart_requested:
            self._restart_game()

        # Background color variation
        if self.state.distance % 500 == 0:
            self.bg_color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

    def _draw_entities(self):
        draw_coins(self.coins, self.screen)
        draw_coin_counter(self.screen, self.font, self.state.coin_count)
        self.player.draw(self.screen)
        self.rocket.draw(self.screen, self.font)

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
        self.state.save_player_data()
        self.state.reset_run()
        self.player.reset()
        self.rocket.reset()
        self.laser = Laser()
        self.coins.clear()
        self.last_coin_spawn = 0
        self.bg_color = BG_COLOR

    def _get_speed(self):
        if self.state.distance < 50000:
            return 1 + (self.state.distance // 500) / 10
        return 11