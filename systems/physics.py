def apply_gravity(player):
    """
    Apply gravity or upward thrust based on player state.
    自动修复飞行速度，booster时只在刚按下时给一个向上加速度。
    """
    if player.controlled_by_ai:
        if player.booster_duration > 0:
            player.booster = True
            player.booster_duration -= 1
        else:
            player.booster = False
    # 记录上一次booster状态
    if not hasattr(player, 'last_booster'):
        player.last_booster = False
    if player.booster:
        # 持续向上推力
        player.velocity_y -= 0.8
    else:
        player.velocity_y += 0.25  # gravity加大
    player.last_booster = player.booster

def update_vertical_position(player, colliding_top: bool, colliding_bottom: bool):
    """
    Update player's vertical position based on current velocity and collision state.
    自动修复碰撞：防止穿地/穿顶。
    """
    from config.settings import HEIGHT
    ground_height = 50
    # 先更新y
    player.y += player.velocity_y
    # 自动修复碰撞
    if player.y < ground_height:
        player.y = ground_height
        player.velocity_y = 0
    elif player.y > HEIGHT - ground_height - player.height:
        player.y = HEIGHT - ground_height - player.height
        player.velocity_y = 0
    # 处理平台碰撞
    if (colliding_bottom and player.velocity_y > 0) or (colliding_top and player.velocity_y < 0):
        player.velocity_y = 0


def check_platform_collisions(player_rect, top_platform, bottom_platform):
    """
    Check if the player is touching the top or bottom platforms.
    Returns (top_collision: bool, bottom_collision: bool)
    """
    top_hit = player_rect.colliderect(top_platform)
    bottom_hit = player_rect.colliderect(bottom_platform)
    return top_hit, bottom_hit
