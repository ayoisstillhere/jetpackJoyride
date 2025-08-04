import pygame
import sys
from core.background_system import BackgroundSystem

# Initialize Pygame
pygame.init()

# Set window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Background System Test")

# Create background system
bg_system = BackgroundSystem(WINDOW_WIDTH, WINDOW_HEIGHT)

# Create clock object
clock = pygame.time.Clock()

# Game variables
distance = 0  # Current distance (meters)
speed = 100  # Speed (meters per second)

# Function to display current information
def draw_info():
    font = pygame.font.Font(None, 36)
    theme_text = font.render(f"Theme: {bg_system.current_theme}", True, (255, 255, 255))
    type_text = font.render(f"Background Type: {bg_system.current_background_type}", True, (255, 255, 255))
    distance_text = font.render(f"Distance: {distance:.0f}m", True, (255, 255, 255))
    help_text = font.render("Keys: Space-pause ESC-exit", True, (255, 255, 255))

    screen.blit(theme_text, (10, 10))
    screen.blit(type_text, (10, 50))
    screen.blit(distance_text, (10, 90))
    screen.blit(help_text, (10, WINDOW_HEIGHT - 40))

# Main game loop
running = True
paused = False
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused

    # Update game state
    if not paused:
        # Update distance
        distance += speed * (1/60)  # Assume 60FPS

    # Update background
    bg_system.update(pause=paused, distance=distance)

    # Draw background
    bg_system.draw_background(screen, pause=paused)

    # Display information
    draw_info()

    # Update display
    pygame.display.flip()

    # Control frame rate
    clock.tick(60)

# Exit game
pygame.quit()
sys.exit()
