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

            if event.key == pygame.K_SPACE and not state.paused and not getattr(player, 'controlled_by_ai', False):
                player.booster = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and not getattr(player, 'controlled_by_ai', False):
                player.booster = False

        if event.type == pygame.MOUSEBUTTONDOWN and state.paused:
            if restart_button and restart_button.collidepoint(event.pos):
                state.restart_requested = True
            if quit_button and quit_button.collidepoint(event.pos):
                state.save_player_data()
                return True

    return False