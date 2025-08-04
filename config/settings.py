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

# reward constants
COIN_REWARD = 15.0
COIN_SHAPING_SCALE = 1.5         # shaping factor for moving closer to coins
PENALTY_NO_COIN = 1.0            # penalty when no coins are collected for too long

ROCKET_DESTROY_REWARD = 10.0
ROCKET_SHAPING_SCALE = 0.15      # shaping reward for moving towards the rocket when shooting
ROCKET_DANGER_RADIUS = 0.25 * WIDTH  # distance threshold for rocket danger zone
ROCKET_DANGER_PENALTY = 2.0      # penalty when too close to a rocket
PENALTY_BAD_SHOT = 0.5           # penalty when shooting but failing to destroy the rocket

LASER_DANGER_RADIUS = 0.25 * WIDTH  # distance threshold for laser danger zone
LASER_DANGER_PENALTY = 2.0       # penalty when too close to a laser

METEOR_DANGER_RADIUS = 0.25 * WIDTH  # distance threshold for meteor danger zone
METEOR_DANGER_PENALTY = 2.0      # penalty when too close to a meteor

PENALTY_DEATH = 10.0
REWARD_STAY_IN_MIDDLE = 0.05     # small reward for staying near the middle of the screen
X_RATIO_THRESHOLD = 0.8          # horizontal ratio after which the player is considered "too far right"
PENALTY_X_RATIO = 5.0            # penalty scaling for staying too far on the right side