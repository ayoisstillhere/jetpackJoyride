import argparse
from core.game import Game

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Jetpack Runner")
    parser.add_argument("--no-render", action="store_true", help="Disables graphic rendering (ai training mode)")

    args = parser.parse_args()

    game = Game(render=not args.no_render)
    game.run()