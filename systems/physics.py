def apply_gravity(player):
    """
    Apply gravity or upward thrust based on player state.
    """
    if player.controlled_by_ai:
        if player.booster_duration > 0:
            player.booster = True
            player.booster_duration -= 1
        else:
            player.booster = False

    if player.booster:
        player.velocity_y -= player.gravity
    else:
        player.velocity_y += player.gravity
    # print(f"[PHYSICS] y_velocity: {player.velocity_y}")


def update_vertical_position(player, colliding_top: bool, colliding_bottom: bool):
    """
    Update player's vertical position based on current velocity and collision state.
    """
    if (colliding_bottom and player.velocity_y > 0) or (colliding_top and player.velocity_y < 0):
        player.velocity_y = 0
    player.y += player.velocity_y


def check_platform_collisions(player_rect, top_platform, bottom_platform):
    """
    Check if the player is touching the top or bottom platforms.
    Returns (top_collision: bool, bottom_collision: bool)
    """
    top_hit = player_rect.colliderect(top_platform)
    bottom_hit = player_rect.colliderect(bottom_platform)
    return top_hit, bottom_hit
