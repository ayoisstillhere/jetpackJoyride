import pygame

def handle_events(state, player, restart_button=None, quit_button=None, events=None):
    """
    Process Pygame events and update game state accordingly.

    Returns:
        should_quit (bool): True if the game window was closed or quit was requested.
    """
    if events is None:
        events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            state.save_player_data()
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                state.paused = not state.paused

            if event.key == pygame.K_t:
                player.controlled_by_ai = not getattr(player, 'controlled_by_ai', False)
                print(f"[HUD] AI mode {'ON' if player.controlled_by_ai else 'OFF'}")

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state.paused:
                if restart_button and restart_button.collidepoint(event.pos):
                    state.restart_requested = True
                if quit_button and quit_button.collidepoint(event.pos):
                    state.save_player_data()
                    return True

            elif not state.paused and not getattr(player, 'controlled_by_ai', False) and event.button == 1:
                projectile = player.shoot()
                if projectile:
                    state.projectiles.append(projectile)

    # continuous state
    keys = pygame.key.get_pressed()
    if not state.paused and not getattr(player, 'controlled_by_ai', False):
        if keys[pygame.K_w]:
            player.booster_power = 1.0
        else:
            player.booster_power = 0.0

        if keys[pygame.K_a]:
            player.move_speed = -1.0
        elif keys[pygame.K_d]:
            player.move_speed = 1.0
        else:
            player.move_speed = 0.0

    return False
