def apply_linear_movement(player):
    """
    Apply linear movement based on player state, no gravity.
    """
    if player.controlled_by_ai:
        if player.booster_duration > 0:
            player.booster = True
            player.booster_duration -= 1
        else:
            player.booster = False
    # No additional physics calculations needed in linear movement mode
    # All movement is handled directly in update_position


def update_vertical_position(player, colliding_top: bool, colliding_bottom: bool):
    """
    Update player's vertical position - now handled in player.update_position()
    This function is kept for compatibility but does nothing in linear movement mode.
    """
    # In linear movement mode, position updates are already completed in player.update_position()
    pass


def check_platform_collisions(player_rect, top_platform, bottom_platform):
    """
    Check if the player is touching the top or bottom platforms.
    Returns (top_collision: bool, bottom_collision: bool)
    """
    top_hit = player_rect.colliderect(top_platform)
    bottom_hit = player_rect.colliderect(bottom_platform)
    return top_hit, bottom_hit
