from config import settings
from ai.agent_base import BaseAgent

class RuleBasedAgent(BaseAgent):
    def decide(self, game_state):
        player_y = game_state["player_y"]
        laser = game_state.get("laser")
        rocket = game_state.get("rocket")
        coins = game_state.get("coins", [])

        print(f"[AI] player_y: {player_y}")

        # === Laser detection ===
        if laser:
            print(f"[AI] laser.top: {laser.top}, laser.bottom: {laser.bottom}")
            if player_y > laser.top - settings.LASER_Y_TOLERANCE and player_y < laser.bottom + settings.LASER_Y_TOLERANCE:
                print("[AI] Decision: JUMP due to LASER")
                return "jump"

        # === Rocket detection ===
        if rocket:
            print(f"[AI] rocket.centerx: {rocket.centerx}, rocket.centery: {rocket.centery}")
            if abs(rocket.centerx - settings.ROCKET_TARGET_X) < settings.ROCKET_X_THRESHOLD:
                if abs(rocket.centery - player_y) < settings.ROCKET_Y_TOLERANCE:
                    print("[AI] Decision: JUMP due to ROCKET")
                    return "jump"

        # === Coin detection ===
        for coin in coins:
            print(f"[AI] coin.x: {coin.x}, coin.y: {coin.y}")
            if settings.COIN_X_MIN < coin.x < settings.COIN_X_MAX:
                if not settings.COIN_ABOVE_PLAYER or coin.y < player_y:
                    print("[AI] Decision: JUMP to COLLECT COIN")
                    return "jump"

        print("[AI] Decision: WAIT (no threats detected)")
        return "wait"