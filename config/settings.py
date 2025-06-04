# screen
WIDTH = 1000
HEIGHT = 600
FPS = 60
FONT_PATH = 'freesansbold.ttf'

# player
PLAYER_INIT_Y = HEIGHT - 130

# background
BG_COLOR = (128, 128, 128)

# coin
COIN_SPAWN_DISTANCE = 400
COIN_X_MIN = 100
COIN_X_MAX = 160
COIN_ABOVE_PLAYER = True   # jump only if coin is above

# laser logic
LASER_Y_TOLERANCE = 20  # vertical buffer to jump over laser

# rocket
ROCKET_X_THRESHOLD = 250  # how close (in X) the rocket must be to trigger reaction
ROCKET_TARGET_X = 120      # expected rocket target position (near player)
ROCKET_Y_TOLERANCE = 40    # vertical range for evasion