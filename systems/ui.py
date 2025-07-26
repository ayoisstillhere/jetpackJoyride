import pygame
from config.settings import WIDTH, HEIGHT

# add global variable to track ground position
ground_offset = 0

def draw_screen(screen, surface, font, bg_color, lines, laser_obj, distance, high_score, pause, game_speed):
    global ground_offset
    
    # no fill black background, because background system has already drawn the background
    pygame.draw.rect(surface, (*bg_color, 50), [0, 0, WIDTH, HEIGHT])
    screen.blit(surface, (0, 0))

    # Load and scale ground image
    try:
        ground_img = pygame.image.load("assets/ground.png").convert_alpha()
        ground_height = 50  # Keep the same height as before
        ground_img = pygame.transform.scale(ground_img, (ground_img.get_width(), ground_height))
        
        # Calculate how many times we need to tile the image
        ground_width = ground_img.get_width()
        num_tiles = WIDTH // ground_width + 2  # +2 to ensure full coverage during scrolling
        
        # Update ground offset if not paused
        if not pause:
            ground_offset -= game_speed
            if ground_offset <= -ground_width:
                ground_offset = 0
        
        # Draw top and bottom ground
        for i in range(num_tiles):
            # Calculate position with offset
            x_pos = i * ground_width + ground_offset
            # Top ground
            screen.blit(ground_img, (x_pos, 0))
            # Bottom ground
            screen.blit(ground_img, (x_pos, HEIGHT - ground_height))
    except:
        # Fallback to original gray rectangles if image loading fails
        top = pygame.draw.rect(screen, 'gray', [0, 0, WIDTH, 50])
        bot = pygame.draw.rect(screen, 'gray', [0, HEIGHT - 50, WIDTH, 50])

    # platform
    for i in range(len(lines)):
        pygame.draw.line(screen, 'black', (lines[i], 0), (lines[i], 50), 3)
        pygame.draw.line(screen, 'black', (lines[i], HEIGHT - 50), (lines[i], HEIGHT), 3)

        if not pause:
            lines[i] -= game_speed

        if lines[i] < 0:
            lines[i] = WIDTH

    # Draw laser using the Laser class method
    laser_rect = laser_obj.draw(screen)

    # print score
    screen.blit(font.render(f'Distance: {int(distance)} m', True, 'white'), (10, 10))
    screen.blit(font.render(f'High Score: {int(high_score)} m', True, 'white'), (10, 70))

    return lines, pygame.Rect(0, 0, WIDTH, 50), pygame.Rect(0, HEIGHT - 50, WIDTH, 50), laser_obj.points, laser_rect