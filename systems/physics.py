def check_platform_collisions(player_rect, top_platform, bottom_platform):
    """
    Check if the player is touching the top or bottom platforms.
    Returns (top_collision: bool, bottom_collision: bool)
    """
    top_hit = player_rect.colliderect(top_platform)
    bottom_hit = player_rect.colliderect(bottom_platform)
    return top_hit, bottom_hit
